import hmac
import six
from encoding import force_bytes
import random
import hashlib
import time
import struct
import binascii
import importlib
import base64
from collections import OrderedDict

SECRET_KEY="oq=0t2k++snm(nh(5&xk3vuf7(hg9#%@&mvyx22e@q%-0nvm6t"

try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    import warnings
    warnings.warn('A secure pseudo-random number generator is not available '
                  'on your system. Falling back to Mersenne Twister.')
    using_sysrandom = False

if hasattr(hmac, "compare_digest"):
    # Prefer the stdlib implementation, when available.
    def constant_time_compare(val1, val2):
        return hmac.compare_digest(force_bytes(val1), force_bytes(val2))
else:
    def constant_time_compare(val1, val2):
        """
        Returns True if the two strings are equal, False otherwise.
        The time taken is independent of the number of characters that match.
        For the sake of simplicity, this function executes in constant time only
        when the two strings have the same length. It short-circuits when they
        have different lengths. Since Django only uses it to compare hashes of
        known expected length, this is acceptable.
        """
        if len(val1) != len(val2):
            return False
        result = 0
        if six.PY3 and isinstance(val1, bytes) and isinstance(val2, bytes):
            for x, y in zip(val1, val2):
                result |= x ^ y
        else:
            for x, y in zip(val1, val2):
                result |= ord(x) ^ ord(y)
        return result == 0

def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Returns a securely generated random string.
    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    if not using_sysrandom:
        # This is ugly, and a hack, but it makes things better than
        # the alternative of predictability. This re-seeds the PRNG
        # using a value that is hard for an attacker to predict, every
        # time a random string is required. This may change the
        # properties of the chosen random sequence slightly, but this
        # is better than absolute predictability.
        random.seed(
            hashlib.sha256(
                ("%s%s%s" % (
                    random.getstate(),
                    time.time(),
                    SECRET_KEY)).encode('utf-8')
            ).digest())
    return ''.join(random.choice(allowed_chars) for i in range(length))

def _bin_to_long(x):
    """
    Convert a binary string into a long integer
    This is a clever optimization for fast xor vector math
    """
    return int(binascii.hexlify(x), 16)

def _long_to_bin(x, hex_format_string):
    """
    Convert a long integer into a binary string.
    hex_format_string is like "%020x" for padding 10 characters.
    """
    return binascii.unhexlify((hex_format_string % x).encode('ascii'))

if hasattr(hashlib, "pbkdf2_hmac"):
    def pbkdf2(password, salt, iterations, dklen=0, digest=None):
        """
        Implements PBKDF2 with the same API as Django's existing
        implementation, using the stdlib.
        This is used in Python 2.7.8+ and 3.4+.
        """
        if digest is None:
            digest = hashlib.sha256
        if not dklen:
            dklen = None
        password = force_bytes(password)
        salt = force_bytes(salt)
        return hashlib.pbkdf2_hmac(
            digest().name, password, salt, iterations, dklen)
else:
    def pbkdf2(password, salt, iterations, dklen=0, digest=None):
        """
        Implements PBKDF2 as defined in RFC 2898, section 5.2
        HMAC+SHA256 is used as the default pseudo random function.
        As of 2014, 100,000 iterations was the recommended default which took
        100ms on a 2.7Ghz Intel i7 with an optimized implementation. This is
        probably the bare minimum for security given 1000 iterations was
        recommended in 2001. This code is very well optimized for CPython and
        is about five times slower than OpenSSL's implementation. Look in
        django.contrib.auth.hashers for the present default, it is lower than
        the recommended 100,000 because of the performance difference between
        this and an optimized implementation.
        """
        assert iterations > 0
        if not digest:
            digest = hashlib.sha256
        password = force_bytes(password)
        salt = force_bytes(salt)
        hlen = digest().digest_size
        if not dklen:
            dklen = hlen
        if dklen > (2 ** 32 - 1) * hlen:
            raise OverflowError('dklen too big')
        l = -(-dklen // hlen)
        r = dklen - (l - 1) * hlen

        hex_format_string = "%%0%ix" % (hlen * 2)

        inner, outer = digest(), digest()
        if len(password) > inner.block_size:
            password = digest(password).digest()
        password += b'\x00' * (inner.block_size - len(password))
        inner.update(password.translate(hmac.trans_36))
        outer.update(password.translate(hmac.trans_5C))

        def F(i):
            u = salt + struct.pack(b'>I', i)
            result = 0
            for j in range(int(iterations)):
                dig1, dig2 = inner.copy(), outer.copy()
                dig1.update(u)
                dig2.update(dig1.digest())
                u = dig2.digest()
                result ^= _bin_to_long(u)
            return _long_to_bin(result, hex_format_string)

        T = [F(x) for x in range(1, l)]
        return b''.join(T) + F(l)[:r]

class BasePasswordHasher(object):
    """
    Abstract base class for password hashers
    When creating your own hasher, you need to override algorithm,
    verify(), encode() and safe_summary().
    PasswordHasher objects are immutable.
    """
    algorithm = None
    library = None

    def _load_library(self):
        if self.library is not None:
            if isinstance(self.library, (tuple, list)):
                name, mod_path = self.library
            else:
                mod_path = self.library
            try:
                module = importlib.import_module(mod_path)
            except ImportError as e:
                raise ValueError("Couldn't load %r algorithm library: %s" %
                                 (self.__class__.__name__, e))
            return module
        raise ValueError("Hasher %r doesn't specify a library attribute" %
                         self.__class__.__name__)

    def salt(self):
        """
        Generates a cryptographically secure nonce salt in ASCII
        """
        return get_random_string()

    def verify(self, password, encoded):
        """
        Checks if the given password is correct
        """
        raise NotImplementedError('subclasses of BasePasswordHasher must provide a verify() method')

    def encode(self, password, salt):
        """
        Creates an encoded database value
        The result is normally formatted as "algorithm$salt$hash" and
        must be fewer than 128 characters.
        """
        raise NotImplementedError('subclasses of BasePasswordHasher must provide an encode() method')

    def safe_summary(self, encoded):
        """
        Returns a summary of safe values
        The result is a dictionary and will be used where the password field
        must be displayed to construct a safe representation of the password.
        """
        raise NotImplementedError('subclasses of BasePasswordHasher must provide a safe_summary() method')

    def must_update(self, encoded):
        return False



def mask_hash(hash, show=6, char="*"):
    """
    Returns the given hash, with only the first ``show`` number shown. The
    rest are masked with ``char`` for security reasons.
    """
    masked = hash[:show]
    masked += char * len(hash[show:])
    return masked

def _(message): # XXX for translation
    return message

class PBKDF2PasswordHasher(BasePasswordHasher):
    """
    Secure password hashing using the PBKDF2 algorithm (recommended)
    Configured to use PBKDF2 + HMAC + SHA256.
    The result is a 64 byte binary string.  Iterations may be changed
    safely but you must rename the algorithm if you change SHA256.
    """
    algorithm = "pbkdf2_sha256"
    iterations = 24000
    digest = hashlib.sha256

    def encode(self, password, salt, iterations=None):
        assert password is not None
        assert salt and '$' not in salt
        if not iterations:
            iterations = self.iterations
        hash = pbkdf2(password, salt, iterations, digest=self.digest)
        hash = base64.b64encode(hash).decode('ascii').strip()
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def verify(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt, int(iterations))
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('iterations'), iterations),
            (_('salt'), mask_hash(salt)),
            (_('hash'), mask_hash(hash)),
        ])

    def must_update(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        return int(iterations) != self.iterations


UNUSABLE_PASSWORD_PREFIX = '!'  # This will never be a valid encoded hash
UNUSABLE_PASSWORD_SUFFIX_LENGTH = 40  # number of random chars to add after UNUSABLE_PASSWORD_PREFIX

hasher = PBKDF2PasswordHasher()

def check_password(password, encoded):
    """
    Returns a boolean of whether the raw password matches the three
    part encoded digest.
    If setter is specified, it'll be called when you need to
    regenerate the password.
    """
    if password is None or not is_password_usable(encoded):
        return False

    is_correct = hasher.verify(password, encoded)
    return is_correct


def make_password(password, salt=None):
    """
    Turn a plain-text password into a hash for database storage
    Same as encode() but generates a new random salt.
    If password is None then a concatenation of
    UNUSABLE_PASSWORD_PREFIX and a random string will be returned
    which disallows logins. Additional random string reduces chances
    of gaining access to staff or superuser accounts.
    See ticket #20079 for more info.
    """
    if password is None:
        return UNUSABLE_PASSWORD_PREFIX + get_random_string(UNUSABLE_PASSWORD_SUFFIX_LENGTH)

    if not salt:
        salt = hasher.salt()

    return hasher.encode(password, salt)


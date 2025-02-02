# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import codecs
import uuid

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateNumbers,
    RSAPublicNumbers,
    generate_private_key,
    rsa_crt_dmp1,
    rsa_crt_dmq1,
    rsa_crt_iqmp,
    RSAPrivateKey,
)

from azure.keyvault.keys.models import JsonWebKey
from ._internal import _bytes_to_int, _int_to_bytes
from .key import Key
from .algorithms import Ps256, Ps384, Ps512, Rsa1_5, RsaOaep, RsaOaep256, Rs256, Rs384, Rs512


class RsaKey(Key):  # pylint:disable=too-many-public-methods
    PUBLIC_KEY_DEFAULT_OPS = ["encrypt", "wrapKey", "verify"]
    PRIVATE_KEY_DEFAULT_OPS = ["encrypt", "decrypt", "wrapKey", "unwrapKey", "verify", "sign"]

    _supported_encryption_algorithms = [Rsa1_5.name(), RsaOaep.name(), RsaOaep256.name()]
    _supported_key_wrap_algorithms = [Rsa1_5.name(), RsaOaep.name(), RsaOaep256.name()]
    _supported_signature_algorithms = [
        Ps256.name(),
        Ps384.name(),
        Ps512.name(),
        Rs256.name(),
        Rs384.name(),
        Rs512.name(),
    ]

    def __init__(self, kid=None):
        super(RsaKey, self).__init__()
        self._kid = kid
        self.kty = None
        self.key_ops = None
        self._rsa_impl = None

    @property
    def n(self):
        return _int_to_bytes(self._public_key_material().n)

    @property
    def e(self):
        return _int_to_bytes(self._public_key_material().e)

    @property
    def p(self):
        return _int_to_bytes(self._public_key_material().p) if self.is_private_key() else None

    @property
    def q(self):
        return _int_to_bytes(self._private_key_material().q) if self.is_private_key() else None

    @property
    def b(self):
        return _int_to_bytes(self._private_key_material().b) if self.is_private_key() else None

    @property
    def d(self):
        return _int_to_bytes(self._private_key_material().d) if self.is_private_key() else None

    @property
    def dq(self):
        return _int_to_bytes(self._private_key_material().dmq1) if self.is_private_key() else None

    @property
    def dp(self):
        return _int_to_bytes(self._private_key_material().dmp1) if self.is_private_key() else None

    @property
    def qi(self):
        return _int_to_bytes(self._private_key_material().iqmp) if self.is_private_key() else None

    @property
    def private_key(self):
        return self._rsa_impl if self.is_private_key() else None

    @property
    def public_key(self):
        return self._rsa_impl.public_key() if self.is_private_key() else self._rsa_impl

    @staticmethod
    def generate(kid=None, kty="RSA", size=2048, e=65537):
        key = RsaKey()
        key.kid = kid or str(uuid.uuid4())
        key.kty = kty
        key.key_ops = RsaKey.PRIVATE_KEY_DEFAULT_OPS
        # pylint:disable=protected-access
        key._rsa_impl = generate_private_key(public_exponent=e, key_size=size, backend=default_backend())
        return key

    @classmethod
    def from_jwk(cls, jwk):
        if jwk.kty != "RSA" and jwk.kty != "RSA-HSM":
            raise ValueError('The specified jwk must have a key type of "RSA" or "RSA-HSM"')

        if not jwk.n or not jwk.e:
            raise ValueError("Invalid RSA jwk, both n and e must be have values")

        rsa_key = cls(kid=jwk.kid)
        rsa_key.kty = jwk.kty
        rsa_key.key_ops = jwk.key_ops

        pub = RSAPublicNumbers(n=_bytes_to_int(jwk.n), e=_bytes_to_int(jwk.e))

        # if the private key values are specified construct a private key
        # only the secret primes and private exponent are needed as other fields can be calculated
        if jwk.p and jwk.q and jwk.d:
            # convert the values of p, q, and d from bytes to int
            p = _bytes_to_int(jwk.p)
            q = _bytes_to_int(jwk.q)
            d = _bytes_to_int(jwk.d)

            # convert or compute the remaining private key numbers
            dmp1 = _bytes_to_int(jwk.dp) if jwk.dp else rsa_crt_dmp1(private_exponent=d, p=p)
            dmq1 = _bytes_to_int(jwk.dq) if jwk.dq else rsa_crt_dmq1(private_exponent=d, q=q)
            iqmp = _bytes_to_int(jwk.qi) if jwk.qi else rsa_crt_iqmp(p=p, q=q)

            # create the private key from the jwk key values
            priv = RSAPrivateNumbers(p=p, q=q, d=d, dmp1=dmp1, dmq1=dmq1, iqmp=iqmp, public_numbers=pub)
            key_impl = priv.private_key(default_backend())

        # if the necessary private key values are not specified create the public key
        else:
            key_impl = pub.public_key(default_backend())

        rsa_key._rsa_impl = key_impl  # pylint:disable=protected-access

        return rsa_key

    def to_jwk(self, include_private=False):
        jwk = JsonWebKey(
            kid=self.kid,
            kty=self.kty,
            key_ops=self.key_ops if include_private else RsaKey.PUBLIC_KEY_DEFAULT_OPS,
            n=self.n,
            e=self.e,
        )

        if include_private:
            jwk.q = self.q
            jwk.p = self.p
            jwk.d = self.d
            jwk.dq = self.dq
            jwk.dp = self.dp
            jwk.qi = self.qi

        return jwk

    @property
    def default_encryption_algorithm(self):
        return RsaOaep.name()

    @property
    def default_key_wrap_algorithm(self):
        return RsaOaep.name()

    @property
    def default_signature_algorithm(self):
        return Rs256.name()

    def encrypt(self, plain_text, **kwargs):
        algorithm = self._get_algorithm("encrypt", **kwargs)
        encryptor = algorithm.create_encryptor(self._rsa_impl)
        return encryptor.transform(plain_text)

    def decrypt(self, cipher_text, **kwargs):
        if not self.is_private_key():
            raise NotImplementedError("The current RsaKey does not support decrypt")

        algorithm = self._get_algorithm("decrypt", **kwargs)
        decryptor = algorithm.create_decryptor(self._rsa_impl)
        return decryptor.transform(cipher_text)

    def sign(self, digest, **kwargs):
        if not self.is_private_key():
            raise NotImplementedError("The current RsaKey does not support sign")

        algorithm = self._get_algorithm("sign", **kwargs)
        signer = algorithm.create_signature_transform(self._rsa_impl)
        return signer.sign(digest)

    def verify(self, digest, signature, **kwargs):
        algorithm = self._get_algorithm("verify", **kwargs)
        signer = algorithm.create_signature_transform(self._rsa_impl)
        try:
            # cryptography's verify methods return None, and raise when verification fails
            signer.verify(digest, signature)
            return True
        except InvalidSignature:
            return False

    def wrap_key(self, key, **kwargs):
        algorithm = self._get_algorithm("wrapKey", **kwargs)
        encryptor = algorithm.create_encryptor(self._rsa_impl)
        return encryptor.transform(key)

    def unwrap_key(self, encrypted_key, **kwargs):
        if not self.is_private_key():
            raise NotImplementedError("The current RsaKey does not support unwrap")

        algorithm = self._get_algorithm("unwrapKey", **kwargs)
        decryptor = algorithm.create_decryptor(self._rsa_impl)
        return decryptor.transform(encrypted_key)

    def is_private_key(self):
        return isinstance(self._rsa_impl, RSAPrivateKey)

    def _public_key_material(self):
        return self.public_key.public_numbers()

    def _private_key_material(self):
        return self.private_key.private_numbers() if self.private_key else None


def _bytes_to_int(b):
    return int(codecs.encode(b, "hex"), 16)


def _int_to_bytes(i):
    h = hex(i)
    if len(h) > 1 and h[0:2] == "0x":
        h = h[2:]

    # need to strip L in python 2.x
    h = h.strip("L")

    if len(h) % 2:
        h = "0" + h
    return codecs.decode(h, "hex")

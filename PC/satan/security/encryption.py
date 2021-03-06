from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Hash import SHA256

from satan.security.interfaces import EncryptionInterface, Key


class RSAEncryption(EncryptionInterface):
    def __init__(self, key: Key):
        """
        :param key: a key generated by RSAKeyManager
        """
        self.key = key

    def encrypt(self, message: bytes, **kwargs) -> bytes:
        cipher = PKCS1_OAEP.new(self.key, hashAlgo=SHA256)
        return cipher.encrypt(message)

    def decrypt(self, message: bytes, **kwargs) -> bytes:
        cipher = PKCS1_OAEP.new(self.key, hashAlgo=SHA256)
        return cipher.decrypt(message)


class AES256Encryption(EncryptionInterface):
    MODE_ECB = AES.MODE_ECB
    MODE_CBC = AES.MODE_CBC
    MODE_CFB = AES.MODE_CFB
    MODE_OFB = AES.MODE_OFB
    MODE_CTR = AES.MODE_CTR
    MODE_EAX = AES.MODE_EAX

    def __init__(self, key: Key, mode: int = MODE_ECB):
        """
        :param key: a key generated by AES256KeyManager
        :param mode: encryption mode to be used (use one of the class constants)
        """
        self.key = key
        self.mode = mode

    def encrypt(self, message: bytes, **kwargs) -> bytes:
        """
        Encrypt the message using AES-256. The message is padded
        using PKCS7.

        The IV will be in the first 16 bytes of the returned data;
        the remaining bytes will contain the ciphertext.

        If using EAX mode, the verification MAC will be appended to
        the data.

        :Keyword Arguments:

        *    **mode** (``int``) --
                mode of operation for encryption
                will change the default mode that may have been
                provided in the constructor
        *    **iv** (``byte string``) --
                initialization vector - should not be repeated - 16 bytes long
                if not provided but required, a random IV is
                generated.
        """

        mode = kwargs.get('mode')
        if mode is not None:
            self.mode = mode

        iv = kwargs.get('iv')

        if self.mode in (self.MODE_CBC, self.MODE_CFB, self.MODE_OFB):
            cipher = AES.new(self.key, self.mode, iv=iv)
            iv = cipher.iv
        elif self.mode in (self.MODE_CTR, self.MODE_EAX):
            cipher = AES.new(self.key, self.mode, nonce=iv)
            iv = cipher.nonce
        else:
            cipher = AES.new(self.key, self.mode)
            iv = b''

        if self.mode == self.MODE_EAX:
            enc, mac = cipher.encrypt_and_digest(message)
            ciphertext = enc + mac
        else:
            ciphertext = cipher.encrypt(pad(message, AES.block_size))

        return iv + ciphertext

    def decrypt(self, message: bytes, *args, **kwargs) -> bytes:
        """
        Decrypt a message using AES-256. Message is assumed
        to be padded using PKCS7.

        IV, if required but not provided, is assumed to be in the first 16 bytes of the message.

        If using EAX mode, the verification MAC is assumed to be
        appended to the data.

        :Keyword Arguments:

        *    *mode* (``int``) --
                mode of operation for encryption
                will change the default mode that may have been
                provided in the constructor
        *    *iv* (``byte string``) --
                initialization vector - should not be repeated - 16 bytes long
        """
        mode = kwargs.get('mode')
        if mode is not None:
            self.mode = mode

        iv = kwargs.get('iv')
        if iv is None and self.mode != self.MODE_ECB:
            iv = message[:16]
            message = message[16:]

        if self.mode in (self.MODE_CBC, self.MODE_CFB, self.MODE_OFB):
            cipher = AES.new(self.key, self.mode, iv=iv)
        elif self.mode in (self.MODE_CTR, self.MODE_EAX):
            cipher = AES.new(self.key, self.mode, nonce=iv)
        else:
            cipher = AES.new(self.key, self.mode)

        if self.mode == self.MODE_EAX:
            mac = message[-16:]
            message = message[:-16]
            plaintext = cipher.decrypt_and_verify(message, mac)
        else:
            plaintext = unpad(cipher.decrypt(message), AES.block_size)

        return plaintext

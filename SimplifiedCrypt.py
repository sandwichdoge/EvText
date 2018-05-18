import pysodium
import binascii


def binary_to_hex(binaryblob):
    ret = ''
    for i in range(len(binaryblob)):
        s = str(hex(ord(binaryblob[i])))[2:]  #remove 0x prefix
        s = ('0' + s)[-2:]  #hexcode = 2 characters, add '0' prefix to single characters
        ret += s
    return ret


def crypt_aed_encrypt(data, keystr):
    key = binascii.unhexlify(binary_to_hex(pysodium.crypto_hash_sha256(keystr)))
    nonce = binascii.unhexlify(b"cd7cf67be39c7977")
    ad = ""
    rtn = pysodium.crypto_aead_chacha20poly1305_encrypt(data, ad, nonce, key)
    return rtn


def crypt_aed_decrypt(data, keystr):
    key = binascii.unhexlify(binary_to_hex(pysodium.crypto_hash_sha256(keystr)))
    nonce = binascii.unhexlify(b"cd7cf67be39c7977")
    ad = ""
    rtn = pysodium.crypto_aead_chacha20poly1305_decrypt(data, ad, nonce, key)
    return rtn

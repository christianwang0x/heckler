import base64
import urllib.parse
import hashlib

# A lot of the code here is unnecessary because I copied it
# over from another project of mine.

# Error constants
BAD_LENGTH_MSG = "One of the parameters given does not have a correct length"

BAD_CHARS_MSG = "Invalid characters for this encoding scheme"

BAD_ENCODER_MSG = "Invalid encoder specified"


# Encoding scheme superclass that acts
#   as an interface to the scheme subclasses
class EncodingScheme:
    @staticmethod
    def encode(input_bytes):
        pass

#  Encodes base64 data
class Base64(EncodingScheme):
    @staticmethod
    def encode(input_str):
        input_bytes = bytes(input_str, 'utf-8')
        return base64.b64encode(input_bytes).decode('utf-8')


class MD5(EncodingScheme):
    @staticmethod
    def encode(input_str):
        input_bytes = bytes(input_str, 'utf-8')
        return hashlib.md5(input_bytes).hexdigest()


#  Encodes ASCII hexadecimal data
#  This data is represented by a series of hex
#    numbers, where each two numbers represent
#    one byte of data.
class AsciiHex(EncodingScheme):
    @staticmethod
    def encode(input_bytes):
        return ascii_hex_encode(input_bytes)


# Encodes from URL hexadecimal
#   format, where special characters are
#   encoded as a hex pair prefixed with a %
#   and spaces are replaced with +
class Url(EncodingScheme):
    @staticmethod
    def encode(input_bytes):
        return url_encode(input_bytes)


# Exception object for the encoder
class EncoderException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


# Encode to ASCII hex format
def ascii_hex_encode(input_str):
    input_bytes = bytes(input_str, 'utf-8')
    encoded = ""
    for b in input_bytes:
        byte = hex(int.from_bytes([b], 'big'))[2:]
        if len(byte) < 2:
            byte = '0' + byte
        encoded += byte
    return encoded


# Encode with URL encoding scheme
# Including space character
def url_encode(input_str):
    return urllib.parse.quote_plus(input_str)


# Encode a 2d table of bytes with the
#   appropriate encoder
def encode_list(l, encoder_obj):
    sequence = []
    for line in l:
        encoded = encoder_obj.encode(line)
        sequence.append(encoded)
    return sequence

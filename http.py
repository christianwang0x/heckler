import re
from base64 import b64encode
from constants import *


class RequestPacket:
    def __init__(self, packet_data):
        self.packet_data = packet_data
        self.method = self.get_method(packet_data)
        self.uri = self.get_uri(packet_data)
        self.version = self.get_version(packet_data)
        self.headers = self.get_headers(packet_data)
        self.data = self.get_data(packet_data)

    def get_method(self, packet_data):
        method = packet_data.strip().split()[0]
        return method

    def get_uri(self, packet_data):
        uri = packet_data.strip().split()[1]
        return uri

    def get_version(self, packet_data):
        version = packet_data.strip().split()[2]
        return version

    def get_headers(self, packet_data):
        headers = []
        for line in packet_data.split('\n')[1:]:
            line = line.strip()
            if not line:
                break
            key, value = line.split(":")
            value = value.lstrip()
            headers.append((key, value))
        return headers

    def get_data(self, packet_data):
        split_packet = packet_data.split('\n')
        while split_packet:
            line = split_packet[0]
            if not line.strip():
                break
            else:
                split_packet.pop(0)
        else:
            return ""
        data = '\n'.join(split_packet).rstrip()
        return data

    def format(self):
        top_line = ' '.join([self.method, self.uri, self.version])
        formatted = top_line + NL
        header_lines = []
        for key, value in self.headers:
            header = ': '.join((key, value))
            header_lines.append(header)
        formatted += NL.join(header_lines)
        formatted += NL * 2
        if self.data:
            self.data = self.data.rstrip()
            formatted += self.data + (NL * 2)
        return formatted


# An object representing a single HTTP request
# to the server, including the parameters
# and response.
class Request:
    def __init__(self, template, params):
        self.template = RequestPacket(template).format()
        self.params = params
        self.request_time = None
        self.response_time = None
        self.request = self.template
        self.response = None


# An exception to be called when functions in this
# module fail.
class HttpException(Exception):
    def __init__(self, message, errors):
        super(HttpException, self).__init__(message)
        self.errors = errors


# Used when the proxy option is selected, edits the HTTP request
# so that the URI now contains the scheme and domain name
# of the remote server. If authentication is enabled, this
# also carries the username and password, encoded in Base64, to
# the server under the Proxy-Authorization header. HTTPS via
# the CONNECT method is not supported yet, so any traffic
# between the client and the proxy server is unencrypted.
def proxify(template, dest_host, https, auth=False, username="", password=""):
    r = RequestPacket(template)
    new_uri = 'https://' if https else 'http://'
    new_uri += dest_host
    new_uri += r.uri
    r.uri = new_uri
    if auth:
        cred_bytes = bytes(username + ':' + password, 'utf-8')
        encoded_cred = b64encode(cred_bytes).decode('utf-8')
        key = 'Proxy-Authorization'
        val = 'Basic ' + encoded_cred
        r.headers.append((key, val))
    return r.format()


def set_content_len(request_str):
    r = RequestPacket(request_str)
    data_len = str(len(r.data))
    for key, value in r.headers:
        if key == 'Content-Length':
            r.headers.remove((key, value))
            break
    r.headers.append(('Content-Length', data_len))
    return r.format()


# Asynchronous function to read an HTTP request from a socket-like
# object. Pretty messy and unreliable at the moment, will be changed soon
async def http_read(reader):
    data = b''
    while True:
        buf = await reader.read(BUFF)
        data += buf
        if b'\r\n\r\n' in data:
            nl = b'\r\n'
            break
        elif b'\n\n' in data:
            nl = b'\n'
            break
        else:
            continue
    headers = data.partition(nl*2)[0]
    cl = [line for line in headers.split(nl) if b'Content-Length' in line]
    if len(cl) != 1:
        raise HttpException("Content-Length header not found", "http_read")
    content_len = int(cl[0].split(b' ')[1].rstrip())
    so_far = len(data.partition(nl)[2])
    while so_far < content_len:
        buf = await reader.read(BUFF)
        data += buf
        so_far += BUFF
    return data
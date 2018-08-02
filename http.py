import re
from base64 import b64encode
from constants import *

# An object representing a single HTTP request
# to the server, including the parameters
# and response.
class Request():
    def __init__(self, template, params):
        self.template = template
        self.params = params
        self.request_time = None
        self.response_time = None
        self.request = template
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
# the server under the Proxy-Authorization header.
def proxify(template, dest_host, https, auth=False, username="", password=""):
    nl = '\r\n'
    top_line, rest= template.split(nl, 1)
    path_version = top_line.partition(' ')[2]
    path = path_version.rpartition(' ')[0]
    full_pattern = 'https?:\/\/.+'
    path_pattern = '\/.+'
    if re.match(full_pattern, path):
        pass
    elif re.match(path_pattern, path):
        scheme = 'https://' if https else 'http://'
        new_uri = scheme + dest_host + path
        template = template.replace(path, new_uri, 1)
    else:
        raise HttpException("Bad URI in template", "proxify")
    if auth:
        pauth_header = "Proxy-Authorization: Basic "
        cred_bytes = bytes(username + ':' + password, 'utf-8')
        encoded_cred = b64encode(cred_bytes).decode('utf-8')
        pauth_header += encoded_cred
        top_line, rest = template.split(nl, 1)
        template = top_line + nl + pauth_header + nl + rest
    return template


# Ensures that the HTTP request ends with two DOS style
# newlines, if this is not the case, the request will probably
# time out.
def add_req_newlines(request):
    end = '\r\n\r\n'
    if request.endswith(end):
        return request
    else:
        request = request.rstrip('\r\n ')
        request += end
        return request

# Again a pretty messy function that sets the Content-Length
# header of a request that contains data to the length of the
# request data.
def set_content_len(request_str):
    nl = '\r\n'
    stripped = request_str.rstrip()
    split = stripped.split(nl*2, 1)
    if len(split) == 1:
        return request_str
    elif len(split) == 2:
        headers, data = split
        new_header = 'Content-Length: %d' % len(data)
        pattern = 'Content-Length: \d+'
        result = re.sub(pattern, new_header, request_str)
        return result
    else:
        raise HttpException("Invalid newlines in request", "set_content_len")


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
        print(data, cl, headers, nl, sep='\n')
        raise HttpException("Content-Length header not found", "http_read")
    content_len = int(cl[0].split(b' ')[1].rstrip())
    so_far = len(data.partition(nl)[2])
    while so_far < content_len:
        buf = await reader.read(BUFF)
        data += buf
        so_far += BUFF
    return data
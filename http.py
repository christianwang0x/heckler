import re
from base64 import b64encode

class HttpException(Exception):
    def __init__(self, message, errors):
        super(HttpException, self).__init__(message)
        self.errors = errors


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
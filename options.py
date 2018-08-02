import re

from encoders import *
from constants import *


# An object to represent the user-defined and current
# state values of the app. Most of the methods for this
# object are used for validation.
class Options:
    def __init__(self):
        self.progress_bar = None
        self.running = None
        self.data = None
        self.host = None
        self.port = None
        self.https = None
        self.mode = None
        self.marker_no = None
        self.ps_box = None
        self.ps_sets = dict()
        self.add_p = None
        self.timeout = None
        self.update_cl = None
        self.proxy = None
        self.proxy_host = None
        self.proxy_port = None
        self.proxy_auth = None
        self.proxy_user = None
        self.proxy_pass = None
        self.reconnects = None
        self.recon_delay = None
        self.threads = None
        self.request_delay = None
        self.encoder = None
        self.vs = [(self.data_isgood, "Invalid data / markers"),
                   (self.host_isgood, "Invalid host"),
                   (self.port_isgood, "Invalid port"),
                   (self.proxy_isgood, "Invalid proxy settings"),
                   (self.reconnects_isgood, "Invalid number of reconnects"),
                   (self.recon_delay_isgood, "Invalid reconnect delay"),
                   (self.threads_isgood, "Invalid number of threads"),
                   (self.req_delay_isgood, "Invalid request delay"),
                   (self.mode_isgood, "Invalid mode"),
                   (self.timeout_isgood, "Invalid timeout")]

    # Encode all the payloads in the payload set with the
    # selected encoder. This encodes them in place, no
    # return value should be expected.
    def encode_all_payloads(self, encoder):
        if encoder == "None":
            return None
        elif encoder == "Hexadecimal":
            E = AsciiHex
        elif encoder == "Base 64":
            E = Base64
        elif encoder == "MD5":
            E = MD5
        else:
            return None
        for key in self.ps_sets:
            p_list = self.ps_sets[key]
            e_list = encode_list(p_list, E)
            self.ps_sets[key] = e_list

    # Ensures that the user-defined request timeout
    # is a positive integer
    def timeout_isgood(self):
        t = self.timeout.GetValue()
        if t.isdigit() and int(t) > 0:
            return True
        else:
            return False

    # Ensures that the markers in the data box
    # are in pairs and that the first left marker
    # comes before the first right marker. This
    # does not do a complete check of all the markers
    # so this method will be improved in the future.
    def data_isgood(self):
        t = self.data.GetValue()
        lc, rc = (t.count(LEFT_CHAR), t.count(RIGHT_CHAR))
        if lc != rc:
            print(1)
            return False
        if self.mode.GetValue() != 'Concurrent':
            if lc != len(self.ps_sets):
                print(2)
                return False
        if t.index(LEFT_CHAR) > t.index(RIGHT_CHAR):
            print(3)
            return False
        else:
            return True

    # Ensure that the host contains only valid
    # characters.
    def valid_host(self, host):
        template = "[A-Za-z0-9-.]+"
        if re.match(template, host):
            return True
        else:
            return False

    # Ensures that the provided port is a positive
    # integer and within the range of TCP ports.
    def valid_port(self, port):
        if port.isdigit():
            if 0 < int(port) > 65535:
                return False
            else:
                return True

    # Ensures that the provided mode corresponds
    # to the number of parameter lists provided.
    # If in Serial or Concurrent mode, there should
    # be only one list. Otherwise there should be
    # multiple.
    # Pretty messy I'll clean it up later.
    def mode_isgood(self):
        mode = self.mode.GetValue()
        if len(self.ps_sets) == 1:
            if mode == "Serial" or mode == "Concurrent":
                pass
            else:
                return False
        elif len(self.ps_sets) > 1:
            if mode == "Multiplex":
                pass
            else:
                return False
        else:
            return False
        return True

    # The actual function called to validate the
    # host.
    def host_isgood(self):
        host = self.host.GetValue()
        if self.valid_host(host):
            return True
        else:
            return False

    # The actual function called to validate the
    # port
    def port_isgood(self):
        port = self.port.GetValue()
        if self.valid_port(port):
            return True
        else:
            return False

    # Ensures that the user-supplied proxy info
    # is correct. If proxy is disabled it's
    # valid. If the supplied host or port are
    # invalid, or if the authentication
    # values are invalid this will fail.
    # Does not allow for blank proxy passwords.
    def proxy_isgood(self):
        if self.proxy.GetValue():
            phost = self.proxy_host.GetValue()
            pport = self.proxy_port.GetValue()
            if not self.valid_host(phost):
                return False
            elif not self.valid_port(pport):
                return False

            pauth = self.proxy_auth.GetValue()
            if not pauth:
                return True
            puser = self.proxy_user.GetValue()
            ppass = self.proxy_pass.GetValue()
            if not puser or not ppass:
                return False
            else:
                return True
        else:
            return True

    # Ensures that the number of reconnects
    # to be attempted is a positive number.
    def reconnects_isgood(self):
        r = self.reconnects.GetValue()
        if r.isdigit() and int(r) >= 0:
            return True
        else:
            return False

    # Ensures that the delay between
    # reconnect attempts is valid
    def recon_delay_isgood(self):
        r = self.recon_delay.GetValue()
        if r.isdigit and int(r) >= 0:
            return True
        else:
            return False

    # Ensures that the number of connection
    # threads is valid.
    def threads_isgood(self):
        t = self.threads.GetValue()
        if t.isdigit() and 0 < int(t) < MAX_THREADS:
            return True
        else:
            return False

    # Ensures that the delay between requests
    # is valid.
    def req_delay_isgood(self):
        r = self.request_delay.GetValue()
        if r.isdigit() and int(r) >= 0:
            return True
        else:
            return False

    # Validates all the options
    def validate(self):
        for func, err in self.vs:
            if not func():
                return err
        return None
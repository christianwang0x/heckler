import re

from encoders import *
from constants import *

class Options:
    def __init__(self):
        self.data = None
        self.host = None
        self.port = None
        self.https = None
        self.mode = None
        self.marker_no = None
        self.ps_box = None
        self.ps_sets = dict()
        self.add_p = None
        self.update_cl = None
        self.keep_alive = None
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
                   (self.mode_isgood, "Invalid mode")]

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



    def data_isgood(self):
        t = self.data.GetValue()
        lc, rc = (t.count(LEFT_CHAR), t.count(RIGHT_CHAR))
        if lc != rc or lc != len(self.ps_sets):
            return False
        elif t.index(LEFT_CHAR) > t.index(RIGHT_CHAR):
            return False
        else:
            return True

    def valid_host(self, host):
        template = "[A-Za-z0-9-.]+"
        if re.match(template, host):
            return True
        else:
            return False

    def valid_port(self, port):
        if port.isdigit():
            if 0 < int(port) > 65535:
                return False
            else:
                return True

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

    def host_isgood(self):
        host = self.host.GetValue()
        if self.valid_host(host):
            return True
        else:
            return False

    def port_isgood(self):
        port = self.port.GetValue()
        if self.valid_port(port):
            return True
        else:
            return False

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

    def reconnects_isgood(self):
        r = self.reconnects.GetValue()
        if r.isdigit():
            return True
        else:
            return False

    def recon_delay_isgood(self):
        r = self.recon_delay.GetValue()
        if r.isdigit and int(r) >= 0:
            return True
        else:
            return False

    def threads_isgood(self):
        t = self.threads.GetValue()
        if t.isdigit() and 0 <int(t) < 256:
            return True
        else:
            return False

    def req_delay_isgood(self):
        r = self.request_delay.GetValue()
        if r.isdigit() and int(r) >= 0:
            return True
        else:
            return False

    def validate(self):
        for func, err in self.vs:
            if not func():
                return err
        return None
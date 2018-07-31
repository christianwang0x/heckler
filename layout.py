from default_settings import *
from events import EventsFrame
import wx


class LayoutFrame(EventsFrame):
    def __init__(self, *args, **kwargs):
        super(LayoutFrame, self).__init__(*args, **kwargs)
        self.panel = wx.Panel(self)
        self.progress_bar = None
        self.InitLayout()

    def InitLayout(self):
        panel = self.panel
        sizer = wx.GridBagSizer(1, 1)
        panel.SetSizer(sizer)
        data_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        data_box.SetFont(self.fwfont)
        data_box.SetValue(DEFAULT_REQUEST_DATA)
        self.ops.data = data_box
        sizer.Add(data_box, pos=(0, 1), span=(30, 2), flag=wx.EXPAND)

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(18)

        run_btn = wx.Button(panel, label="Run", size=(120,25))
        run_btn.SetFont(self.hfont)
        sizer.Add(run_btn, pos=(0, 4))
        run_btn.Bind(wx.EVT_BUTTON, self.OnRun)

        stop_btn = wx.Button(panel, label="Stop", size=(120,25))
        stop_btn.SetFont(self.hfont)
        sizer.Add(stop_btn, pos=(0,5))
        stop_btn.Bind(wx.EVT_BUTTON, self.OnStop)

        cnt_btn = wx.Button(panel, label="Continue", size=(120, 25))
        cnt_btn.SetFont(self.hfont)
        sizer.Add(cnt_btn, pos=(0,6))
        cnt_btn.Bind(wx.EVT_BUTTON, self.OnRun)

        host_lbl = wx.StaticText(panel, label="Host:")
        host_lbl.SetFont(self.hfont)
        sizer.Add(host_lbl, pos=(3,4))
        host_txt = wx.TextCtrl(panel)
        host_txt.SetFont(self.hfont)
        host_txt.SetValue(DEFAULT_HOST)
        self.ops.host = host_txt
        sizer.Add(host_txt, pos=(3, 5), span=(1, 2), flag=wx.EXPAND)

        port_lbl = wx.StaticText(panel, label="Port:")
        port_lbl.SetFont(self.hfont)
        sizer.Add(port_lbl, pos=(4, 4))
        port_txt = wx.TextCtrl(panel)
        port_txt.SetFont(self.hfont)
        port_txt.SetValue(DEFAULT_PORT)
        self.ops.port = port_txt
        sizer.Add(port_txt, pos=(4, 5), flag=wx.EXPAND)
        ssl_chk = wx.CheckBox(panel, label="HTTPS")
        ssl_chk.SetFont(self.hfont)
        ssl_chk.SetValue(DEFAULT_HTTPS)
        self.ops.https = ssl_chk
        sizer.Add(ssl_chk, pos=(4, 6))

        sep1 = wx.StaticLine(panel, size=(300, 1))
        sizer.Add(sep1, pos=(6, 4), span=(1, 4), flag=wx.ALIGN_CENTER)

        mode_lbl = wx.StaticText(panel, label="Mode:")
        mode_lbl.SetFont(self.hfont)
        sizer.Add(mode_lbl, pos=(8, 4))
        mode_names = ['Serial', 'Concurrent', 'Multiplex', 'Permuter']
        mode_cb = wx.ComboBox(panel, choices=mode_names,
                              style=wx.CB_READONLY)
        mode_cb.SetFont(self.hfont)
        mode_cb.SetValue(mode_names[0])
        self.ops.mode = mode_cb
        sizer.Add(mode_cb, pos=(8, 5), span=(1, 2))

        mark_lbl = wx.StaticText(panel, label="Marker #:")
        mark_lbl.SetFont(self.hfont)
        sizer.Add(mark_lbl, pos=(9, 4))
        mark_numbers = [str(i) for i in range(1, 17)]
        mark_cb = wx.ComboBox(panel, choices=mark_numbers,
                              style=wx.CB_READONLY)
        mark_cb.SetValue(mark_numbers[0])
        mark_cb.SetFont(self.hfont)
        self.ops.marker_no = mark_cb
        sizer.Add(mark_cb, pos=(9, 5))
        mark_cb.Bind(wx.EVT_COMBOBOX, self.OnSelectPS)

        load_ps_btn = wx.Button(panel, label="Load File", size=(90, 25))
        load_ps_btn.SetFont(self.hfont)
        sizer.Add(load_ps_btn, pos=(9, 6))
        load_ps_btn.Bind(wx.EVT_BUTTON, self.OnLoadSetFile)

        ps_lb = wx.ListBox(panel)
        ps_lb.SetFont(self.hfont)
        self.ops.ps_box = ps_lb
        sizer.Add(ps_lb, pos=(10, 5), span=(5, 2), flag=wx.EXPAND)

        ps_label = wx.StaticText(panel, label="Parameter list:")
        sizer.Add(ps_label, pos=(11, 4))

        ps_clr_btn = wx.Button(panel, label="Clear", size=(90, 25))
        ps_clr_btn.Bind(wx.EVT_BUTTON, self.OnClearPS)
        ps_clr_btn.SetFont(self.hfont)
        sizer.Add(ps_clr_btn, pos=(13, 4))

        ps_del_btn = wx.Button(panel, label="Delete", size=(90, 25))
        ps_del_btn.Bind(wx.EVT_BUTTON, self.OnDelP)
        ps_del_btn.SetFont(self.hfont)
        sizer.Add(ps_del_btn, pos=(14, 4))


        add_pl_btn = wx.Button(panel, label="Add", size=(90, 25))
        add_pl_btn.SetFont(self.hfont)
        sizer.Add(add_pl_btn, pos=(15, 4))

        add_pl_txt = wx.TextCtrl(panel)
        add_pl_txt.SetFont(self.hfont)
        self.ops.add_p = add_pl_txt
        sizer.Add(add_pl_txt, pos=(15, 5), span=(1, 2), flag=wx.EXPAND)
        add_pl_btn.Bind(wx.EVT_BUTTON, self.OnAddP)

        encdr_lbl = wx.StaticText(panel, label="Encoder:")
        encdr_lbl.SetFont(self.hfont)
        sizer.Add(encdr_lbl, pos=(16, 4), span=(1, 1))
        encdrs = ["None", "Hexadecimal", "Base 64", "MD5"]
        encdr_cb = wx.ComboBox(panel, choices=encdrs, style=wx.CB_READONLY)
        encdr_cb.SetFont(self.hfont)
        encdr_cb.SetValue(encdrs[0])
        self.ops.encoder =encdr_cb
        sizer.Add(encdr_cb, pos=(16, 5), span=(1, 2), flag=wx.EXPAND)

        sep2 = wx.StaticLine(panel, size=(300, 1))
        sizer.Add(sep2, pos=(18, 4), span=(1, 4), flag=wx.ALIGN_CENTER)

        update_cl = wx.CheckBox(panel, label="Update Content Length Header")
        update_cl.SetFont(self.hfont)
        update_cl.SetValue(DEFAULT_UPDATE_CL)
        self.ops.update_cl = update_cl
        sizer.Add(update_cl, pos=(20, 4), span=(1, 3))

        ka_cb = wx.CheckBox(panel, label="Keep-Alive")
        ka_cb.SetValue(DEFAULT_KEEP_ALIVE)
        ka_cb.SetFont(self.hfont)
        self.ops.keep_alive = ka_cb
        sizer.Add(ka_cb, pos=(21, 4), span=(1, 3))

        proxy = wx.CheckBox(panel, label="Use Proxy")
        proxy.SetFont(self.hfont)
        proxy.SetValue(DEFAULT_USE_PROXY)
        self.ops.proxy = proxy
        sizer.Add(proxy, pos=(22, 4), span=(1, 3))

        phost_lbl = wx.StaticText(panel, label="Proxy Host:")
        phost_lbl.SetFont(self.hfont)
        sizer.Add(phost_lbl, pos=(23,4), span=(1, 1))
        phost_txt = wx.TextCtrl(panel)
        phost_txt.SetFont(self.hfont)
        phost_txt.SetValue(DEFAULT_PROXY_HOST)
        self.ops.proxy_host = phost_txt
        sizer.Add(phost_txt, pos=(23, 5), span=(1, 2), flag=wx.EXPAND)

        pport_lbl = wx.StaticText(panel, label="Proxy Port:")
        pport_lbl.SetFont(self.hfont)
        sizer.Add(pport_lbl, pos=(24,4), span=(1, 1))
        pport_txt = wx.TextCtrl(panel)
        pport_txt.SetFont(self.hfont)
        pport_txt.SetValue(DEFAULT_PROXY_PORT)
        self.ops.proxy_port = pport_txt
        sizer.Add(pport_txt, pos=(24, 5), span=(1, 2), flag=wx.EXPAND)

        proxy_auth = wx.CheckBox(panel, label="Authenticate Proxy")
        proxy_auth.SetFont(self.hfont)
        proxy_auth.SetValue(DEFAULT_AUTHENTICATE_PROXY)
        self.ops.proxy_auth = proxy_auth
        sizer.Add(proxy_auth, pos=(25, 4), span=(1, 3))

        puser_lbl = wx.StaticText(panel, label="Proxy User:")
        puser_lbl.SetFont(self.hfont)
        sizer.Add(puser_lbl, pos=(26,4), span=(1, 1))
        puser_txt = wx.TextCtrl(panel)
        puser_txt.SetValue(DEFAULT_PROXY_USER)
        puser_txt.SetFont(self.hfont)
        self.ops.proxy_user = puser_txt
        sizer.Add(puser_txt, pos=(26, 5), span=(1, 2), flag=wx.EXPAND)

        ppass_lbl = wx.StaticText(panel, label="Proxy Pass:")
        ppass_lbl.SetFont(self.hfont)
        sizer.Add(ppass_lbl, pos=(27,4), span=(1, 1))
        ppass_txt = wx.TextCtrl(panel)
        ppass_txt.SetFont(self.hfont)
        ppass_txt.SetValue(DEFAULT_PROXY_PASS)
        self.ops.proxy_pass = ppass_txt
        sizer.Add(ppass_txt, pos=(27, 5), span=(1, 2), flag=wx.EXPAND)

        ra_lbl = wx.StaticText(panel, label="Reconnect Attempts:")
        ra_lbl.SetFont(self.hfont)
        sizer.Add(ra_lbl, pos=(28,4), span=(1, 2))
        ra_txt = wx.TextCtrl(panel)
        ra_txt.SetFont(self.hfont)
        ra_txt.SetValue(DEFAULT_RA)
        self.ops.reconnects = ra_txt
        sizer.Add(ra_txt, pos=(28, 6), span=(1, 1), flag=wx.EXPAND)

        rcd_lbl = wx.StaticText(panel, label="Reconnect Delay (ms):")
        rcd_lbl.SetFont(self.hfont)
        sizer.Add(rcd_lbl, pos=(29,4), span=(1, 2))
        rcd_txt = wx.TextCtrl(panel)
        rcd_txt.SetFont(self.hfont)
        rcd_txt.SetValue(DEFAULT_RCD)
        self.ops.recon_delay = rcd_txt
        sizer.Add(rcd_txt, pos=(29, 6), span=(1, 1), flag=wx.EXPAND)

        threads_lbl = wx.StaticText(panel, label="Network Threads:")
        threads_lbl.SetFont(self.hfont)
        sizer.Add(threads_lbl, pos=(30,4), span=(1, 2))
        threads_txt = wx.TextCtrl(panel)
        threads_txt.SetFont(self.hfont)
        threads_txt.SetValue(DEFAULT_THREADS)
        self.ops.threads = threads_txt
        sizer.Add(threads_txt, pos=(30, 6), span=(1, 1), flag=wx.EXPAND)

        rqd_lbl = wx.StaticText(panel, label="Requests Delay (ms):")
        rqd_lbl.SetFont(self.hfont)
        sizer.Add(rqd_lbl, pos=(31,4), span=(1, 2))
        rqd_txt = wx.TextCtrl(panel)
        rqd_txt.SetFont(self.hfont)
        rqd_txt.SetValue(DEFAULT_RQD)
        self.ops.request_delay = rqd_txt
        sizer.Add(rqd_txt, pos=(31, 6), span=(1, 1), flag=wx.EXPAND)

        add_mark_btn = wx.Button(panel, label="Add Markers", size=(120, 25))
        add_mark_btn.SetFont(self.hfont)
        add_mark_btn.Bind(wx.EVT_BUTTON, self.OnAddMarkers)
        sizer.Add(add_mark_btn, pos=(30, 1), flag=wx.ALIGN_RIGHT)

        clr_mark_btn = wx.Button(panel, label="Clear Markers", size=(120, 25))
        clr_mark_btn.Bind(wx.EVT_BUTTON, self.OnClearMarkers)
        clr_mark_btn.SetFont(self.hfont)
        sizer.Add(clr_mark_btn, pos=(30, 2))

        progress_bar = wx.Gauge(panel, range=100)
        sizer.Add(progress_bar, pos=(31, 1), flag=wx.EXPAND, span=(1, 2))
        self.progress_bar = progress_bar
        sizer.Add((10, 10), pos=(35, 1))
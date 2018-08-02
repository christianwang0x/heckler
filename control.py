import wx
from default_settings import *
from events import EventsPanel
from wxasync import AsyncBind

# This defines the formatting and layout
# for the main control panel. Inherited directly
# from the class that defines the control panel
# events.
class ControlPanel(EventsPanel):
    # Initialize control panel
    def __init__(self, *args, **kwargs):
        super(ControlPanel, self).__init__(*args, **kwargs)
        self.InitLayout()

    # Buttons, text boxes, checkboxes and other
    # controls are defined here
    def InitLayout(self):
        sizer = wx.GridBagSizer(1, 1)
        self.SetSizer(sizer)

        # Defines the fixed width font
        self.fwfont = wx.Font(9, wx.FONTFAMILY_TELETYPE,
                              wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_NORMAL)

        # Text box where users insert the raw HTTP data
        data_box = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        data_box.SetFont(self.fwfont)
        data_box.SetValue(DEFAULT_REQUEST_DATA)
        self.ops.data = data_box
        sizer.Add(data_box, pos=(0, 1), span=(30, 2), flag=wx.EXPAND)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(18)

        # Button that runs the engine, binds using
        # AsyncBind function to allow engine to run
        # asynchronously
        run_btn = wx.Button(self, label="Run", size=(120,25))
        run_btn.SetFont(self.hfont)
        sizer.Add(run_btn, pos=(0, 4))
        AsyncBind(run_btn, wx.EVT_BUTTON, self.OnRun)

        # Button that stops the engine
        stop_btn = wx.Button(self, label="Stop", size=(120,25))
        stop_btn.SetFont(self.hfont)
        sizer.Add(stop_btn, pos=(0,5))
        stop_btn.Bind(wx.EVT_BUTTON, self.OnStop)

        # Empty cells added for formatting
        sizer.Add((120, 25), pos=(0, 6))
        sizer.Add((10, 0), pos=(0, 7))

        # Host text box and label
        host_lbl = wx.StaticText(self, label="Host: ")
        host_lbl.SetFont(self.hfont)
        sizer.Add(host_lbl, pos=(3,4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        host_txt = wx.TextCtrl(self)
        host_txt.SetFont(self.hfont)
        host_txt.SetValue(DEFAULT_HOST)
        self.ops.host = host_txt
        sizer.Add(host_txt, pos=(3, 5), span=(1, 2), flag=wx.EXPAND)

        # Port text box and label
        port_lbl = wx.StaticText(self, label="Port: ")
        port_lbl.SetFont(self.hfont)
        sizer.Add(port_lbl, pos=(4, 4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        port_txt = wx.TextCtrl(self)
        port_txt.SetFont(self.hfont)
        port_txt.SetValue(DEFAULT_PORT)
        self.ops.port = port_txt
        sizer.Add(port_txt, pos=(4, 5), flag=wx.EXPAND)

        # SSL check box and label
        ssl_chk = wx.CheckBox(self, label="HTTPS")
        ssl_chk.SetFont(self.hfont)
        ssl_chk.SetValue(DEFAULT_HTTPS)
        self.ops.https = ssl_chk
        sizer.Add(ssl_chk, pos=(4, 6))

        # Cosmetic horizontal separator line
        sep1 = wx.StaticLine(self, size=(300, 1))
        sizer.Add(sep1, pos=(6, 4), span=(1, 4), flag=wx.ALIGN_CENTER)

        # Mode drop down box and label
        mode_lbl = wx.StaticText(self, label="Mode:")
        mode_lbl.SetFont(self.hfont)
        sizer.Add(mode_lbl, pos=(8, 4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        mode_names = ['Serial', 'Concurrent', 'Multiplex']
        mode_cb = \
            wx.ComboBox(self, choices=mode_names, style=wx.CB_READONLY)
        mode_cb.SetFont(self.hfont)
        mode_cb.SetValue(DEFAULT_MODE)
        self.ops.mode = mode_cb
        sizer.Add(mode_cb, pos=(8, 5), span=(1, 2))

        # Marker number drop down box and label
        mark_lbl = wx.StaticText(self, label="Marker #:")
        mark_lbl.SetFont(self.hfont)
        sizer.Add(mark_lbl, pos=(9, 4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        mark_numbers = [str(i) for i in range(1, 17)]
        mark_cb = \
            wx.ComboBox(self, choices=mark_numbers, style=wx.CB_READONLY)
        mark_cb.SetValue(DEFAULT_MARKER)
        mark_cb.SetFont(self.hfont)
        self.ops.marker_no = mark_cb
        sizer.Add(mark_cb, pos=(9, 5))
        mark_cb.Bind(wx.EVT_COMBOBOX, self.OnSelectPS)

        # Load list of parameters from file
        load_ps_btn = wx.Button(self, label="Load File", size=(90, 25))
        load_ps_btn.SetFont(self.hfont)
        sizer.Add(load_ps_btn, pos=(9, 6))
        load_ps_btn.Bind(wx.EVT_BUTTON, self.OnLoadParamFile)

        # List box to show currently selected parameter
        # list.
        ps_label = wx.StaticText(self, label="Parameter list:")
        sizer.Add(ps_label, pos=(11, 4))
        ps_lb = wx.ListBox(self)
        ps_lb.SetFont(self.hfont)
        self.ops.ps_box = ps_lb
        sizer.Add(ps_lb, pos=(10, 5), span=(5, 2), flag=wx.EXPAND)

        # Clears the current parameter list.
        ps_clr_btn = wx.Button(self, label="Clear", size=(90, 25))
        ps_clr_btn.Bind(wx.EVT_BUTTON, self.OnClearPS)
        ps_clr_btn.SetFont(self.hfont)
        sizer.Add(ps_clr_btn, pos=(13, 4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        # Deletes the currently selected parameter. If no
        # parameter is selected, delete the last one.
        ps_del_btn = wx.Button(self, label="Delete", size=(90, 25))
        ps_del_btn.Bind(wx.EVT_BUTTON, self.OnDelP)
        ps_del_btn.SetFont(self.hfont)
        sizer.Add(ps_del_btn, pos=(14, 4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        # Button, textbox, and label to add parameter to
        # parameter list.
        add_pl_btn = wx.Button(self, label="Add", size=(90, 25))
        add_pl_btn.SetFont(self.hfont)
        sizer.Add(add_pl_btn, pos=(15, 4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        add_pl_txt = wx.TextCtrl(self)
        add_pl_txt.SetFont(self.hfont)
        self.ops.add_p = add_pl_txt
        sizer.Add(add_pl_txt, pos=(15, 5), span=(1, 2), flag=wx.EXPAND)
        add_pl_btn.Bind(wx.EVT_BUTTON, self.OnAddP)

        # Encoder label and drop down box. Will encode
        # all parameters with selected encoder.
        encdr_lbl = wx.StaticText(self, label="Encoder: ")
        encdr_lbl.SetFont(self.hfont)
        sizer.Add(encdr_lbl, pos=(16, 4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        encdrs = ["None", "Hexadecimal", "Base 64", "MD5"]
        encdr_cb = wx.ComboBox(self, choices=encdrs, style=wx.CB_READONLY)
        encdr_cb.SetFont(self.hfont)
        encdr_cb.SetValue(DEFAULT_ENCODER)
        self.ops.encoder =encdr_cb
        sizer.Add(encdr_cb, pos=(16, 5), span=(1, 2), flag=wx.EXPAND)

        # Cosmetic horizontal separator line
        sep2 = wx.StaticLine(self, size=(300, 1))
        sizer.Add(sep2, pos=(18, 4), span=(1, 4), flag=wx.ALIGN_CENTER)

        # Timeout label and textbox
        timeout_lbl = wx.StaticText(self, label="Timeout: ")
        timeout_lbl.SetFont(self.hfont)
        sizer.Add(timeout_lbl, pos=(20, 4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        timeout_txt = wx.TextCtrl(self)
        timeout_txt.SetFont(self.hfont)
        timeout_txt.SetValue(DEFAULT_TIMEOUT)
        self.ops.timeout = timeout_txt
        sizer.Add(timeout_txt, pos=(20, 5), span=(1, 1), flag=wx.EXPAND)

        # Checkbox to either enable or disable the updating of
        # the Content-Length HTTP header. This should probably
        # be used if the length of the parameters vary and the
        # PUT or POST methods are being used
        update_cl = wx.CheckBox(self, label="Update Content Length Header")
        update_cl.SetFont(self.hfont)
        update_cl.SetValue(DEFAULT_UPDATE_CL)
        self.ops.update_cl = update_cl
        sizer.Add(update_cl, pos=(21, 5), span=(1, 2))

        # Checkbox to enable or disable the use of an HTTP proxy
        proxy = wx.CheckBox(self, label="Use Proxy")
        proxy.SetFont(self.hfont)
        proxy.SetValue(DEFAULT_USE_PROXY)
        self.ops.proxy = proxy
        sizer.Add(proxy, pos=(22, 5), span=(1, 2))

        # Textbox and label to define the domain name
        # or IP address of the proxy server to connect to
        phost_lbl = wx.StaticText(self, label="Proxy Host: ")
        phost_lbl.SetFont(self.hfont)
        sizer.Add(phost_lbl, pos=(23,4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        phost_txt = wx.TextCtrl(self)
        phost_txt.SetFont(self.hfont)
        phost_txt.SetValue(DEFAULT_PROXY_HOST)
        self.ops.proxy_host = phost_txt
        sizer.Add(phost_txt, pos=(23, 5), span=(1, 2), flag=wx.EXPAND)

        # Textbox and label to define the TCP port
        # of the proxy server.
        pport_lbl = wx.StaticText(self, label="Proxy Port: ")
        pport_lbl.SetFont(self.hfont)
        sizer.Add(pport_lbl, pos=(24,4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        pport_txt = wx.TextCtrl(self)
        pport_txt.SetFont(self.hfont)
        pport_txt.SetValue(DEFAULT_PROXY_PORT)
        self.ops.proxy_port = pport_txt
        sizer.Add(pport_txt, pos=(24, 5), span=(1, 2), flag=wx.EXPAND)

        # Checkbox to enable or disable proxy authentication
        # If enabled, Proxy-Authorization header will be added
        # to the request.
        proxy_auth = wx.CheckBox(self, label="Authenticate Proxy")
        proxy_auth.SetFont(self.hfont)
        proxy_auth.SetValue(DEFAULT_AUTHENTICATE_PROXY)
        self.ops.proxy_auth = proxy_auth
        sizer.Add(proxy_auth, pos=(25, 5), span=(1, 2))

        # Proxy username used for proxy authentication
        puser_lbl = wx.StaticText(self, label="Proxy User: ")
        puser_lbl.SetFont(self.hfont)
        sizer.Add(puser_lbl, pos=(26,4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        puser_txt = wx.TextCtrl(self)
        puser_txt.SetValue(DEFAULT_PROXY_USER)
        puser_txt.SetFont(self.hfont)
        self.ops.proxy_user = puser_txt
        sizer.Add(puser_txt, pos=(26, 5), span=(1, 2), flag=wx.EXPAND)

        # Proxy password used for proxy authentication
        ppass_lbl = wx.StaticText(self, label="Proxy Pass: ")
        ppass_lbl.SetFont(self.hfont)
        sizer.Add(ppass_lbl, pos=(27,4), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        ppass_txt = wx.TextCtrl(self)
        ppass_txt.SetFont(self.hfont)
        ppass_txt.SetValue(DEFAULT_PROXY_PASS)
        self.ops.proxy_pass = ppass_txt
        sizer.Add(ppass_txt, pos=(27, 5), span=(1, 2), flag=wx.EXPAND)

        # Number of attempts to make at reconnecting to the
        # remote host upon network failure.
        ra_lbl = wx.StaticText(self, label="Reconnect Attempts: ")
        ra_lbl.SetFont(self.hfont)
        sizer.Add(ra_lbl, pos=(28,4), span=(1, 2), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        ra_txt = wx.TextCtrl(self)
        ra_txt.SetFont(self.hfont)
        ra_txt.SetValue(DEFAULT_RA)
        self.ops.reconnects = ra_txt
        sizer.Add(ra_txt, pos=(28, 6), span=(1, 1), flag=wx.EXPAND)

        # Number of milliseconds to wait between reconnect attempts
        # upon a network failure.
        rcd_lbl = wx.StaticText(self, label="Reconnect Delay (ms): ")
        rcd_lbl.SetFont(self.hfont)
        sizer.Add(rcd_lbl, pos=(29,4), span=(1, 2), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        rcd_txt = wx.TextCtrl(self)
        rcd_txt.SetFont(self.hfont)
        rcd_txt.SetValue(DEFAULT_RCD)
        self.ops.recon_delay = rcd_txt
        sizer.Add(rcd_txt, pos=(29, 6), span=(1, 1), flag=wx.EXPAND)

        # Maximum number of connections to have open with the server.
        # Be careful as high values for this can trigger
        # IDS or possibly a DoS. Maximum recommended value
        # over the Internet is 10.
        threads_lbl = wx.StaticText(self, label="Network Threads: ")
        threads_lbl.SetFont(self.hfont)
        sizer.Add(threads_lbl, pos=(30,4), span=(1, 2), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        threads_txt = wx.TextCtrl(self)
        threads_txt.SetFont(self.hfont)
        threads_txt.SetValue(DEFAULT_THREADS)
        self.ops.threads = threads_txt
        sizer.Add(threads_txt, pos=(30, 6), span=(1, 1), flag=wx.EXPAND)

        # Number of milliseconds to wait between opening a new
        # connection to the server. If there are currently the
        # max number of connections open with the server, this
        # defines the number of milliseconds to wait
        # after a connection slot has opened up.
        rqd_lbl = wx.StaticText(self, label="Requests Delay (ms):")
        rqd_lbl.SetFont(self.hfont)
        sizer.Add(rqd_lbl, pos=(31,4), span=(1, 2), flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        rqd_txt = wx.TextCtrl(self)
        rqd_txt.SetFont(self.hfont)
        rqd_txt.SetValue(DEFAULT_RQD)
        self.ops.request_delay = rqd_txt
        sizer.Add(rqd_txt, pos=(31, 6), span=(1, 1), flag=wx.EXPAND)

        # Button to add parameter markers, these markers will be added
        # at the position of the text cursor in the data box.
        # In the future I'll try to add the ability to place markers
        # at the beginning and end of a selection of text.
        add_mark_btn = wx.Button(self, label="Add Markers", size=(120, 25))
        add_mark_btn.SetFont(self.hfont)
        add_mark_btn.Bind(wx.EVT_BUTTON, self.OnAddMarkers)
        sizer.Add(add_mark_btn, pos=(30, 1), flag=wx.ALIGN_RIGHT)

        # Clear all the markers from the data text box.
        clr_mark_btn = wx.Button(self, label="Clear Markers", size=(120, 25))
        clr_mark_btn.Bind(wx.EVT_BUTTON, self.OnClearMarkers)
        clr_mark_btn.SetFont(self.hfont)
        sizer.Add(clr_mark_btn, pos=(30, 2))

        # This defines the progress bar for the current engine job.
        progress_bar = wx.Gauge(self, range=100)
        sizer.Add(progress_bar, pos=(31, 1), flag=wx.EXPAND, span=(1, 2))
        self.ops.progress_bar = progress_bar
        sizer.Add((10, 10), pos=(35, 1))
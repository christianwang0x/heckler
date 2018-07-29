import wx
import pickle
import re
import requests

from default_settings import *
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
        self.vs = [(self.data_isgood, "Invalid data"),
                   (self.host_isgood, "Invalid host"),
                   (self.port_isgood, "Invalid port"),
                   (self.proxy_isgood, "Invalid proxy settings"),
                   (self.reconnects_isgood, "Invalid number of reconnects"),
                   (self.recon_delay_isgood, "Invalid reconnect delay"),
                   (self.threads_isgood, "Invalid number of threads"),
                   (self.req_delay_isgood, "Invalid request delay")]

    def data_isgood(self):
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

    def reconnects_isgood(self):
        r = self.reconnects.GetValue()
        if r.isdigit():
            return True
        else:
            return False

    def recon_delay_isgood(self):
        r = self.recon_delay.GetValue()
        if r.isdigit and r >= 0:
            return True
        else:
            return False

    def threads_isgood(self):
        t = self.threads.GetValue()
        if t.isdigit() and 0 < t < 256:
            return True
        else:
            return False

    def req_delay_isgood(self):
        r = self.request_delay.GetValue()
        if r.isdigit() and r >= 0:
            return True
        else:
            return False

    def validate(self):
        for func, err in self.vs:
            if not func():
                return err
        return None


class EventsFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(EventsFrame, self).__init__(*args, **kwargs)
        self.ops = Options()
        self.requests = []
        self.running = False
        self.requester = None

    def OnNew(self, e):
        for opname, opobject in vars(self.ops).items():
            setattr(self.ops, opname, "")

    def OnOpen(self, e):
        pass

    def OnSave(self, e):
        with wx.FileDialog(self, "Save requests to file", wildcard="Pickle files (*.p)|*.p",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            with open(pathname, 'w') as fp:
                pickle.dump(self.requests, fp)

    def OnOpenSetup(self, e):
        with wx.FileDialog(self, "Open setup file", wildcard="Pickle files (*.p)|*.p",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            with open(pathname, 'r') as fp:
                setup = pickle.load(fp)
                for (key, value) in vars(setup):
                    getattr(self.ops, key).SetValue(value)

    def OnSaveSetup(self, e):
        with wx.FileDialog(self, "Save current setup to file", wildcard="Pickle files (*.p)|*.p",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            with open(pathname, 'w') as fp:
                pickle.dump(self.ops, fp)

    def OnExit(self, e):
        self.Close()

    def OnRun(self, e):
        if self.running:
            wx.MessageBox("Engine is already running", 'Error', wx.OK | wx.ICON_INFORMATION)
            return None
        s = self.ops.validate()
        if s:
            wx.MessageBox(s, 'Input Error', wx.OK | wx.ICON_EXCLAMATION)
            return None
        else:
            self.running = True
            self.ToolBar.EnableTool(wx.ID_STOP, True)
            self.ToolBar.EnableTool(wx.ID_EXECUTE, False)
            return None


    def OnStop(self, e):
        if not self.running:
            wx.MessageBox("Engine is not running", "Error", wx.OK | wx.ICON_INFORMATION)
            return None
        self.requester.stop_signal = True
        self.running = False
        self.ToolBar.EnableTool(wx.ID_STOP, False)
        self.ToolBar.EnableTool(wx.ID_EXECUTE, True)
        return None

    def OnPreferences(self, e):
        pass

    def OnHelp(self, e):
        wx.MessageBox(HELP_MSG, 'Help', wx.OK | wx.ICON_QUESTION)

    def OnAbout(self, e):
        wx.MessageBox(ABOUT_MSG, 'About', wx.OK | wx.ICON_INFORMATION)

    def UpdatePSBox(self):
        current_marker = self.ops.marker_no.GetValue()
        self.ops.ps_box.Clear()
        current_ps = self.ops.ps_sets.get(current_marker, [])
        for p in current_ps:
            self.ops.ps_box.Append(p)
        return None

    def OnLoadSetFile(self, e):
        with wx.FileDialog(self, "Open payload set file", wildcard="All files (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            with open(pathname, 'r') as fp:
                ps = [i.rstrip() for i in fp.readlines()]
                current_marker = self.ops.marker_no.GetValue()
                self.ops.ps_sets[current_marker] = ps
                self.UpdatePSBox()


    def OnAddP(self, e):
        new_p = self.ops.add_p.GetValue()
        current_marker = self.ops.marker_no.GetValue()
        current_ps = self.ops.ps_sets.get(current_marker)
        if current_ps is None:
            self.ops.ps_sets[current_marker] = [new_p, ]
        else:
            self.ops.ps_sets[current_marker].append(new_p)
        self.UpdatePSBox()


    def OnSelectPS(self, e):
        new_no = self.ops.marker_no.GetValue()
        new_ps = self.ops.ps_sets.get(new_no, [])
        self.ops.ps_box.Clear()
        for p in new_ps:
            self.ops.ps_box.Append(p)
        return None


class LayoutFrame(EventsFrame):
    def __init__(self, *args, **kwargs):
        super(LayoutFrame, self).__init__(*args, **kwargs)
        self.panel = wx.Panel(self)
        self.InitLayout()

    def InitLayout(self):
        panel = self.panel
        sizer = wx.GridBagSizer(3, 3)
        panel.SetSizer(sizer)
        data_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        data_box.SetValue(DEFAULT_REQUEST_DATA)
        self.ops.data = data_box
        sizer.Add(data_box, pos=(0, 1), span=(30, 2), flag=wx.EXPAND)

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(18)

        run_btn = wx.Button(panel, label="Run", size=(120,30))
        sizer.Add(run_btn, pos=(0, 4))
        run_btn.Bind(wx.EVT_BUTTON, self.OnRun)

        stop_btn = wx.Button(panel, label="Stop", size=(120,30))
        sizer.Add(stop_btn, pos=(0,5))
        stop_btn.Bind(wx.EVT_BUTTON, self.OnStop)

        cnt_btn = wx.Button(panel, label="Continue", size=(120, 30))
        sizer.Add(cnt_btn, pos=(0,6))
        cnt_btn.Bind(wx.EVT_BUTTON, self.OnRun)

        host_lbl = wx.StaticText(panel, label="Host:")
        sizer.Add(host_lbl, pos=(3,4))
        host_txt = wx.TextCtrl(panel)
        host_txt.SetValue(DEFAULT_HOST)
        self.ops.host = host_txt
        sizer.Add(host_txt, pos=(3, 5), span=(1, 2), flag=wx.EXPAND)

        port_lbl = wx.StaticText(panel, label="Port:")
        sizer.Add(port_lbl, pos=(4, 4))
        port_txt = wx.TextCtrl(panel)
        port_txt.SetValue(DEFAULT_PORT)
        self.ops.port = port_txt
        sizer.Add(port_txt, pos=(4, 5), flag=wx.EXPAND)
        ssl_chk = wx.CheckBox(panel, label="HTTPS")
        ssl_chk.SetValue(DEFAULT_HTTPS)
        self.ops.https = ssl_chk
        sizer.Add(ssl_chk, pos=(4, 6))

        sep1 = wx.StaticLine(panel, size=(300, 1))
        sizer.Add(sep1, pos=(6, 4), span=(1, 4), flag=wx.ALIGN_CENTER)

        mode_lbl = wx.StaticText(panel, label="Mode:")
        sizer.Add(mode_lbl, pos=(8, 4))
        mode_names = ['Serial', 'Concurrent', 'Multiplex', 'Permuter']
        mode_cb = wx.ComboBox(panel, choices=mode_names,
                              style=wx.CB_READONLY)
        mode_cb.SetValue(mode_names[0])
        self.ops.mode = mode_cb
        sizer.Add(mode_cb, pos=(8, 5), span=(1, 2))

        mark_lbl = wx.StaticText(panel, label="Marker #:")
        sizer.Add(mark_lbl, pos=(9, 4))
        mark_numbers = [str(i) for i in range(1, 17)]
        mark_cb = wx.ComboBox(panel, choices=mark_numbers,
                              style=wx.CB_READONLY)
        mark_cb.SetValue(mark_numbers[0])
        self.ops.marker_no = mark_cb
        sizer.Add(mark_cb, pos=(9, 5))
        mark_cb.Bind(wx.EVT_COMBOBOX, self.OnSelectPS)

        load_ps_btn = wx.Button(panel, label="Load File", size=(90, 30))
        sizer.Add(load_ps_btn, pos=(9, 6))
        load_ps_btn.Bind(wx.EVT_BUTTON, self.OnLoadSetFile)
        ps_lb = wx.ListBox(panel)
        self.ops.ps_box = ps_lb
        sizer.Add(ps_lb, pos=(10, 4), span=(5, 3), flag=wx.EXPAND)

        add_pl_btn = wx.Button(panel, label="Add", size=(90, 30))
        sizer.Add(add_pl_btn, pos=(15, 4))
        add_pl_txt = wx.TextCtrl(panel)
        self.ops.add_p = add_pl_txt
        sizer.Add(add_pl_txt, pos=(15, 5), span=(1, 2), flag=wx.EXPAND)
        add_pl_btn.Bind(wx.EVT_BUTTON, self.OnAddP)

        encdr_lbl = wx.StaticText(panel, label="Encoder:")
        sizer.Add(encdr_lbl, pos=(16, 4), span=(1, 1))
        encdrs = ["None", "Hexadecimal", "Base 64", "MD5"]
        encdr_cb = wx.ComboBox(panel, choices=encdrs, style=wx.CB_READONLY)
        encdr_cb.SetValue(encdrs[0])
        self.ops.encoder =encdr_cb
        sizer.Add(encdr_cb, pos=(16, 5), span=(1, 2), flag=wx.EXPAND)

        sep2 = wx.StaticLine(panel, size=(300, 1))
        sizer.Add(sep2, pos=(18, 4), span=(1, 4), flag=wx.ALIGN_CENTER)

        update_cl = wx.CheckBox(panel, label="Update Content Length Header")
        update_cl.SetValue(DEFAULT_UPDATE_CL)
        self.ops.update_cl = update_cl
        sizer.Add(update_cl, pos=(20, 4), span=(1, 3))

        ka_cb = wx.CheckBox(panel, label="Keep-Alive")
        ka_cb.SetValue(DEFAULT_KEEP_ALIVE)
        self.ops.keep_alive = ka_cb
        sizer.Add(ka_cb, pos=(21, 4), span=(1, 3))

        proxy = wx.CheckBox(panel, label="Use Proxy")
        proxy.SetValue(DEFAULT_USE_PROXY)
        self.ops.proxy = proxy
        sizer.Add(proxy, pos=(22, 4), span=(1, 3))

        phost_lbl = wx.StaticText(panel, label="Proxy Host:")
        sizer.Add(phost_lbl, pos=(23,4), span=(1, 1))
        phost_txt = wx.TextCtrl(panel)
        phost_txt.SetValue(DEFAULT_PROXY_HOST)
        self.ops.proxy_host = phost_txt
        sizer.Add(phost_txt, pos=(23, 5), span=(1, 2), flag=wx.EXPAND)

        pport_lbl = wx.StaticText(panel, label="Proxy Port:")
        sizer.Add(pport_lbl, pos=(24,4), span=(1, 1))
        pport_txt = wx.TextCtrl(panel)
        pport_txt.SetValue(DEFAULT_PROXY_PORT)
        self.ops.proxy_port = pport_txt
        sizer.Add(pport_txt, pos=(24, 5), span=(1, 2), flag=wx.EXPAND)

        proxy_auth = wx.CheckBox(panel, label="Authenticate Proxy")
        proxy_auth.SetValue(DEFAULT_AUTHENTICATE_PROXY)
        self.ops.proxy_auth = proxy_auth
        sizer.Add(proxy_auth, pos=(25, 4), span=(1, 3))

        puser_lbl = wx.StaticText(panel, label="Proxy User:")
        sizer.Add(puser_lbl, pos=(26,4), span=(1, 1))
        puser_txt = wx.TextCtrl(panel)
        puser_txt.SetValue(DEFAULT_PROXY_USER)
        self.ops.proxy_user = puser_txt
        sizer.Add(puser_txt, pos=(26, 5), span=(1, 2), flag=wx.EXPAND)

        ppass_lbl = wx.StaticText(panel, label="Proxy Pass:")
        sizer.Add(ppass_lbl, pos=(27,4), span=(1, 1))
        ppass_txt = wx.TextCtrl(panel)
        ppass_txt.SetValue(DEFAULT_PROXY_PASS)
        self.ops.proxy_pass = ppass_txt
        sizer.Add(ppass_txt, pos=(27, 5), span=(1, 2), flag=wx.EXPAND)

        ra_lbl = wx.StaticText(panel, label="Reconnect Attempts:")
        sizer.Add(ra_lbl, pos=(28,4), span=(1, 2))
        ra_txt = wx.TextCtrl(panel)
        ra_txt.SetValue(DEFAULT_RA)
        self.ops.reconnects = ra_txt
        sizer.Add(ra_txt, pos=(28, 6), span=(1, 1), flag=wx.EXPAND)

        rcd_lbl = wx.StaticText(panel, label="Reconnect Delay (ms):")
        sizer.Add(rcd_lbl, pos=(29,4), span=(1, 2))
        rcd_txt = wx.TextCtrl(panel)
        rcd_txt.SetValue(DEFAULT_RCD)
        self.ops.recon_delay = rcd_txt
        sizer.Add(rcd_txt, pos=(29, 6), span=(1, 1), flag=wx.EXPAND)

        threads_lbl = wx.StaticText(panel, label="Network Threads:")
        sizer.Add(threads_lbl, pos=(30,4), span=(1, 2))
        threads_txt = wx.TextCtrl(panel)
        threads_txt.SetValue(DEFAULT_THREADS)
        self.ops.threads = threads_txt
        sizer.Add(threads_txt, pos=(30, 6), span=(1, 1), flag=wx.EXPAND)

        rqd_lbl = wx.StaticText(panel, label="Requests Delay (ms):")
        sizer.Add(rqd_lbl, pos=(31,4), span=(1, 2))
        rqd_txt = wx.TextCtrl(panel)
        rqd_txt.SetValue(DEFAULT_RQD)
        self.ops.request_delay = rqd_txt
        sizer.Add(rqd_txt, pos=(31, 6), span=(1, 1), flag=wx.EXPAND)

        add_mark_btn = wx.Button(panel, label="Add Markers", size=(120, 30))
        sizer.Add(add_mark_btn, pos=(30, 1), flag=wx.ALIGN_RIGHT)
        clr_mark_btn = wx.Button(panel, label="Clear Markers", size=(120, 30))
        sizer.Add(clr_mark_btn, pos=(30, 2))

        progress_bar = wx.Gauge(panel, range=100)
        sizer.Add(progress_bar, pos=(31, 1), flag=wx.EXPAND, span=(1, 2))
        self.progress_bar = progress_bar
        sizer.Add((10, 10), pos=(35, 1))


class MenuFrame(LayoutFrame):
    def __init__(self, *args, **kwargs):
        super(MenuFrame, self).__init__(*args, **kwargs)
        self.InitMenu()

    def InitMenu(self):
        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        new_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&New')
        open_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Open')
        save_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Save')
        open_setup_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Open Setup')
        save_setup_mi = wx.MenuItem(file_menu, wx.ID_ANY, '&Save Setup')
        exit_mi = wx.MenuItem(file_menu, wx.ID_ANY, 'Exit')

        [ file_menu.AppendItem(i) for i in (new_mi, open_mi, save_mi) ]
        file_menu.AppendSeparator()
        [ file_menu.AppendItem(i) for i in (open_setup_mi, save_setup_mi) ]
        file_menu.AppendSeparator()
        file_menu.AppendItem(exit_mi)
        
        control_menu = wx.Menu()
        run_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Run')
        abort_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Abort')
        stop_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Stop')
        preferences_mi = wx.MenuItem(control_menu, wx.ID_ANY, '&Preferences')

        [ control_menu.AppendItem(i) for i in (run_mi, abort_mi, stop_mi)]
        control_menu.AppendSeparator()
        control_menu.AppendItem(preferences_mi)

        help_menu = wx.Menu()
        help_mi = wx.MenuItem(help_menu, wx.ID_ANY, '&Help')
        about_mi = wx.MenuItem(help_menu, wx.ID_ANY, '&About')

        help_menu.AppendItem(help_mi)
        help_menu.AppendItem(about_mi)
        help_menu.AppendSeparator()

        self.Bind(wx.EVT_MENU, self.OnNew, new_mi)
        self.Bind(wx.EVT_MENU, self.OnOpen, open_mi)
        self.Bind(wx.EVT_MENU, self.OnSave, save_mi)
        self.Bind(wx.EVT_MENU, self.OnOpenSetup, open_setup_mi)
        self.Bind(wx.EVT_MENU, self.OnSaveSetup, save_setup_mi)
        self.Bind(wx.EVT_MENU, self.OnExit, exit_mi)
        
        self.Bind(wx.EVT_MENU, self.OnRun, run_mi)
        self.Bind(wx.EVT_MENU, self.OnStop, stop_mi)
        self.Bind(wx.EVT_MENU, self.OnPreferences, preferences_mi)
        
        self.Bind(wx.EVT_MENU, self.OnHelp, help_mi)
        self.Bind(wx.EVT_MENU, self.OnAbout, about_mi)

        menubar.Append(file_menu, '&File')
        menubar.Append(control_menu, '&Control')
        menubar.Append(help_menu, '&Help')

        self.SetMenuBar(menubar)

class WindowFrame(MenuFrame):
    def __init__(self, *args, **kwargs):
        super(WindowFrame, self).__init__(*args, **kwargs)
        self.InitWindow()
        
    def InitWindow(self):
        self.SetSize((860, 860))
        self.SetTitle('Heckler Control')
        self.Center()


class ToolbarFrame(WindowFrame):
    def __init__(self, *args, **kwargs):
        super(ToolbarFrame, self).__init__(*args, **kwargs)
        self.toolbar = None
        self.InitToolbar()

    def InitToolbar(self):
        toolbar = wx.ToolBar(self, wx.ID_ANY, pos=(0, 0))
        self.ToolBar = toolbar
        new_tb = toolbar.AddTool(wx.ID_ANY, wx.Bitmap('res/icon/file.png'))
        open_tb = toolbar.AddTool(wx.ID_OPEN, wx.Bitmap('res/icon/folder-open.png'))
        save_tb = toolbar.AddTool(wx.ID_SAVE, wx.Bitmap('res/icon/save.png'))
        exit_tb = toolbar.AddTool(wx.ID_EXIT, wx.Bitmap('res/icon/sign-out-alt.png'))
        run_tb = toolbar.AddTool(wx.ID_EXECUTE, wx.Bitmap('res/icon/play.png'))
        stop_tb = toolbar.AddTool(wx.ID_STOP, wx.Bitmap('res/icon/stop.png'))
        toolbar.EnableTool(wx.ID_STOP, False)
        toolbar.EnableTool(wx.ID_EXECUTE, False)
        toolbar.Bind(wx.EVT_TOOL, self.OnNew, new_tb)
        toolbar.Bind(wx.EVT_TOOL, self.OnOpen, open_tb)
        toolbar.Bind(wx.EVT_TOOL, self.OnSave, save_tb)
        toolbar.Bind(wx.EVT_TOOL, self.OnExit, exit_tb)
        toolbar.Bind(wx.EVT_TOOL, self.OnRun, run_tb)
        toolbar.Bind(wx.EVT_TOOL, self.OnStop, stop_tb)
        toolbar.Realize()


def main():
    app = wx.App()
    toolbar_frame = ToolbarFrame(None)
    toolbar_frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()

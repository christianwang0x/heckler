import wx
import pickle
import engine
import asyncio
import http
from options import Options
from constants import *
from default_settings import *


class EventsPanel(wx.Panel):
    def __init__(self, parent_window, *args, **kwargs):
        super(EventsPanel, self).__init__(*args, **kwargs)
        self.ops = Options()
        self.requests = []
        self.hfont = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        self.hfont.SetPointSize(9)
        self.fwfont = wx.Font(9, wx.FONTFAMILY_TELETYPE,
                              wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_NORMAL)
        self.parent_window = parent_window
        self.engine = None
        self.progress_bar = None

    async def OnRun(self, e):
        if self.ops.running:
            wx.MessageBox("Engine is already running", 'Error', wx.OK | wx.ICON_INFORMATION)
            return None

        s = self.ops.validate()
        if s:
            wx.MessageBox(s, 'Input Error', wx.OK | wx.ICON_EXCLAMATION)
            return None
        else:
            self.ops.running = True
            self.parent_window.ToolBar.EnableTool(wx.ID_STOP, True)
            self.parent_window.ToolBar.EnableTool(wx.ID_EXECUTE, False)


            _ssl = bool(self.ops.https.GetValue())
            template = self.ops.data.GetValue()
            encoder = self.ops.encoder.GetValue()
            self.ops.encode_all_payloads(encoder)
            pset = self.ops.ps_sets
            mode = self.ops.mode.GetValue()
            proxy = bool(self.ops.proxy.GetValue())
            pauth = bool(self.ops.proxy_auth.GetValue())
            puser = self.ops.proxy_user.GetValue()
            ppass = self.ops.proxy_pass.GetValue()
            dest_host = self.ops.host.GetValue()
            if proxy:
                template = http.proxify(template, dest_host, _ssl,
                                        auth=pauth, username=puser,
                                        password=ppass)
            E = engine.Engine(self.ops,  self.parent_window.loop)
            tasks = []
            task = self.parent_window.loop.create_task(E.run(template, pset, _ssl, mode, self.progress_bar))
            tasks.append(task)
            await asyncio.wait(tasks)
            requests = tasks[0].result()
            self.parent_window.CreateViewer(requests)
            self.requests = requests
            self.ops.running = False
            self.parent_window.ToolBar.EnableTool(wx.ID_STOP, False)
            self.parent_window.ToolBar.EnableTool(wx.ID_EXECUTE, True)
            return None

    def OnStop(self, e):
        if not self.ops.running:
            wx.MessageBox("Engine is not running", "Error", wx.OK | wx.ICON_INFORMATION)
            return None
        # self.requester.stop_signal = True
        self.ops.running = False
        self.parent_window.ToolBar.EnableTool(wx.ID_STOP, False)
        self.parent_window.ToolBar.EnableTool(wx.ID_EXECUTE, True)
        return None

    def OnNew(self, e):
        self.ops.data.SetValue(DEFAULT_REQUEST_DATA)
        self.ops.host.SetValue(DEFAULT_HOST)
        self.ops.port.SetValue(DEFAULT_PORT)
        self.ops.https.SetValue(DEFAULT_HTTPS)
        self.ops.mode.SetValue(DEFAULT_MODE)
        self.ops.marker_no.SetValue(DEFAULT_MARKER)
        self.ops.ps_box.Clear()
        self.ops.encoder.SetValue(DEFAULT_ENCODER)
        self.ops.timeout.SetValue(DEFAULT_TIMEOUT)
        self.ops.update_cl.SetValue(DEFAULT_UPDATE_CL)
        self.ops.proxy.SetValue(DEFAULT_USE_PROXY)
        self.ops.proxy_host.SetValue(DEFAULT_PROXY_HOST)
        self.ops.proxy_port.SetValue(DEFAULT_PROXY_PORT)
        self.ops.proxy_auth.SetValue(DEFAULT_AUTHENTICATE_PROXY)
        self.ops.proxy_user.SetValue(DEFAULT_PROXY_USER)
        self.ops.proxy_pass.SetValue(DEFAULT_PROXY_PASS)
        self.ops.reconnects.SetValue(DEFAULT_RA)
        self.ops.recon_delay.SetValue(DEFAULT_RCD)
        self.ops.threads.SetValue(DEFAULT_THREADS)
        self.ops.request_delay.SetValue(DEFAULT_RQD)
        self.progress_bar.SetValue(0)
        return None

    def OnSave(self, e):
        if not self.requests:
            wx.MessageBox("No requests have been made yet!", "Save error", wx.ICON_EXCLAMATION)
            return
        with wx.FileDialog(self, "Save requests to file", wildcard="Pickle files (*.p)|*.p",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            with open(pathname, 'w') as fp:
                pickle.dump(self.requests, fp)

    def OnOpen(self, e):
        with wx.FileDialog(self, "Open requests file", wildcard="Pickle files (*.p)|*.p",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            with open(pathname, 'r') as fp:
                reqs = pickle.load(fp)
                self.parent_window.CreateViewer(reqs)


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

    def OnPreferences(self, e):
        wx.MessageBox("No preferences yet", "Preferences", wx.OK)

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

    def OnLoadParamFile(self, e):
        with wx.FileDialog(self, "Open parameter file", wildcard="All files (*.*)|*.*",
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
            current_ps.append(new_p)
        self.UpdatePSBox()

    def OnDelP(self, e):
        current_marker = self.ops.marker_no.GetValue()
        current_ps = self.ops.ps_sets.get(current_marker)
        if not current_ps:
            return
        selected = self.ops.ps_box.GetSelections()
        if not selected:
            current_ps.pop()
        else:
            for i in selected:
                current_ps.pop(i)
        self.UpdatePSBox()


    def OnClearPS(self, e):
        current_marker = self.ops.marker_no.GetValue()
        self.ops.ps_sets[current_marker] = []
        self.UpdatePSBox()


    def OnSelectPS(self, e):
        new_no = self.ops.marker_no.GetValue()
        new_ps = self.ops.ps_sets.get(new_no, [])
        self.ops.ps_box.Clear()
        for p in new_ps:
            self.ops.ps_box.Append(p)
        return None

    def OnAddMarkers(self, e):
        index = self.ops.data.GetInsertionPoint()
        sindex = index
        squote = chr(0xab)
        equote = chr(0xbb)
        oldtext = self.ops.data.GetValue()
        newtext = oldtext[:sindex] + squote
        newtext += equote + oldtext[sindex:]
        self.ops.data.SetValue(newtext)
        return None

    def OnClearMarkers(self, e):
        oldtext = self.ops.data.GetValue()
        newtext = oldtext.replace(chr(0xab), '')
        newtext = newtext.replace(chr(0xbb), '')
        self.ops.data.SetValue(newtext)
        return None
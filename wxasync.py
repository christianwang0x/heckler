import asyncio
import wx
import warnings
from asyncio.futures import CancelledError
from collections import defaultdict
from asyncio.events import get_event_loop


GlobalWxAsyncApp = None

# Special thanks to Christian Bodt for creating this module!

class WxAsyncApp(wx.App):
    def __init__(self, warn_on_cancel_callback=False, loop=None):
        global GlobalWxAsyncApp
        super(WxAsyncApp, self).__init__()
        if GlobalWxAsyncApp is not None:
            raise Exception("WxAsyncApp already created")
        self.loop = loop or get_event_loop()
        GlobalWxAsyncApp = self
        self.BoundObjects = {}
        self.RunningTasks = defaultdict(set)
        self.SetExitOnFrameDelete(True)
        self.exiting = False
        self.warn_on_cancel_callback = warn_on_cancel_callback

    async def MainLoop(self):
        evtloop = wx.GUIEventLoop()
        with wx.EventLoopActivator(evtloop):
            while not self.exiting:
                while evtloop.Pending():
                    evtloop.Dispatch()
                await asyncio.sleep(0.005)
                evtloop.ProcessIdle()

    def ExitMainLoop(self):
        self.exiting = True

    def AsyncBind(self, object, event_binder, async_callback):
        if object not in self.BoundObjects:
            self.BoundObjects[object] = {}
            object.Bind(wx.EVT_WINDOW_DESTROY, lambda event: self.OnDestroy(event, object))
        self.BoundObjects[object][event_binder.typeId] = async_callback
        object.Bind(event_binder, lambda event: self.OnEvent(event, object, event_binder.typeId))

    def OnEvent(self, event, obj, type):
        asyncallback = self.BoundObjects[obj][type]
        event_task = self.loop.create_task(asyncallback(event.Clone()))
        event_task.add_done_callback(self.OnEventCompleted)
        event_task.obj = obj
        self.RunningTasks[obj].add(event_task)

    def OnEventCompleted(self, event_task):
        # gather completed callbacks
        try:
            _res = event_task.result()  # get the result (exceptions from callbacks raise here)
        except CancelledError:
            pass
        self.RunningTasks[event_task.obj].remove(event_task)

    def OnDestroy(self, event, obj):
        # Cancel async callbacks
        for task in self.RunningTasks[obj]:
            task.cancel()
            if self.warn_on_cancel_callback:
                warnings.warn("cancelling callback" + str(obj) + str(task))
        del self.RunningTasks[obj]
        del self.BoundObjects[obj]


def AsyncBind(object, event, async_callback):
    if GlobalWxAsyncApp is None:
        raise Exception("Create a 'WxAsyncApp' first")
    GlobalWxAsyncApp.AsyncBind(object, event, async_callback)
import asyncio
import ssl
import time
import async_timeout

from constants import *
from http import *


# An exception of this class should be thrown if there is an
# error during the running of the engine.
class EngineException(Exception):
    def __init__(self, message, errors):
        super(EngineException, self).__init__(message)
        self.errors = errors


# This defines the mechanism that makes the actual requests to the server.
# In the future, the aiohttp library may be used, but was not originally because
# it does not support the modification of the raw HTTP data.
class Engine:
    # Stores some of the input values as instance attributes for easier
    # access by the methods. Most of these values should not change throughout
    # the life of an Engine instance. Also links the object to the loop
    # of the main app, and defines a semaphore which controls the number
    # of connection threads.
    def __init__(self, ops, loop):
        host = str(ops.host.GetValue())
        port = int(ops.port.GetValue())
        threads = int(ops.threads.GetValue())
        timeout = int(ops.timeout.GetValue())
        proxy = bool(ops.proxy.GetValue())
        self.context = ssl.create_default_context()
        self.semaphore = asyncio.Semaphore(threads)
        self.loop = loop
        self.host = ops.proxy_host.GetValue() if proxy else host
        self.port = int(ops.proxy_port.GetValue() if proxy else port)
        self.timeout = timeout
        self.requests_made = 0
        self.ops = ops
        self.update_cl = bool(ops.update_cl.GetValue())
        self.progress_bar = ops.progress_bar

    # Returns a request in serial mode
    def gen_serial(self, template, param):
        req = Request(template, [param])
        req = self.sub_marker(req, param)
        return req

    # Generator for requests in serial mode
    # Each call yields a request with the single
    # pair of markers substituted with one parameter
    def gen_serials(self, template, param_set):
        if len(param_set) != 1:
            raise EngineException("Bad parameters", "Serial")
        param_list = param_set[list(param_set.keys())[0]]
        for param in param_list:
            yield self.gen_serial(template, param)

    # Returns a request in concurrent mode
    def gen_concurrent(self, template, param):
        req = Request(template, [param])
        while req.request.count(LEFT_CHAR):
            req = self.sub_marker(req, param)
        return req

    # Generator for requests in concurrent mode
    # Each call yields a request with every pair
    # of markers substituted with the same parameter
    # from a single list.
    def gen_concurrents(self, template, param_set):
        param_list = param_set[list(param_set.keys())[0]]
        for param in param_list:
            yield self.gen_concurrent(template, param)

    # Substutues a pair of markers with a parameter
    def sub_marker(self, req, param):
        lb_index = req.request.index(LEFT_CHAR)
        rb_index = req.request.index(RIGHT_CHAR)
        req.request = req.request[:lb_index] + param + req.request[rb_index + 1:]
        req.request = add_req_newlines(req.request)
        if self.update_cl:
            req.request = set_content_len(req.request)
        return req

    # Returns a request in multiplex mode.
    def gen_multiplex(self, template, param_list):
        req = Request(template, param_list)
        req.request = template
        for p in param_list:
            req = self.sub_marker(req, p)
        return req

    # Generator for requests in multiplex mode
    # Each call yields a request with each pair
    # of markers substituted with a parameter
    # from that pair's corresponding list.
    def gen_multiplexes(self, template, param_set):
        min_len = min([len(param_set[i]) for i in param_set.keys()])
        for j in range(min_len):
            param_list = []
            for key in sorted(param_set.keys(), key=int):
                param = param_set[key][j]
                param_list.append(param)
            yield self.gen_multiplex(template, param_list)

    # Asynchronous function that makes a plain HTTP
    # request to the server.
    async def tcp_request(self, request):
        async with self.semaphore:
            async with async_timeout.timeout(self.timeout):
                reader, writer = await asyncio.open_connection(
                    self.host, int(self.port), loop=self.loop)
                request_data = request.request
                writer.write(request_data.encode())
                await writer.drain()
                request.request_time = time.time()
                data = await http_read(reader)
                writer.close()
                request.response_time = time.time()
                request.response = data
            self.requests_made += 1
            self.progress_bar.SetValue(self.requests_made)
            return request

    # Very similar to tcp_request function except for
    # HTTPS connections. Lots of redundant code here I'll
    # change this soon
    async def ssl_request(self, request):
        async with self.semaphore:
            async with async_timeout.timeout(self.timeout):
                reader, writer = await asyncio.open_connection(
                    self.host, int(self.port), loop=self.loop, ssl=self.context)
                request_data = request.request
                writer.write(request_data.encode())
                await writer.drain()
                request.request_time = time.time()
                data = await http_read(reader)
                writer.close()
                request.response_time = time.time()
                request.response = data
            self.requests_made += 1
            self.progress_bar.SetValue(self.requests_made)
            return request

    # The asynchronous function that defines the mechanism that makes
    # the requests to the server.
    async def engine(self, template, param_set, _ssl, mode):
        tasks = []
        if mode == 'Serial':
            generator = self.gen_serials(template, param_set)
        elif mode == 'Concurrent':
            generator = self.gen_concurrents(template, param_set)
        elif mode == 'Multiplex':
            generator = self.gen_multiplexes(template, param_set)
        else:
            raise EngineException("Bad mode", "Engine")
        _requests = [r for r in generator]
        self.progress_bar.SetRange(len(_requests))
        for request in _requests:
            if not self.ops.running:
                break
            if _ssl:
                t = self.loop.create_task(self.ssl_request(request))
            else:
                t = self.loop.create_task(self.tcp_request(request))
            tasks.append(t)
        await asyncio.wait(tasks)
        return [t.result() for t in tasks]

    # The function that gets called by the main app, runs the engine
    # and returns the request objects with the response values.
    async def run(self, template, param_set, _ssl, mode):
        t = [self.loop.create_task(self.engine(template, param_set, _ssl, mode))]
        await asyncio.wait(t)
        return t[0].result()
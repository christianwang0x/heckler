import asyncio
import ssl
import time
import async_timeout

from constants import *

class Request():
    def __init__(self, template, params):
        self.template = template
        self.params = params
        self.request_time = None
        self.response_time = None
        self.request = template
        self.response = None

class EngineException(Exception):
    def __init__(self, message, errors):
        super(EngineException, self).__init__(message)
        self.errors = errors

class Engine:
    def __init__(self, ops, loop):
        host = str(ops.host.GetValue())
        port = int(ops.port.GetValue())
        threads = int(ops.threads.GetValue())
        timeout = int(ops.timeout.GetValue())
        self.context = ssl.create_default_context()
        self.semaphore = asyncio.Semaphore(threads)
        self.loop = loop
        self.host = host
        self.port = int(port)
        self.timeout = timeout
        self.requests_made = 0

    def add_req_newlines(self, request):
        end = '\r\n\r\n'
        if request.endswith(end):
            return request
        else:
            request = request.rstrip('\r\n ')
            request += end
            return request

    def gen_serial(self, template, param):
        req = Request(template, [param])
        req = self.sub_marker(req, param)
        return req

    def gen_serials(self, template, param_set):
        if len(param_set) != 1:
            raise EngineException("Bad parameters", "Serial")
        param_list = param_set[list(param_set.keys())[0]]
        for param in param_list:
            yield self.gen_serial(template, param)

    def gen_concurrent(self, template, param):
        req = Request(template, [param])
        while req.request.count(LEFT_CHAR):
            req = self.sub_marker(req, param)
        return req

    def gen_concurrents(self, template, param_set):
        param_list = param_set[list(param_set.keys())[0]]
        for param in param_list:
            yield self.gen_concurrent(template, param)


    def sub_marker(self, req, param):
        lb_index = req.request.index(LEFT_CHAR)
        rb_index = req.request.index(RIGHT_CHAR)
        req.request = req.request[:lb_index] + param + req.request[rb_index + 1:]
        req.request = self.add_req_newlines(req.request)
        return req


    def gen_multiplex(self, template, param_list):
        req = Request(template, param_list)
        req.request = template
        for p in param_list:
            req = self.sub_marker(req, p)
        return req

    def gen_multiplexes(self, template, param_set):
        min_len = min([len(param_set[i]) for i in param_set.keys()])
        for j in range(min_len):
            param_list = []
            for key in sorted(param_set.keys(), key=int):
                param = param_set[key][j]
                param_list.append(param)
            yield self.gen_multiplex(template, param_list)


# for testing purposes only
    async def get_request(self, request):
        async with self.semaphore:
            await asyncio.sleep(1)
            return request

    async def http_read(self, reader):
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
            raise EngineException("Content-Length header not found", "http_read")
        content_len = int(cl[0].split(b' ')[1].rstrip())
        so_far = len(data.partition(nl)[2])
        while so_far < content_len:
            buf = await reader.read(BUFF)
            data += buf
            so_far += BUFF
        return data

    async def tcp_request(self, request):
        async with self.semaphore:
            async with async_timeout.timeout(self.timeout):
                reader, writer = await asyncio.open_connection(
                    self.host, int(self.port), loop=self.loop)
                request_data = request.request
                writer.write(request_data.encode())
                await writer.drain()
                request.request_time = time.time()
                data = await self.http_read(reader)
                writer.close()
                request.response_time = time.time()
                request.response = data
            self.requests_made += 1
            self.progress_bar.SetValue(self.requests_made)
            return request

    async def ssl_request(self, request):
        async with self.semaphore:
            async with async_timeout.timeout(self.timeout):
                reader, writer = await asyncio.open_connection(
                    self.host, int(self.port), loop=self.loop, ssl=self.context)
                request_data = request.request
                writer.write(request_data.encode())
                await writer.drain()
                request.request_time = time.time()
                data = await self.http_read(reader)
                writer.close()
                request.response_time = time.time()
                request.response = data
            self.requests_made += 1
            self.progress_bar.SetValue(self.requests_made)
            return request

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
            if _ssl:
                t = self.loop.create_task(self.ssl_request(request))
            else:
                t = self.loop.create_task(self.tcp_request(request))
            tasks.append(t)
        await asyncio.wait(tasks)
        return [t.result() for t in tasks]

    async def run(self, template, param_set, _ssl, mode, progress_bar):
        self.progress_bar = progress_bar
#        requests = self.loop.run_until_complete(
#            self.engine(template, param_set, _ssl, mode))
        t = [self.loop.create_task(self.engine(template, param_set, _ssl, mode))]
        await asyncio.wait(t)
        return t[0].result()
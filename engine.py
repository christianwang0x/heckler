import asyncio
import ssl


class EngineException(Exception):
    def __init__(self, message, errors):
        super(EngineException, self).__init__(message)
        self.errors = errors

class Engine:
    def __init__(self, host, port, threads):
        self.context = ssl.create_default_context()
        self.semaphore = asyncio.Semaphore(threads)
        self.loop = asyncio.get_event_loop()
        self.host = host
        self.port = int(port)

    def add_req_newlines(self, request):
        end = '\r\n\r\n'
        if request.endswith(end):
            return request
        else:
            request = request.rstrip('\r\n ')
            request += end
            return request

    def gen_requests(self, template, param_set):
        min_len = min([len(param_set[i]) for i in param_set.keys()])
        for j in range(min_len):
            param_list = []
            for key in sorted(param_set.keys(), key=int):
                param = param_set[key][j]
                param_list.append(param)
            yield self.gen_request(template, param_list)

    def gen_request(self, template, param_list):
        left_char = chr(0xab)
        right_char = chr(0xbb)
        if not template.count(left_char) == template.count(right_char) == len(param_list):
            raise EngineException("Bad markers or parameters", "")
        req = template
        for p in param_list:
            lb_index = req.index(left_char)
            rb_index = req.index(right_char)
            req = req[:lb_index] + p + req[rb_index + 1:]
            req = self.add_req_newlines(req)
        return req


# for testing purposes only
    async def get_request(self, request):
        async with self.semaphore:
            await asyncio.sleep(1)
            return request


# make sure you increase the buffer
    async def tcp_request(self, request):
        async with self.semaphore:
            reader, writer = await asyncio.open_connection(
                self.host, int(self.port), loop=self.loop)
            writer.write(request.encode())
            await writer.drain()
            data = await reader.read(1024)
            writer.close()
            return data

    async def ssl_request(self, request):
        async with self.semaphore:
            reader, writer = await asyncio.open_connection(
                self.host, self.port, ssl=self.context, loop=self.loop)
            writer.write(request.encode())
            await writer.drain()
            writer.close()
            data = await reader.read(1024)
            writer.close()
            return data

    async def engine(self, template, param_set, _ssl):
        tasks = []
        for request in self.gen_requests(template, param_set):
            if _ssl:
                t = self.loop.create_task(self.ssl_request(request))
            else:
                t = self.loop.create_task(self.tcp_request(request))
            tasks.append(t)
        await asyncio.wait(tasks)
        return tasks

    def run(self, template, param_set, _ssl):
        responses = self.loop.run_until_complete(
            self.engine(template, param_set, _ssl))
        return responses
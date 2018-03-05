import os
import socket


class WebServer:
    pids = []

    def __init__(self, n_cpu, address, listeners, buffer, handler):
        self.cpu_count = n_cpu
        self.address = address
        self.listeners = listeners
        self.buffer = buffer
        self.handler = handler
        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    def exec(self):
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.address)
        self.server.listen(self.listeners)
        for i in range(self.cpu_count):
            pid = os.fork()

            if pid != 0:
                self.pids.append(pid)
            else:
                print("Created worker PID: {}".format(os.getpid()))
                while True:
                    client, client_addr = self.server.accept()
                    request = client.recv(self.buffer)
                    if len(request.strip()) == 0:
                        client.close()
                        continue

                    response = self.handler.handle(request)

                    client.send(response.build())
                    client.close()

        self.server.close()

        for pid in self.pids:
            os.waitpid(pid, 0)

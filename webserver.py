import os
import socket
import time


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
                pid = os.getpid()
                print("Created worker PID: {}".format(pid))
                while True:
                    start_time = time.time()
                    client, client_addr = self.server.accept()
                    wait_time = time.time() - start_time

                    request = client.recv(self.buffer)
                    if len(request.strip()) == 0:
                        client.close()
                        continue

                    response = self.handler.handle(request)
                    handle_time = time.time() - start_time - wait_time

                    client.send(response.build())
                    client.close()
                    send_time = time.time() - start_time - wait_time - handle_time
                    all_time = time.time() - start_time
                    print("[PID {}] Request time {}; ".format(pid, all_time) +
                          "wait {} {}%; ".format(wait_time, wait_time / all_time * 100) +
                          "handle {} {}%; ".format(handle_time, handle_time / all_time * 100) +
                          "send {} {}%".format(send_time, send_time / all_time * 100))

        self.server.close()

        for pid in self.pids:
            os.waitpid(pid, 0)

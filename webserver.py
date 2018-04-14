import os
import socket
import select
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

    def start(self):
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.address)
        self.server.listen(self.listeners)
        self.server.setblocking(0)
        for i in range(self.cpu_count):
            pid = os.fork()

            if pid != 0:
                self.pids.append(pid)
            else:
                pid = os.getpid()
                print("Created worker PID: {}".format(pid))

                epoll = select.epoll()
                epoll.register(self.server.fileno(), select.EPOLLIN)

                connections = {}
                responses = {}

                while True:
                    events = epoll.poll()
                    for fileno, event in events:
                        if fileno == self.server.fileno() and event & select.EPOLLIN:
                            try:
                                connection, addr = self.server.accept()
                                connection.setblocking(0)
                                epoll.register(connection.fileno(), select.EPOLLIN)
                                connections[connection.fileno()] = connection
                            except BlockingIOError:
                                pass
                        elif event & select.EPOLLIN:
                            connection = connections[fileno]
                            request = connection.recv(self.buffer)

                            if len(request.strip()) == 0:
                                epoll.unregister(fileno)
                                connection.close()
                                del connections[fileno]
                                continue

                            responses[fileno] = self.handler.handle(request)

                            epoll.modify(fileno, select.EPOLLOUT)

                        elif event & select.EPOLLOUT:
                            connections[fileno].send(responses[fileno].build())

                            epoll.unregister(fileno)
                            connections[fileno].close()
                            del connections[fileno]
                            del responses[fileno]

                        elif event & select.EPOLLHUP:
                            epoll.unregister(fileno)
                            connections[fileno].close()
                            del connections[fileno]
                            del responses[fileno]

        self.server.close()

        for pid in self.pids:
            os.waitpid(pid, 0)

import os
import socket
import select
import struct


class WebServer:
    def __init__(self, n_cpu, address, listeners, buffer, handler):
        self.cpu_count = n_cpu
        self.address = address
        self.listeners = listeners
        self.buffer = buffer
        self.handler = handler
        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.workers = []

    def start(self):
        self.server.bind(self.address)
        self.server.listen(self.listeners)

        # создаём потомков
        for i in range(self.cpu_count):
            self.create_child()
        # массив сокетов-кандидатов на чтение
        to_read = [self.server] + [worker.pipe.fileno() for worker in self.workers]

        while True:
            readable, writable, exceptions = select.select(to_read, [], [])

            if self.server in readable:
                for worker in self.workers:
                    if worker.is_free:
                        # передаём свободному потомку запрос
                        worker.is_free = False

                        client, client_addr = self.server.accept()
                        request = client.recv(self.buffer)

                        if len(request.strip()) == 0:
                            worker.is_free = True
                            client.close()
                            break

                        worker.pipe.send(request)
                        worker.client = client
                        break

            for worker in self.workers:
                if worker.pipe.fileno() in readable:
                    # мы получили ответ от потомка
                    response = WebServer.recv_msg(worker.pipe)
                    worker.client.send(response)
                    worker.client.close()
                    worker.is_free = True

    def create_child(self):
        # создаём пару связанных анонимных сокетов
        child, parent = socket.socketpair()
        pid = os.fork()
        if pid == 0:
            # дочерний процесс
            print("Created worker PID: {}".format(os.getpid()))
            child.close()
            while True:
                # блокирующее чтение из сокета, соединяющего потомка с родителем
                request = parent.recv(self.buffer)
                response = self.handler.handle(request)
                # отправляем родителю информацию, что мы освободились
                WebServer.send_msg(parent, response.build())

        # это выполняется в родительском процессе
        self.workers.append(WebServer.Worker(child))
        parent.close()

    @staticmethod
    def send_msg(sock, msg):
        msg = struct.pack('>Q', len(msg)) + msg
        sock.sendall(msg)

    @staticmethod
    def recv_msg(sock):
        msg_len = WebServer.recv_all(sock, 8)
        if not msg_len:
            return None
        msg_len = struct.unpack('>Q', msg_len)[0]
        # Read the message data
        return WebServer.recv_all(sock, msg_len)

    @staticmethod
    def recv_all(sock, size):
        data = b''
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                return None
            data += packet
        return data

    def __del__(self):
        self.server.close()

    class Worker:
        def __init__(self, pipe):
            self.pipe = pipe
            self.is_free = True
            self.client = None

import os
import socket
import select


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
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                        # передаём свободному потомку команду принять подключение
                        worker.pipe.send(b'A')
                        worker.is_free = False
                        break

            for worker in self.workers:
                if worker.pipe.fileno() in readable:
                    # мы получили команду от потомка
                    command = worker.pipe.recv(1)
                    if command == b'F':
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
                command = parent.recv(1)
                # получаем соединение
                client, client_addr = self.server.accept()
                request = client.recv(self.buffer)

                if len(request.strip()) > 0:
                    response = self.handler.handle(request)
                    client.send(response.build())

                client.close()
                # отправляем родителю информацию, что мы освободились
                parent.send(b'F')

        # это выполняется в родительском процессе
        self.workers.append(WebServer.Worker(child))
        parent.close()

    class Worker:
        def __init__(self, pipe):
            self.is_free = True
            self.pipe = pipe

class ConfigReader:
    def __init__(self, path):
        self.host = None
        self.listen = None
        self.path = path
        self.cpu_limit = None
        self.document_root = None
        self.thread_limit = None

        self.parse()

    def parse(self):
        try:
            with open(self.path, 'rb') as f:
                line = f.readline()
                while line:
                    param = line.split(b' ')[0].decode()
                    if param == 'cpu_limit':
                        self.cpu_limit = int(line.split(b' ')[1].strip().decode())
                    elif param == 'document_root':
                        self.document_root = line.split(b' ')[1].strip().decode()
                    elif param == 'host':
                        self.host = line.split(b' ')[1].strip().decode()
                    elif param == 'listen':
                        self.listen = int(line.split(b' ')[1].strip().decode())
                    elif param == 'thread_limit':
                        self.thread_limit = int(line.split(b' ')[1].strip().decode())
                    else:
                        print('ERROR can not read param: ' + param)
                    line = f.readline()
        except IOError:
            print('ERROR can not read config file: ' + self.path)

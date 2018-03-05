class ConfigReader:
    def __init__(self, path):
        with open(path, 'rb') as f:
            line = f.readline()
            while line:
                param = line.split(b' ')[0].decode()
                if param == 'cpu_limit':
                    self.cpu_limit = int(line.split(b' ')[1].decode())
                elif param == 'document_root':
                    self.document_root = line.split(b' ')[1].decode()
                elif param == 'thread_limit':
                    pass
                else:
                    print('ERROR can not read param: ' + param)

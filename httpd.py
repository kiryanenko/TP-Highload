import argparse
import config

from webserver import WebServer
from handler import Handler


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='server')
    parser.add_argument('-r', type=str, help='root directory')
    parser.add_argument('-c', type=int, help='CPU count')
    args = vars(parser.parse_args())

    cpu_count = args['c'] or config.CPU_COUNT
    root_dir = args['r'] or config.ROOT_DIR
    address = (config.HOST, config.PORT)

    handler = Handler(root_dir)
    server = WebServer(cpu_count, address, config.LISTENERS, config.BUFFER, handler)
    server.exec()

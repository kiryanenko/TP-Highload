import argparse
import config

from webserver import WebServer
from handler import Handler
from config_reader import ConfigReader


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='server')
    parser.add_argument('-r', type=str, help='root directory')
    parser.add_argument('-c', type=int, help='CPU count')
    parser.add_argument('-H', type=int, help='host')
    parser.add_argument('-p', type=str, help='port')

    args = vars(parser.parse_args())
    config_file = ConfigReader(config.config_path)

    cpu_count = args['c'] or config_file.cpu_limit or config.CPU_COUNT
    root_dir = args['r'] or config_file.document_root or config.ROOT_DIR
    host = args['H'] or config_file.host or config.HOST
    port = args['p'] or config_file.listen or config.PORT
    address = (config.HOST, config.PORT)

    handler = Handler(root_dir)
    server = WebServer(cpu_count, address, config.LISTENERS, config.BUFFER, handler)
    server.start()

import argparse
import config

from webserver import WebServer
from handler import Handler


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='server')
    parser.add_argument('-r', type=str, help='root directory')
    parser.add_argument('-c', type=int, help='number of CPU')
    args = vars(parser.parse_args())

    n_cpu = args['c'] or config.N_CPU
    root_dir = args['r'] or config.ROOT_DIR
    address = (config.HOST, config.PORT)

    handler = Handler(root_dir)
    server = WebServer(n_cpu, address, config.LISTENERS, config.BUFF, handler)
    server.start()

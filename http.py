import argparse
import os

from webserver import WebServer
from handler import Handler


HOST = '127.0.0.1'
PORT = 80
N_CPU = os.cpu_count()
BUFF = 1024
LISTENERS = 1000
ROOT_DIR = "./"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='server')
    parser.add_argument('-r', type=str, help='root directory')
    parser.add_argument('-c', type=int, help='number of CPU')
    args = vars(parser.parse_args())

    n_cpu = args['c'] or N_CPU
    root_dir = args['r'] or ROOT_DIR
    address = (HOST, PORT)

    handler = Handler(root_dir)
    server = WebServer(n_cpu, address, LISTENERS, BUFF, handler)
    server.start()

# coding=utf-8
import os


HOST = '127.0.0.1'
PORT = 80
CPU_COUNT = os.cpu_count() + 1
BUFFER = 1024
LISTENERS = 1000
ROOT_DIR = "/var/www/html"
HTTP_VERSION = '1.1'
SERVER_NAME = 'HttpServer'
config_path = '/etc/httpd.conf'

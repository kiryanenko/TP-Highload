# coding=utf-8
import os
from urllib.parse import urlparse, unquote
from response import HttpResponse, ResponseCode, CONTENT_TYPES

METHODS = ["GET", "HEAD"]

class Handler:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    @staticmethod
    def parse_url(request):
        url = request.split(b' ')[1].decode()
        return unquote(urlparse(url).path)

    def handle(self, request):
        method = request.split(b' ')[0].decode()
        path = self.parse_url(request)
        if method in METHODS:
            response = self.process(path, method)
        else:
            response = HttpResponse(ResponseCode.NOT_ALLOWED)
        return response

    def process(self, path, method):
        # нормализую путь, убирая избыточные разделители и ссылки на предыдущие директории
        full_path = os.path.normpath(self.root_dir + path)
        response = HttpResponse(code=ResponseCode.NOT_FOUND)

        if os.path.commonprefix([full_path, self.root_dir]) != self.root_dir:
            return response         # случай /../../../ ...

        path_to_index = os.path.join(full_path, 'index.html')
        if os.path.isfile(path_to_index):
            full_path = path_to_index
        elif os.path.exists(os.path.join(full_path)):
            response.code = ResponseCode.FORBIDDEN
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
                response.body = content if method != "HEAD" else b''
                response.content_length = len(content)
                response.content_type = self.get_content_type(full_path)
                response.code = ResponseCode.OK
        except IOError as e:
            print("Error with " + e.filename)
        return response

    @staticmethod
    def get_content_type(path):
        file_type = path.split('.')[-1]
        return CONTENT_TYPES.get(file_type, '')

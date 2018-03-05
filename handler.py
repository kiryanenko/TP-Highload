# coding=utf-8
import os
from urllib.parse import unquote
from response import HttpResponse, ResponseCode, CONTENT_TYPES

METHODS = ["GET", "HEAD"]


class Handler:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    @staticmethod
    def parse_url(request):
        url = request.split(b' ')[1].decode()
        return unquote(url.split('?')[0])

    def handle(self, request):
        method = request.split(b' ')[0].decode()
        path = self.parse_url(request)
        if method not in METHODS:
            return HttpResponse(code=ResponseCode.NOT_ALLOWED)

        # нормализую путь, убирая избыточные разделители и ссылки на предыдущие директории
        full_path = os.path.normpath(self.root_dir + '/' + path)

        if os.path.commonprefix([full_path, self.root_dir]) != self.root_dir:
            return HttpResponse(code=ResponseCode.NOT_FOUND)                    # случай /../../../ ...

        path_to_index = os.path.join(full_path, 'index.html')
        if os.path.isfile(path_to_index):
            full_path = path_to_index
        elif not os.path.exists(os.path.join(full_path)):
            return HttpResponse(code=ResponseCode.NOT_FOUND)

        try:
            return self.get_content(full_path, method)
        except IOError:
            return HttpResponse(code=ResponseCode.FORBIDDEN)

    def get_content(self, path, method):
        response = HttpResponse(code=ResponseCode.OK)
        with open(path, 'rb') as f:
            content = f.read()
            response.body = content if method != "HEAD" else b''
            response.content_length = len(content)
            response.content_type = self.get_content_type(path)
        return response

    @staticmethod
    def get_content_type(path):
        file_type = path.split('.')[-1]
        return CONTENT_TYPES.get(file_type, '')

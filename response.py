from datetime import datetime
from enum import Enum

RESPONSE_STATUS = {
    200: "200 OK",
    403: "403 Forbidden",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
}

CONTENT_TYPES = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'application/javascript',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'swf': 'application/x-shockwave-flash'
}


class ResponseCode(Enum):
    OK = 200
    FORBIDDEN = 403
    NOT_FOUND = 404
    NOT_ALLOWED = 405


HTTP_VERSION = '1.1'
SERVER_NAME = 'httpserver'
HTTP_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


def http_format_date_now(format):
    return datetime.utcnow().strftime(format)


class HttpResponse:
    def __init__(self, code, content_length=0, content_type='', content=b''):
        self.code = code
        self.content_length = content_length
        self.content_type = content_type
        self.body = content

    def build(self):
        if self.code is ResponseCode.OK:
            response = self.get_success()
        else:
            response = self.get_fail()
        return response

    def get_success(self):
        return ('HTTP/{http_ver} {http_status}\r\n'
                'Server: {server_name}\r\n'
                'Date: {date}\r\n'
                'Connection: Close\r\n'
                'Content-Length: {content_length}\r\n'
                'Content-Type: {content_type}\r\n\r\n'
                ).format(http_ver=HTTP_VERSION, http_status=RESPONSE_STATUS[self.code.value],
                         server_name=SERVER_NAME, date=http_format_date_now(HTTP_DATE_FORMAT),
                         content_length=self.content_length, content_type=self.content_type).encode() + self.body

    def get_fail(self):
        return ('HTTP/{http_ver} {http_status}\r\n'
                'Server: {server_name}\r\n'
                'Date: {date}\r\n'
                'Connection: Closed\r\n\r\n').format(http_ver=HTTP_VERSION,
                                                     http_status=RESPONSE_STATUS[self.code.value],
                                                     server_name=SERVER_NAME,
                                                     date=http_format_date_now(HTTP_DATE_FORMAT)).encode()

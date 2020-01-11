from select import select
from socketserver import StreamRequestHandler,ThreadingTCPServer
from socket import socket,create_connection,inet_ntop,AF_INET6,AF_INET
from ssl import SSLContext,PROTOCOL_TLS,CERT_REQUIRED,TLSVersion
from json import *
from re import match
from os import path
from sys import argv

class config():
    CHINA_LIST = {}
    MODE = ''
    ACTIVE = ''
    UUID = ''
    CA = ''
    LOCAL_PORT = ''
    SERVER_HOST = ''
    SERVER_PORT = ''

class TLS():
    def load_TLS(self):
        context = SSLContext(PROTOCOL_TLS)
        context.minimum_version = TLSVersion.TLSv1_3
        context.verify_mode = CERT_REQUIRED
        context.check_hostname = True
        if self.CA != 'default' and self.CA != '':
            context.load_verify_locations(self.CA)
        else:
            context.load_default_certs()
        self.server = create_connection((self.SERVER_HOST, self.SERVER_PORT))
        self.server = context.wrap_socket(self.server, server_hostname=self.SERVER_HOST)

    def verify(self):
        self.server.send(self.UUID)

    def loop(self):
        try:
            while True:
                r, w, e = select([self.client, self.server], [], [])
                if self.client in r:
                    data = self.client.recv(65536)
                    if self.server.send(data) <= 0:
                        break
                if self.server in r:
                    data = self.server.recv(65536)
                    if self.client.send(data) <= 0:
                        break
        except Exception:
            pass
        finally:
            self.client.close()
            self.server.close()

class SOCKS5(config,TLS):
    def run(self):
        try:
            self.analysis_socks5()
            self.load_TLS()
            self.verify()
            self.server.send(self.host + b'\o\o' + self.port + b'\o\o')
        except Exception:
            return 0
        else:
            self.loop()

    def analysis_socks5(self):
        self.client.send(b'\x05\x00')
        request = self.client.recv(65536)
        if request[3] == 1:
            self.host = inet_ntop(AF_INET, request[4:8]).encode('utf-8')
            self.port = str(int.from_bytes(request[-2:], 'big')).encode('utf-8')
            self.client.send(b'\x05\x00\x00\x01' + request[4:])
        elif request[3] == 4:
            self.host = inet_ntop(AF_INET6, request[4:20]).encode('utf-8')
            self.port = str(int.from_bytes(request[-2:], 'big')).encode('utf-8')
            self.client.send(b'\x05\x00\x00\x04' + request[4:])
        elif request[3] == 3:
            self.host = request[5:5 + request[4]]
            self.port = str(int.from_bytes(request[-2:], 'big')).encode('utf-8')
            self.client.send(b'\x05\x00\x00\x03' + request[4:])

class HTTP(config,TLS):
    def run(self):
        try:
            self.analysis_http()
            self.mode()
        except Exception:
            return 0
        else:
            self.loop()

    def delete(self,host):
        sigment = host.split('.')
        if match('\D', sigment[-1]) == None:
            sigment.reverse()
        location = self.CHINA_LIST
        END = -len(sigment)
        for x in range(-1, END - 1, -1):
            if '*' in location:
                return True
            elif sigment[x] in location:
                if x > END:
                    location = location[sigment[x]]
                elif '|' in location[sigment[x]]:
                    return True
            else:
                break
        return False

    def analysis_http(self):
        sigment = self.request_data.split(b' ')[1]
        if b'http://' not in sigment:
            self.host = sigment.split(b':')[0]
            self.port = sigment.split(b':')[1]
        else:
            self.host = sigment.split(b'/')[2]
            if b':' in self.host:
                self.port = self.host.split(b':')[1]
                self.host = self.host.split(b':')[0]
            else:
                self.port = b'80'

    def response(self):
        if self.request_data[:7] == b'CONNECT':
            self.client.send(b'''HTTP/1.1 200 Connection Established\r\nProxy-Connection: close\r\n\r\n''')
        else:
            self.request_data = self.request_data.replace(b'Proxy-', b'', 1)
            self.request_data = self.request_data.replace(b':' + self.port, b'', 1)
            if self.port == b'80':
                self.request_data = self.request_data.replace(b'http://' + self.host, b'', 1)
            self.server.send(self.request_data)

    def mode(self):
        if self.MODE == 'global' or (self.MODE == 'auto' and not self.delete(self.host.decode('utf-8'))):
            self.load_TLS()
            self.verify()
            self.server.send(self.host+b'\o\o'+self.port+b'\o\o')
        else:
            self.server = create_connection((self.host, int(self.port)), 5)
        self.response()

class TCP_handler(StreamRequestHandler,HTTP,SOCKS5):
    def handle(self):
        try:
            self.client = self.connection
            self.request_data = self.client.recv(65536)
        except Exception:
            self.client.close()
            return 0
        else:
            if self.request_data[:1] != b'\x05':
                HTTP.run(self)
            elif self.request_data[1:3] == b'\x01\x00':
                SOCKS5.run(self)
            else:
                self.client.send(b'\x05\xff')

class Crack(ThreadingTCPServer,config):
    def __init__(self):
        self.load_config()
        ThreadingTCPServer.__init__(self, ('0.0.0.0', self.LOCAL_PORT), TCP_handler)

    def load_config(self):
        conf_path = self.translate(path.abspath(path.dirname(argv[0]))+'/crack_user.conf')
        if path.exists(conf_path):
            file = open(conf_path, 'r')
            conf = self.translate(file.read())
            conf = loads(conf)
            file.close()
            config.MODE = conf['mode']
            config.ACTIVE = conf['active']
            config.UUID = conf[self.ACTIVE]['uuid'].encode('utf-8')
            config.CA = self.translate(conf[self.ACTIVE]['ca'])
            config.LOCAL_PORT = int(conf[self.ACTIVE]['local_port'])
            config.SERVER_HOST = conf[self.ACTIVE]['server_host']
            config.SERVER_PORT = int(conf[self.ACTIVE]['server_port'])
            config.CHINA_LIST_PATH = self.translate(conf[self.ACTIVE]['china_list_path'])
            self.load_CHINA_LIST()
        else:
            example = {'mode': '','active': '','my_server':{'uuid': '','ca': '','server_host': '','server_port': '','local_port': '','china_list_path': ''}}
            file = open(conf_path, 'w')
            dump(example, file, indent=4)
            file.close()
            raise AttributeError


    def deepsearch(self,CHINA_LIST, location):
        for key in location.keys():
            if key not in CHINA_LIST:
                CHINA_LIST[key] = location[key]
            else:
                self.deepsearch(CHINA_LIST[key], location[key])

    def load_CHINA_LIST(self):
        file = open(self.CHINA_LIST_PATH,'r')
        data = load(file)
        file.close()
        for x in data:
            sigment = x.split('.')
            if match('\D', sigment[-1]) == None:
                sigment.reverse()
            location = {'|': {}}
            for y in sigment:
                location = {y: location}
            self.deepsearch(self.CHINA_LIST, location)

    def translate(self,path):
        return path.replace('\\', '/')


if __name__ == '__main__':
    try:
        server = Crack()
        server.serve_forever(0.01)
    except AttributeError:
        pass
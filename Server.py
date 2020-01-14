from select import select
from socketserver import StreamRequestHandler,ThreadingTCPServer,ThreadingUDPServer
from socket import socket,create_connection
from ssl import SSLContext,PROTOCOL_TLS,CERT_REQUIRED,TLSVersion
from json import *
from os import path
from sys import argv

class config():
    UUIDs = {}
    CRT = ''
    KEY = ''
    PORT = ''

class TCP_handler(StreamRequestHandler,config):
    def handle(self):
        try:
            self.load_TLS()
            self.verify()
            self.analysis()
            self.loop()
        except Exception:
            try:
                self.client.close()
                self.server.close()
            except Exception:
                pass
        return 0

    def analysis(self):
        self.request_data = self.client.recv(65536)
        sigment = self.request_data.split(b'\o\o')
        self.host = sigment[0]
        self.port = sigment[1]
        self.request_data = sigment[2]
        self.server = create_connection((self.host,int(self.port)))

    def load_TLS(self):
        context = SSLContext(PROTOCOL_TLS)
        context.minimum_version = TLSVersion.TLSv1_3
        context.load_cert_chain(self.CRT, self.KEY)
        self.client = context.wrap_socket(self.connection, server_side=True)

    def verify(self):
        if self.client.recv(36).decode('utf-8') not in self.UUIDs:
            raise Exception

    def loop(self):
        self.server.send(self.request_data)
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

class Crack(ThreadingTCPServer,config):
    def __init__(self):
        self.load_config()
        ThreadingTCPServer.__init__(self, ('0.0.0.0', self.PORT), TCP_handler)

    def load_config(self):
        conf_path = self.translate(path.abspath(path.dirname(argv[0])) + '/crack_server.conf')
        if path.exists(conf_path):
            file = open(conf_path, 'r')
            conf = load(file)
            file.close()
            config.UUIDs = set(conf['uuids'])
            config.CRT = self.translate(conf['crt'])
            config.KEY = self.translate(conf['key'])
            config.PORT = int(conf['port'])
        else:
            example = {'uuids': [''],'crt': '','key': '','port': ''}
            file = open(conf_path, 'w')
            dump(example, file, indent=4)
            file.close()
            raise AttributeError

    def translate(self,path):
        return path.replace('\\', '/')

if __name__ == '__main__':
    try:
        server = Crack()
        server.serve_forever(0.01)
    except AttributeError:
        pass
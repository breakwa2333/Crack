from select import select
from socketserver import StreamRequestHandler,ThreadingTCPServer,ThreadingUDPServer
from socket import socket,create_connection
from ssl import SSLContext,PROTOCOL_TLS,CERT_REQUIRED,TLSVersion,OPENSSL_VERSION
from json import load,dump
from os import path
from sys import argv

class config():
    conf_path = path.abspath(path.dirname(argv[0]))+'/crack_server.conf'
    if path.exists(conf_path):
        file = open(conf_path,'r')
        conf = load(file)
        file.close()
        UUIDs = conf['uuids']
        CRT = conf['crt']
        KEY = conf['key']
        PORT = int(conf['port'])
    else:
        example = {'uuids':[''],'crt':'','key':'','port':''}
        file = open(conf_path,'w')
        dump(example,file,indent=4)
        file.close()

class TCP_handler(StreamRequestHandler,config):
    def handle(self):
        try:
            self.load_TLS()
            self.verify()
            self.analysis()
        except Exception:
            self.client.close()
            return 0
        self.loop()

    def analysis(self):
        request = self.client.recv(65536)
        if b'http://' not in request.split(b' ')[1]:
            host = request.split(b' ')[1].split(b':')[0]
            port = request.split(b' ')[1].split(b':')[1]
        else:
            host = request.split(b' ')[1].split(b'/')[2]
            if b':' in host:
                port = host.split(b':')[1]
                host = host.split(b':')[0]
            else:
                port = b'80'
        self.server = create_connection((host,int(port)),5)
        self.response(request, host, port)

    def response(self,request,host,port):
        if request[:7] == b'CONNECT':
            self.client.send(b'''HTTP/1.1 200 Connection Established\r\nProxy-Connection: close\r\n\r\n''')
        else:
            request = request.replace(b'Proxy-', b'', 1)
            request = request.replace(b':' + port, b'', 1)
            if port == b'80':
                request = request.replace(b'http://' + host, b'', 1)
            self.server.send(request)

    def load_TLS(self):
        context = SSLContext(PROTOCOL_TLS)
        context.minimum_version = TLSVersion.TLSv1_3
        context.load_cert_chain(self.CRT, self.KEY)
        self.client = context.wrap_socket(self.connection, server_side=True)

    def verify(self):
        if self.client.recv(36).decode('utf-8') not in self.UUIDs:
            raise Exception

    def loop(self):
        while True:
            try:
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
                break
        self.client.close()
        self.server.close()

class Crack(ThreadingTCPServer,config):
    def __init__(self):
        ThreadingTCPServer.__init__(self, ('0.0.0.0', self.PORT), TCP_handler)

if __name__ == '__main__':
    try:
        server = Crack()
        server.serve_forever(0.01)
    except AttributeError:
        pass
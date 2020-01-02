from select import select
from socketserver import StreamRequestHandler,ThreadingTCPServer
from socket import socket,create_connection
from ssl import SSLContext,PROTOCOL_TLS,CERT_REQUIRED,TLSVersion,OPENSSL_VERSION
from json import load,dump
from os import path
from sys import argv

class config():
    conf_path = path.abspath(path.dirname(argv[0]))+'/crack_user.conf'
    if path.exists(conf_path):
        file = open(conf_path,'r')
        conf = load(file)
        file.close()
        MODE = conf['mode']
        ACTIVE = conf['active']
        UUID = conf[ACTIVE]['uuid'].encode('utf-8')
        CA = conf[ACTIVE]['ca']
        LOCAL_PORT = int(conf[ACTIVE]['local_port'])
        SERVER_HOST = conf[ACTIVE]['server_host']
        SERVER_PORT = int(conf[ACTIVE]['server_port'])
        CHINA_LIST_PATH = conf[ACTIVE]['china_list_path']
        CHINA_LIST = {}
    else:
        example = {'mode':'','active':'','my_server':{'uuid':'','ca':'','server_host':'','server_port':'','local_port':'','china_list_path':''}}
        file = open(conf_path,'w')
        dump(example,file,indent=4)
        file.close()

class TCP_handler(StreamRequestHandler,config):
    def handle(self):
        try:
            self.client = self.connection
            self.analysis()
        except Exception:
            self.client.close()
            return 0
        self.loop()

    def delete(self,host):
        location = self.CHINA_LIST
        sigment = host.split('.')
        END = -len(sigment)
        for x in range(-1, END - 1, -1):
            if '*' in location:
                return True
            elif sigment[x] in location:
                if x > END:
                    location = location[sigment[x]]
                elif '|' in location[sigment[x]]:
                    return True
        return False

    def analysis(self):
        if self.MODE == 'global':
            self.load_TLS()
            self.verify()
        else:
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
            if self.MODE == 'auto' and not self.delete(host.decode('utf-8')):
                self.load_TLS()
                self.verify()
                self.server.send(request)
            else:
                #print(host)
                self.server = create_connection((host, int(port)), 5)
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
        context.verify_mode = CERT_REQUIRED
        context.check_hostname = True
        context.load_verify_locations(self.CA)
        self.server = create_connection((self.SERVER_HOST, self.SERVER_PORT))
        self.server = context.wrap_socket(self.server, server_hostname=self.SERVER_HOST)

    def verify(self):
        self.server.send(self.UUID)

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
        self.load_CHINA_LIST()
        ThreadingTCPServer.__init__(self, ('0.0.0.0', self.LOCAL_PORT), TCP_handler)

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
            location = {'|': {}}
            for y in sigment:
                location = {y: location}
            self.deepsearch(self.CHINA_LIST, location)


if __name__ == '__main__':
    try:
        server = Crack()
        server.serve_forever(0.01)
    except AttributeError:
        pass
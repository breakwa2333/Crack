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
        UUID = conf['my_server']['uuid'].encode('utf-8')
        CA = conf['my_server']['ca']
        LOCAL_PORT = int(conf['my_server']['local_port'])
        SERVER_HOST = conf['my_server']['server_host']
        SERVER_PORT = int(conf['my_server']['server_port'])
    else:
        example = {'my_server':{'uuid':'','ca':'','server_host':'','server_port':'','local_port':''}}
        file = open(conf_path,'w')
        dump(example,file,indent=4)
        file.close()

class TCP_handler(StreamRequestHandler,config):
    def handle(self):
        context = SSLContext(PROTOCOL_TLS)
        context.minimum_version = TLSVersion.TLSv1_3
        context.verify_mode = CERT_REQUIRED
        context.check_hostname = True
        context.load_verify_locations(self.CA)
        server = create_connection((self.SERVER_HOST, self.SERVER_PORT))
        server = context.wrap_socket(server, server_hostname=self.SERVER_HOST)
        server.send(self.UUID)
        self.loop(self.connection,server)

    def loop(self,client,server):
        while True:
            try:
                r, w, e = select([client, server], [], [])
                if client in r:
                    data = client.recv(65536)
                    if server.send(data) <= 0:
                        break
                if server in r:
                    data = server.recv(65536)
                    if client.send(data) <= 0:
                        break
            except Exception:
                break
        client.close()
        server.close()

class Crack(ThreadingTCPServer,config):
    def __init__(self):
        ThreadingTCPServer.__init__(self, ('0.0.0.0', self.LOCAL_PORT), TCP_handler)

if __name__ == '__main__':
    try:
        server = Crack()
        server.serve_forever(0.01)
    except AttributeError:
        pass
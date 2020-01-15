from select import select
from socketserver import StreamRequestHandler,ThreadingTCPServer
from socket import socket,create_connection,inet_ntop,AF_INET6,AF_INET
from ssl import SSLContext,PROTOCOL_TLS,CERT_REQUIRED,TLSVersion
from json import *
from ipaddress import ip_address,ip_network
from re import match
from os import path
from sys import argv,getsizeof

class config():
    CHINA_LIST = set()
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

class loops():
    def loop(self):
        while True:
            r, w, e = select([self.client, self.server], [], [], 1)
            if self.client in r:
                data = self.client.recv(65536)
                if self.server.send(data) <= 0:
                    self.client.setblocking(False)
                    self.server.setblocking(False)
                    break
            if self.server in r:
                data = self.server.recv(65536)
                if self.client.send(data) <= 0:
                    self.client.setblocking(False)
                    self.server.setblocking(False)
                    break

class SOCKS5(StreamRequestHandler,TLS,loops,config):
    def run(self):
        try:
            self.analysis_socks5()
            self.load_TLS()
            self.verify()
            self.server.send(self.host + b'\o\o' + self.port + b'\o\o')
            self.loop()
        except Exception:
            pass
        try:
            self.client.close()
        except Exception:
            pass
        try:
            self.server.close()
        except Exception:
            pass
        return 0

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

class HTTP(StreamRequestHandler,TLS,loops,config):
    def run(self):
        try:
            self.analysis_http()
            self.mode()
            self.loop()
        except Exception:
            pass
        try:
            self.client.close()
        except Exception:
            pass
        try:
            self.server.close()
        except Exception:
            pass
        return 0

    def delete(self,host):

        def ip(host,diction):
            if host in diction:
                return True
            sigment_length = 1
            while True:
                sigment_length = host.find('.', sigment_length) + 1
                if sigment_length <= 0:
                    break
                if host[:sigment_length] in diction:
                    return True

        def domain(host,diction):
            if host in diction:
                return True
            sigment_length = host_length
            while True:
                sigment_length = host.rfind('.', 0, sigment_length) - 1
                if sigment_length <= -1:
                    break
                if host[sigment_length + 1:] in diction:
                    return True

        host_length = len(host)
        if match('\D', host[host.rfind('.') + 1:]) == None:
            if ip(host,self.CHINA_LIST):
                return True
        else:
            if domain(host,self.CHINA_LIST):
                return True
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

class TCP_handler(HTTP,SOCKS5):
    def handle(self):
        try:
            self.client = self.connection
            self.request_data = self.client.recv(65536)
            if self.request_data == b'':
                raise ConnectionError
        except Exception:
            self.client.close()
        else:
            if self.request_data[:1] != b'\x05':
                HTTP.run(self)
            elif self.request_data[1] > 0:
                methord = {0}
                for x in self.request_data[1:]:
                    if x in methord:
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
            self.CHINA_LIST_PATH = self.translate(conf[self.ACTIVE]['china_list_path'])
            self.GEOIP_PATH = self.translate(conf[self.ACTIVE]['geoip_path'])
            self.load_CHINA_LIST()
            self.load_GEOIP()
        else:
            example = {'mode': '','active': '','my_server':{'uuid': '','ca': '','server_host': '','server_port': '','local_port': '','china_list_path': '','geoip_path': ''}}
            file = open(conf_path, 'w')
            dump(example, file, indent=4)
            file.close()
            raise AttributeError

    def IP_CIDR(self,ipv4):
        sigment = ipv4.split('/')
        NCIDR = int(sigment[1])
        sigment = sigment[0].split('.')
        diction = {8: sigment[0] + '.*',
                   16: sigment[0] + '.' + sigment[1] + '.*',
                   24: sigment[0] + '.' + sigment[1] + '.' + sigment[2] + '.*',
                   32: sigment[0] + '.' + sigment[1] + '.' + sigment[2] + '.' + sigment[3]}
        ipv4 = []
        S = int('{:08b}'.format(int(sigment[NCIDR // 8]))[0:NCIDR % 8] + '00000000'[NCIDR % 8:8], 2)
        E = int('{:08b}'.format(int(sigment[NCIDR // 8]))[0:NCIDR % 8] + '11111111'[NCIDR % 8:8], 2)
        if int(sigment[NCIDR // 8]) <= S:
            if NCIDR in diction:
                return [diction[NCIDR]]
            for x in range(S, E + 1):
                item = ''
                for y in range(0, NCIDR // 8):
                    item += sigment[y] + '.'
                if NCIDR < 24:
                    item += str(x) + '.' + '*'
                else:
                    item += str(x)
                ipv4.append(item)
        return ipv4

    def load_CHINA_LIST(self):
        if self.CHINA_LIST_PATH != '':
            file = open(self.CHINA_LIST_PATH, 'r')
            data = load(file)
            file.close()
            for x in data:
                self.CHINA_LIST.add(x.replace('*',''))

    def load_GEOIP(self):
        if self.GEOIP_PATH != '':
            file = open(self.GEOIP_PATH, 'r')
            data = load(file)
            file.close()
            for x in data:
                for y in self.IP_CIDR(x):
                    self.CHINA_LIST.add(y.replace('*',''))

    def translate(self,path):
        return path.replace('\\', '/')

if __name__ == '__main__':
    try:
        server = Crack()
        server.serve_forever(0.01)
    except AttributeError:
        pass
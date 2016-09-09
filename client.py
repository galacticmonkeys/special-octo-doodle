import socket
import sys
import select
import utils

#Constants
RECV_BUFFER = 200
socket_list = []

#get args from stdin
args = sys.argv
if len(args) != 4:
    print "Please supply a name, server address and port."
    sys.exit()

#define client class
class Client(object):
    def __init__(self, name, address, port):
        self.address = address
        self.port = int(port)
        self.name = name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      

    def send(self, message):
        #connect to remote host
        try:
            self.socket.connect((self.address, self.port))
            self.socket.send(message) #send client name
        except:
            print(utils.CLIENT_CANNOT_CONNECT.format(self.address, self.port))
            sys.exit()

        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush()

        while True:
            socket_list = [sys.stdin, self.socket]

            # get the list sockets which are ready to be read
            rlist,wlist,xlist = select.select(socket_list,[],[])

            for sock in rlist:
                # incoming message from server ready to read
                if sock == self.socket:
                    #hacky way of saying ReceiveAll 200 bytes
                    #while data.length() < 200: #fix to match bytes
                    data = sock.recv(RECV_BUFFER)
                    # todo: error handling according to spec
                    if not data:
                        print(utils.CLIENT_SERVER_DISCONNECTED.format(self.address,self.port))
                        sys.exit()
                    else: 
                        sys.stdout.write(utils.CLIENT_WIPE_ME)
                        sys.stdout.write("\r" + data)
                        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                        sys.stdout.flush()
                else:
                    #user is sending a message
                    msg = sys.stdin.readline()
                    self.socket.sendall(msg)
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                    sys.stdout.flush()

#instantiate client class with your name, address and port
client = Client(args[1] ,args[2], args[3])

#send the name to the server
client.send(args[1])

#is connect blocking? asked on piazza
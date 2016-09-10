import socket
import sys
import select
import utils

#Constants
socket_list = []

#get args from stdin
args = sys.argv
if len(args) != 4:
    print "Please supply a name, server address and port."
    sys.exit()

# pads messages to 200 characters with spaces
def pad_message(message):
    return message.ljust(200, ' ')

# blocking recvall. recv all 200 characters
def recvall(sock, count):
    buf = ''
    while count:
        #print('enter while loop')
        newbuf = sock.recv(count) #it's blcoking!
        if not newbuf: 
            #print('no new data')
            return None
        buf += newbuf
        count -= len(newbuf)
        #print(count)
    #print('got out of whileloop')
    #print(buf)
    return buf


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
            #self.socket.sendall(message) #send client name
            self.socket.sendall(pad_message(message)) #send client name
        except:
            sys.stdout.write(utils.CLIENT_CANNOT_CONNECT.format(self.address, self.port) + "\n")
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
                    #receive all 200 char
                    data = recvall(sock, 200)
                    #data = sock.recv(200)
                    
                    #print('i got out of the loop')
                   
                    # todo: error handling according to spec
                    if not data: #socket is broken
                        sys.stdout.write(utils.CLIENT_SERVER_DISCONNECTED.format(self.address,self.port) + "\n")
                        sys.exit()
                    else: 
                        data = data.rstrip(' ')
                        sys.stdout.write(utils.CLIENT_WIPE_ME)
                        sys.stdout.write("\r")
                        if data:  #sending over blank messages
                            sys.stdout.write(data + "\n")
                        sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                        sys.stdout.flush()
                else:
                    #user is sending a message
                    msg = sys.stdin.readline()
                    msg = msg.rstrip('\n')
                    #self.socket.sendall(msg)
                    self.socket.sendall(pad_message(msg))
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX)
                    sys.stdout.flush()

#instantiate client class with your name, address and port
client = Client(args[1] ,args[2], args[3])

#send the name to the server
client.send(args[1])

# basic_server.py

import socket
import sys

RECV_BUFFER = 4096

#get stdin args
args = sys.argv
if len(args) != 2:
	print "Please supply a port."
	sys.exit()

#create a socket obj
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#get local machine name
host = "127.0.0.1"
port = args[1]

#bind to the port
serversocket.bind((host,int(float(port))))

#start listening
serversocket.listen(5)

while True:
	clientsocket,addr = serversocket.accept()
	data = clientsocket.recv(RECV_BUFFER)
	if not data: 
		break
	print("%s" % str(data))
	clientsocket.close()
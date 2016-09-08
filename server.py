import socket
import sys
import select
import utils

#get stdin args
args = sys.argv

if len(args) != 2:
	print "Please supply a port."
	sys.exit()

#constants
RECV_BUFFER = 200
HOST = "localhost"
PORT = args[1]
SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#global variables
socket_channels = {} # mapping of channel to sockets
socket_list = {} # mapping of socket to string username



#bind to the port
SERVER_SOCKET.bind((HOST,int(float(PORT))))

#start listening
SERVER_SOCKET.listen(5)

#add SERVER_SOCKET into list of readable connections
socket_list.update({SERVER_SOCKET: "server"})


#broadcast messages to all connected clients in list
def broadcast(currsock, msg):
	for sock in socket_list:
		if sock != SERVER_SOCKET and sock != currsock:
			try:
				# server sends this sock this message
				sock.send(msg) 
			except:
				# exception has occured. broken socket
				sock.close()
				del socket_list[sock]

#start the server
while True:
    # get the list sockets which are ready to be read, written to, or exceptional condition
	rlist,wlist,xlist = select.select(socket_list,[],[])

	for s in rlist:
		# new connections
		if s == SERVER_SOCKET:
			clientsocket,addr = SERVER_SOCKET.accept()
			clientname = clientsocket.recv(RECV_BUFFER)
			socket_list.update({clientsocket: clientname})
			broadcast(clientsocket, utils.SERVER_CLIENT_JOINED_CHANNEL.format(str(clientname)) + "\n")
		else:
			# receive data from exisiting connections
			data = s.recv(RECV_BUFFER)
			if data:
				#something in the socket
				broadcast(s, "[" + str(socket_list[s]) + "] " + data)
			else:
				#broken socket. remove the client
				broadcast(s, utils.SERVER_CLIENT_LEFT_CHANNEL.format(socket_list[s]) + "\n") 
				if s in socket_list:
					del socket_list[s]



#shutdown server
SERVER_SOCKET.close()

# add to dicitonary
# todo: how od you exit the chat room?
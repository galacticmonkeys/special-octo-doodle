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
HOST = "localhost"
PORT = args[1]
SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#global variables
channels_list = {} # mapping of channels to sockets
socket_list = {} # mapping of socket to string username
incompete_msgs = {} #mapping of socket to incomplete messages

#bind to the port
SERVER_SOCKET.bind((HOST,int(float(PORT))))

#start listening
SERVER_SOCKET.listen(5)

#add SERVER_SOCKET into list of readable connections
socket_list.update({SERVER_SOCKET: "server"})

def pad_message(message):
	return message.ljust(200, 'a')


# checks if socket is in an existing channel. 
# if it exists, it will return the first channel name where its contained
# a sock can only be in 1 channel at a time so we don't specifiy where it should search
def in_channel(sock):
	for key, value in channels_list.items():
		if sock in value:
			return key
	return False

# remove a socket from is channel. if socket isn't in any channel, then nothing happens
# we don't need a channel argument because we'll just traverse all channels
# since a socket can only be in 1 channel at a time
def remove_from_channel(sock):
	for value in channels_list.itervalues():
		if sock in value:
			value.remove(sock)
			break

#broadcast messages to all connected clients in current channel except the current socket
def broadcast(currsock, msg):
    # if socket not in any channel, don't broadcast anything
    if (not in_channel(currsock)):
        return
    curr_channel = in_channel(currsock)
    for sock in channels_list[curr_channel]:
        if sock != SERVER_SOCKET and sock != currsock:
            try:
                # server sends this sock this message, stripping off whitespace
                sock.sendall(pad_message(msg))
            except:
                # exception has occured. broken socket
                sock.close()
                remove_from_channel(sock)
                if sock in socket_list:
                    del socket_list[sock]

# removes socket from existing channel and adds it to the new channel
# def move_socket(sock, channel):


#handles commands. assumes strings received with "/"
def command_handler(currsock, message):
	command = message.split()[0]
	if (command == "/list"):
		tosend = ""
		for key in channels_list.iterkeys():
			tosend += key + "\n"
		currsock.send(tosend.rstrip("\n"))
		#print(channels_list)
	elif (command == "/join"):
		if len(message.split()) > 1:
			channel_name = message.split()[1]
			# check to see channel exists
			if channel_name in channels_list:
				#tell everyone you're checking out
				broadcast(currsock, utils.SERVER_CLIENT_LEFT_CHANNEL.format(str(socket_list[currsock])))
				#checkout
				remove_from_channel(currsock)
				#move to new channel
				channels_list[channel_name].append(currsock)
				#say hi to everyone in the new channel
				broadcast(currsock, utils.SERVER_CLIENT_JOINED_CHANNEL.format(str(socket_list[currsock])))
			else:
				#channel doesn't exist
				currsock.sendall(utils.SERVER_NO_CHANNEL_EXISTS.format(channel_name))
		else:
			#not enough arguments
			currsock.sendall(utils.SERVER_JOIN_REQUIRES_ARGUMENT)
		#print(channels_list)
	elif (command == "/create"):
		if len(message.split()) > 1:
			channel_name = message.split()[1]
			# check to see first channel doesn't already exist
			if not channel_name in channels_list:
				#tell everyone you're checking out
				broadcast(currsock, utils.SERVER_CLIENT_LEFT_CHANNEL.format(str(socket_list[currsock])))
				#checkout
				remove_from_channel(currsock)
				# create the channel, and add currsock into it
				channels_list.update({channel_name:[currsock]})
				#say hi to everyone
				broadcast(currsock, utils.SERVER_CLIENT_JOINED_CHANNEL.format(str(socket_list[currsock])))
			else:
				#Error: channel already exists.
				currsock.sendall(utils.SERVER_CHANNEL_EXISTS.format(channel_name))
		else:
			#not enough arguments
			currsock.sendall(utils.SERVER_CREATE_REQUIRES_ARGUMENT)
		#print(channels_list)
	else:
		currsock.sendall(utils.SERVER_INVALID_CONTROL_MESSAGE.format(command))

#start the server
while True:
    # get the list sockets which are ready to be read, written to, or exceptional condition
	rlist,wlist,xlist = select.select(socket_list,[],[])

	for s in rlist:
		# new connections
		if s == SERVER_SOCKET:
			clientsocket,addr = SERVER_SOCKET.accept()
			clientname = clientsocket.recv(200) #take me out of here
			incompete_msgs.update({clientsocket: ""})
			socket_list.update({clientsocket: clientname.rstrip('a')}) #take me out of here
		else:
			# receive data from exisiting connections
			data = s.recv(200)
			data = data.rstrip('a')
			if data:
				#something in the socket

				#handles commands
				if (str(data)[0] == "/"):
					command_handler(s, data)
				# check to make sure the socket belongs to a channel
				elif not in_channel(s):
					s.sendall(utils.SERVER_CLIENT_NOT_IN_CHANNEL)
				else:
					broadcast(s, "[" + str(socket_list[s]) + "] " + data)
			else:
				#broken socket. remove the client
				broadcast(s, utils.SERVER_CLIENT_LEFT_CHANNEL.format(socket_list[s]))
				remove_from_channel(s)
				if s in socket_list:
					del socket_list[s]
				s.close()

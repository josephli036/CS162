import sys
import socket
import select
import utils
import traceback

PORT = 0
SOCKET_LIST = []

# Maps channel name to list of sockets in the channel
channels = {'home':[]}
# Maps socket to its message buffer
message_buffer = {}

# Mapping from socket to (name, channel name)
socket_info = {}

initiated = []

def join_channel(message, server_socket, client_socket):
    if len(message) < 2:
        single_client_message(utils.SERVER_JOIN_REQUIRES_ARGUMENT.format(message[1]), client_socket)
    elif message[1] not in channels or message[1] == 'home':
        single_client_message(utils.SERVER_NO_CHANNEL_EXISTS.format(message[1]), client_socket)
    else:
        client = socket_info[client_socket]
        channel_broadcast(utils.SERVER_CLIENT_LEFT_CHANNEL.format(client[0]), server_socket, client_socket)
        channels[client[1]].remove(client_socket)
        channels[message[1]].append(client_socket)
        socket_info[client_socket] = (client[0], message[1])
        channel_broadcast(utils.SERVER_CLIENT_JOINED_CHANNEL.format(client[0]), server_socket, client_socket)

def list_channel(message, server_socket, client_socket):
    channel = socket_info[client_socket][1]
    for channel in channels:
        if channel != 'home':
            single_client_message(channel, client_socket)

def create_channel(message, server_socket, client_socket):
    if len(message) < 2:
        single_client_message(utils.SERVER_CREATE_REQUIRES_ARGUMENT.format(message[1]), client_socket)
    elif message[1] in channels:
        single_client_message(utils.SERVER_CHANNEL_EXISTS.format(message[1]), client_socket)
    else:
        client = socket_info[client_socket]
        if client[1] != 'home':
            channel_broadcast(utils.SERVER_CLIENT_LEFT_CHANNEL.format(client[0]), server_socket, client_socket)
        channels[client[1]].remove(client_socket)
        channels[message[1]] = [client_socket]
        socket_info[client_socket] = (client[0], message[1])

commands = {'/join': join_channel, '/list': list_channel, '/create': create_channel}

def process_message(message, server_socket, client_socket):
    if client_socket in message_buffer:
        message_buffer[client_socket] += message
    else:
        message_buffer[client_socket] = message
    if len(message_buffer[client_socket]) >= utils.MESSAGE_LENGTH:
        output = message_buffer[client_socket][:utils.MESSAGE_LENGTH]
        if len(message_buffer[client_socket]) == utils.MESSAGE_LENGTH:
            message_buffer.pop(client_socket)
        else:
            message_buffer[client_socket] = message_buffer[client_socket][utils.MESSAGE_LENGTH:]
        if client_socket not in initiated:
            initiated.append(client_socket)
            socket_info[client_socket] = (output.rstrip(), 'home')
            return
        if output[0] == '/':
            command = output.rstrip().split()
            try:
                commands[command[0]](command, server_socket, client_socket)
            except Exception, e:
                single_client_message(utils.SERVER_INVALID_CONTROL_MESSAGE.format(command[0]), client_socket)
                traceback.print_exc()
        else:
            client_channel = socket_info[client_socket][1]
            if client_channel == 'home':
                single_client_message(utils.SERVER_CLIENT_NOT_IN_CHANNEL, client_socket)
            else:
                channel_broadcast('[' + socket_info[client_socket][0] + '] ' + output, server_socket, client_socket)

def single_client_message(message, client_socket):
    message += '' * (200 - len(message))
    client_socket.send(message)

def channel_broadcast(message, server_socket, client_socket):
    message = message.rstrip()
    client_channel = socket_info[client_socket][1]
    for s in SOCKET_LIST:
        if s != server_socket and s != client_socket and s in channels[client_channel]:
            message += '' * (utils.MESSAGE_LENGTH - len(message))
            s.send(message)

def server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', PORT)) 
    server_socket.listen(10)

    SOCKET_LIST.append(server_socket)
 
    while 1:

        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[])
      
        for sock in ready_to_read:
            # client message recieved
            if sock != server_socket:
                try:
                    client_channel = socket_info[sock][1]
                    message = sock.recv(4096)
                    if message:
                        process_message(message, server_socket, sock)
                    else:
                        SOCKET_LIST.remove(sock)
                        channels[client_channel].remove(sock)
                        channel_broadcast(utils.SERVER_CLIENT_LEFT_CHANNEL.format(socket_info[sock][0]), server_socket, sock)
                        initiated.remove(socket)
                except Exception, e:
                    SOCKET_LIST.remove(sock)
                    channels[client_channel].remove(sock)
                    channel_broadcast(utils.SERVER_CLIENT_LEFT_CHANNEL.format(socket_info[sock][0]), server_socket, sock)
                    initiated.remove(socket)

                    traceback.print_exc()
            # a new connection request recieved
            elif sock == server_socket: 
                new_socket, addr = server_socket.accept()
                SOCKET_LIST.append(new_socket)
                name = new_socket.recv(4096)
                process_message(name, server_socket, new_socket)
                socket_info[new_socket] = ('', 'home')
                channels['home'].append(new_socket)
 
if __name__ == "__main__":

    PORT = int(sys.argv[1])
    sys.exit(server()) 
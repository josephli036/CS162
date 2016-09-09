# chat_client.py

import sys
import socket
import select
import utils
 
def chat_client():
    if(len(sys.argv) < 3) :
        print 'Usage : python chat_client.py hostname port'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = socket.socket()
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print sys.stdout.write(utils.CLIENT_CANNOT_CONNECT.format(host, port))
        sys.exit()
     
    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush()
     
    while 1:
        socket_list = [s, sys.stdin]
         
        ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
         
        for sock in ready_to_read:             
            if sock == s:
                message = sock.recv(4096)
                if not mesaage :
                    print '\r' + utils.CLIENT_SERVER_DISCONNECTED.format(host, port)
                    sys.exit()
                else:
                    sys.stdout.write('/r' + message)
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX);
                    sys.stdout.flush()     
            else:
                # user entered a message
                msg = sys.stdin.readline()
                msg += ' ' * (200 - len(msg))
                s.send(msg)
                sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX);
                sys.stdout.flush()

if __name__ == "__main__":

    sys.exit(chat_client())
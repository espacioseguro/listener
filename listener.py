#git pull https://rogger.aburto@gmail.com:Rj451300@gitlab.com/r1305/listener.git
# import socket
# import sys
# import urllib
# import urllib2

# # Create a TCP/IP socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # Bind the socket to the port
# server_address = ('192.168.1.100', 97)
# print >>sys.stderr, 'starting up on %s port %s' % server_address
# sock.bind(server_address)
# # Listen for incoming connections
# sock.listen(100)


# while True:
#     # Wait for a connection
#     print >>sys.stderr, 'waiting for a connection'
#     connection, client_address = sock.accept()
#     try:
#         print >>sys.stderr, 'connection from', client_address

#         # Receive the data in small chunks and retransmit it
#         while True:
#             data = connection.recv(1024)
#             #urllib.request.urlopen('https://www.espacioseguro.pe/php_connection/47.php?data='+data)
#             data_alarm=urllib.quote(data)
#             urllib2.urlopen('https://www.espacioseguro.pe/php_connection/cambiarEstado.php?data='+data_alarm)
#             print >>sys.stderr, 'received "%s"' % data
#             if data:
#                 print >>sys.stderr, 'sending data back to the client'
#                 connection.sendall(data)
#             else:
#                 print >>sys.stderr, 'no more data from', client_address
#                 break                
#     finally:
#         # Clean up the connection
#         connection.close()

import select, socket, sys, Queue
import urllib
import urllib2
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind(('192.168.1.100', 97))
server.listen(100)
inputs = [server]
outputs = []
message_queues = {}
try:
    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is server:
                connection, client_address = s.accept()
                connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = Queue.Queue()
            else:
                data = s.recv(1024)
                if data:
                    message_queues[s].put(data)
                    if s not in outputs:
                        outputs.append(s)
                        data_alarm=urllib.quote(data)
                        urllib2.urlopen('https://www.espacioseguro.pe/php_connection/cambiarEstado.php?data='+data_alarm)
                        print >>sys.stderr, 'received "%s"' % data
                        if data:
                            print >>sys.stderr, 'sending data back to the client'
                            connection.sendall(data)
                        else:
                            print >>sys.stderr, 'no more data from', client_address
                            break 
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del message_queues[s]

        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except Queue.Empty:
                outputs.remove(s)
            else:
                s.send(next_msg)

        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]

except socket.timeout as err:
    logging.error(err)

except socket.error as err:
    logging.error(err)
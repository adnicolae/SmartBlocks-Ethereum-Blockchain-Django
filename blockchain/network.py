import os
import socket
import selectors
import time

'''
127.0.0.1 used for both addresses in order to test using a single
machine (replace with actual IP addresses - has been tested using
local IP addresses when running on two different computers on the
same network)

e.g. ADDRESS = '192.168.0.20', PEER_ADDRESS = '192.168.0.52' on
     one machine
     ADDRESS = '192.168.0.52', PEER_ADDRESS = '192.168.0.20' on
     second machine
'''
# the IP address of the current node (your IP)
ADDRESS = '127.0.0.1'
# the IP address of a peer you wish to connect to
PEER_ADDRESS = '127.0.0.1'
# the port used for the connection
PORT = 65432 
# variable used to store received data
data = b''
# variable used to indicate if data can be sent
can_send = True
# variable used to indicate if data can be received
can_receive = True

# selectors module used for I/O multiplexing
# necessary to deal with multiple connections at the same time
sel = selectors.DefaultSelector()

# create a socket object (address family = IPv4, type = TCP)
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to IP address and port
listen_socket.bind((ADDRESS, PORT))
# listen for connections and ensure socket is non-blocking (so
# that listen doesn't block and wait for a connection)
listen_socket.listen()
listen_socket.setblocking(False)
# register listening socket to monitor read events
sel.register(listen_socket, selectors.EVENT_READ, 'accept')

def accept_connection(sckt, can_receive):
    '''
    creates a connection when the listening socket is
    ready to accept a connection (this connection is used
    to receive data from node that is connecting)

    sckt: listening socket
    can_receive: set to False after connection is accepted
                 so that data can only be received from one
                 node at a time
    '''

    accepted = sckt.accept()
    # connection is a new socket object for the connection
    # make connection non-blocking and register socket to 
    # monitor read events
    connection = accepted[0]
    connection.setblocking(False)
    sel.register(connection, selectors.EVENT_READ, 'read')
    can_receive = False

def connect_socket(host, port, can_send):
    '''
    connects to a listening socket at the given address in order
    to send data to the node at this address

    host: host IP address of the node to connect to
    port: port used for the connection (65432)
    can_send: set to False after connecting to ensure that data can
              only be sent to a node at a time
    '''

    # create a socket object and connect to the address
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.setblocking(False)
    sckt.connect_ex((host, port))
    print('Connecting to Peer with Address', host, ' on Port', port)
    # after connecting set can_send to False and register the socket
    # to monitor write events
    can_send = False
    sel.register(sckt, selectors.EVENT_WRITE, 'send')

def read_data(sckt, data, can_receive):
    '''
    receive data from connection created by accept_connection() 
    function

    sckt: socket object for the connection
    data: variable used to keep track of received data
    can_receive: once all data has been received, set to True
                 so that a new connection can be created
    '''

    # receive data
    received = sckt.recv(1024)
    if received:
        # append received data to data variable
        data += received
        print('Received Data')
    else:
        # if no data is received, reset data variable, set can_receive
        # to True so that a new connection can be created, unregister the
        # connection socket object for monitoring and close the connection
        # socket.
        print(data)
        data = b''
        can_receive = True
        sel.unregister(sckt)
        sckt.close()
    return data

def send_data(sckt, can_send):
    '''
    send data to address connected to using socket object

    sckt: socket object created in connect_socket() function
          used for the connection
    can_send: after data has been sent, set to True so that a new
              connection can be created
    '''

    # try to send all the data
    try:
        sckt.sendall(b'Hello World')
    except BrokenPipeError:
        print('Cannot send data: BrokenPipeError')
    except ConnectionRefusedError:
        print('Cannot send data: ConnectionRefusedError')
    except ConnectionResetError:
        print('Cannot send data: ConnectionResetError')
    # if data is sent successfully, set can_send to true
    else:
        print('Data has been sent')
        can_send = True
    # ensure socket is unregistered for monitoring and closed if data
    # is sent successfully or if there is an issue with the connection
    finally:
        sel.unregister(sckt)
        sckt.close()


while True:
    # wait until a monitored event becomes ready
    events = sel.select(timeout = 1)
    for key, mask in events:
        # listening socket can accept a connection and can_receive is
        # true, call accept_connection(). key.fileobject gives the
        # socket object
        if key.data == 'accept' and can_receive:
            accept_connection(key.fileobj, can_receive)
        # if connection socket is ready to read data call the 
        # read_data() function
        elif key.data == 'read':
            data = read_data(key.fileobj, data, can_receive)
        # if outgoing connection is ready to write/send data,
        # call the send_data function
        elif key.data == 'send':
            send_data(key.fileobj, can_send)
    # if can_send is true, attempt to create a connection with a
    # given node
    if can_send:
        time.sleep(1)
        connect_socket(PEER_ADDRESS, PORT, can_send)

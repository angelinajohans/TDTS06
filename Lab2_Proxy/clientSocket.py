import socket

#A class, as initialized creates a client socket which will be doing messag forwarding to and receiving from webserver.
#Will only be created if the url of the request does not contain any forbidden words.
class clientSocket:

    #Creates a socket and connects it to the input argument webpage (host) on a given port (80)
    def __init__(self, webpage):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Client socket created')
        print('Trying to connect to',webpage)                
        self.sock.connect((webpage,80))
        print('Server socket connects to',webpage,'on port 80')
            

    #Forwards the request from server side to the webserver and
    #receives the response message from the webserver.
    #The received response is returned
    def forward_request(self, request):
        recv_msg = [b'']
        send_msg_size = 0
        sent_msg_size = 0
        print('Entered forward_request')
        request_to_send = request.encode('utf=8', errors='strict')
        send_msg_size = len(request_to_send)
        print('This is the send_msg_size:',send_msg_size)
        print('This is the sent_msg_size:',sent_msg_size)
        print('This is the type of the request to be sent:',type(request_to_send))
        while sent_msg_size < send_msg_size:
            sent_msg = self.sock.send(request_to_send[sent_msg_size:])
            print('This is the sent_msg:',sent_msg)
            print('This is the type of the returned value when send message:',type(sent_msg))
            sent_msg_size = sent_msg_size + sent_msg
            print('This is the sent_msg_size:',sent_msg_size,'after the plus operation')
        print('\nRequest to the webserver has been sent\n',request_to_send)
        recv_part_msg = self.sock.recv(4096)
        while recv_part_msg != b'':
            recv_msg[0] = recv_msg[0]+recv_part_msg
            recv_part_msg = self.sock.recv(4096)
        print('\nA response message has been received:\n',recv_msg[0])
        return recv_msg[0]

    #Closes the client socket
    def close_socket(self):
        print('About to close client socket')
        self.sock.close()
        print('Client socket is closed')
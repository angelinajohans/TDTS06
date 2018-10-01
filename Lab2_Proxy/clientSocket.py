import socket

#A class, as initialized creates a client socket which will be doing messag forwarding to and receiving from webserver.
#Will only be created if the url of the request does not contain any forbidden words.
class clientSocket:

    #Creates a socket and connects it to the input argument webpage (host) on a given port (80)
    def __init__(self, webpage):
        #webpage = webpage[:len(webpage)-1]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Client socket created")
        print("Trying to connect to",webpage)                
        #try:
        self.sock.connect((webpage,80))
        print("Server socket connects to",webpage,"on port 80")
        #except socket.gaierror:
        #    print("The socket could not be properly connected!")
            

    #Forwards the request from server side to the webserver and
    #receives the response message from the webserver.
    #The received response is returned
    def forward_request(self, request):
        print("Entered forward_request")
        request_to_send = request.encode("utf=8", errors="strict")
        print(type(request_to_send))
        self.sock.send(request_to_send)
        print("Request to the webserver has been sent\n",request_to_send)
        webserver_msg = self.sock.recv(4096)
        print("A response message has been received")
        return webserver_msg

    #Closes the client socket
    def close_socket(self):
        print("About to close client socket")
        self.sock.close()
        print("Client socket is closed")
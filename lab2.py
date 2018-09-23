import socket
import threading
import re

class clientSocket:

    def __init__(self, webpage):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Client socket created")
        print("Trying to connect to",webpage)
        print(type(webpage))
        self.sock.connect((webpage, 80))
        print("Server socket connects to", webpage, "on port 80")

    def forward_request(self, request):
        print("Entered forward_request")
        request_to_send = request.encode("utf=8", errors="strict")
        print(type(request_to_send))
        self.sock.send(request_to_send)
        webserver_msg = self.sock.recv(4000)
        return webserver_msg

    def close_socket(self):
        self.sock.close()

class serverSocket:
    
    def __init__(self, port_server):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Server socket created")
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', port_server))
        print(socket.gethostname())
        print("Socket is bound to port",port_server)
        self.sock.listen(10)
        print("Server is listening")

    def hear_client(self):
        (incommingSocket, incommingAddress) = self.sock.accept()
        print("Connection established")
        new_thread_id = threading.Thread(target=self.recv_from_client, args=[incommingSocket])
        print("New thread created")
        print(new_thread_id)
        new_thread_id.start()

    def handle_request(self, incommingSocket, request, webpage):
        print("Want to create client socket and connect to",webpage[0])
        clientSock = clientSocket(webpage[0])
        print(clientSock)
        print(type(request))
        webserver_msg = clientSock.forward_request(request)
        incommingSocket.send(webserver_msg)
        clientSocket.close_socket()

    def recv_from_client(self, incommingSocket):
        bytes_request = incommingSocket.recv(4000)
        print(type(bytes_request))
        string_request = bytes_request.decode(encoding="utf-8", errors="strict")
        print('Original string:', string_request)
        url_of_page = re.findall('Host:(.+)', bytes_request.decode('utf-8'))
        new_request = re.sub('https?:\/+\/.+ ', '/ ', string_request)
        new_request_to_send = re.sub('[Pp]roxy.[Cc]onnection:.+','Connection: close\r', new_request)
        #divide_msg = re.search('Proxy(.+)', new_request)
        #req_no_connKeepAlive = new_request[:divide_msg.start()] + new_request[divide_msg.end():]
        #new_ready_to_send = re.sub('\n\n', '\n', req_no_connKeepAlive)
        print('The url of the page:',url_of_page[0])
        print('New request1\n',new_request)
        #print('Request without Connection: Keep-Alive \n',req_no_connKeepAlive)
        print('Request with no Keel-Alive and one new line \n',new_request_to_send)
        self.handle_request(incommingSocket, new_request_to_send, url_of_page)



# Don't know if this will ever be used...
    def close_socket(self):
        self.sock.close()

    
def main():
    serverSock = serverSocket(8080)
    while 1:
        serverSock.hear_client()


if __name__ == "__main__":
    main()

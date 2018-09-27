import socket
import threading
import re
import codecs
import sys

class uglyWordsFinder:

    def need_to_investigate(self, request): #or just url?
        print("In the need_to_investigate function")
        pic_formats = ["tif","tiff","bmp","jpg","jpeg","gif","png","eps"]
        for i in pic_formats:
            exist = request.find(i)
            if exist != -1:
                print("The object does not need to be investigated")
                return False
            else:
                print("The object needs to be investigated")
                return True
        
    def acceptable(self, obj_of_interest):
        forbidden_words = ["[Bb]ritney ?[Ss]pears", "[Pp]aris ?[Hh]ilton", "[Ll]inkoping", "[Ss]ponge[Bb]ob"]
        if self.need_to_investigate(obj_of_interest):
            for i in forbidden_words:
                found_words = re.findall(i,obj_of_interest)
                if found_words != []:
                    print("The object is dirty")
                    print("This is what the function searched through:\n",obj_of_interest)
                    return False
                else:
                    continue
            print("The object is clean")
            print("This is what the function searched through:\n",obj_of_interest)
            return True
        else:
            print("The object is clean")
            print("This is what the function searched through:\n",obj_of_interest)
            return True
            
class clientSocket:

    def __init__(self, webpage):
        #webpage = webpage[:len(webpage)-1]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Client socket created")
        print("Trying to connect to",webpage)                
        self.sock.connect((webpage,80))
        print("Server socket connects to",webpage,"on port 80")

    def forward_request(self, request):
        print("Entered forward_request")
        request_to_send = request.encode("utf=8", errors="strict")
        print(type(request_to_send))
        self.sock.send(request_to_send)
        print("Request to the webserver has been sent")
        webserver_msg = self.sock.recv(4096)
        print("A response message has been received")
        return webserver_msg

    def close_socket(self):
        print("About to close client socket")
        self.sock.close()
        print("Client socket is closed")

class serverSocket:

    badUrl_url = "www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html"
    badContent_url = "www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html"
    
    def __init__(self, port_server):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Server socket created")
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', port_server))
        print(socket.gethostname())
        print("Socket is bound to port",port_server)
        self.sock.listen(10)
        print("Server is listening")
        self.checker = uglyWordsFinder()

    def redirect(self, new_url):
        redirection_response = "HTTP/1.1 302 Found\r\nLocation: http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html\r\nConnection: close\r\n"
        print("This is the redirection response",redirection_response)
        redirection_to_send = redirection_response.encode("utf=8", errors="strict")
        return redirection_to_send
        

    def hear_client(self):
        (incommingSocket, incommingAddress) = self.sock.accept()
        print("Connection established")
        new_thread_id = threading.Thread(target=self.recv_from_client, args=[incommingSocket])
        print("New thread created")
        print(new_thread_id)
        new_thread_id.start()

    def handle_request(self, incommingSocket, request, url):
        print("Want to create client socket and connect to",url)
        clientSock = clientSocket(url)
        print(clientSock)
        print(type(request))
        response = clientSock.forward_request(request)
        print("The size of the response is",sys.getsizeof(response))
        print("Response is received\n",response)
        data_position = response.find(b'\r\n\r\n')
        response_header = response[:data_position+2]
        response_data = response[data_position+4:]
        print(response_header,"\n\n")
        print(response_data)
        string_data = codecs.encode(response_data,'hex')
        print("This is the response data, when hex encoder has been applied", string_data)
        one_more_encoding = codecs.encode(string_data, 'hex')
        string_data_response = one_more_encoding.decode(encoding="utf-8", errors="strict")
        if self.checker.acceptable(string_data_response):
            print("The webserver message is:\n",string_data_response)
            incommingSocket.send(response)
            print("The webserver response has been forwarded to the client")
            clientSock.close_socket()
        else:
            print("Bad content")
            redirect_response = self.redirect(self.badContent_url)
            incommingSocket.send(redirect_response)
            print("The webserver response was dirty, the client has been redirected")
            clientSock.close_socket()

    def recv_from_client(self, incommingSocket):
        bytes_request = incommingSocket.recv(4096)
        print(type(bytes_request))
        string_request = bytes_request.decode(encoding="utf-8", errors="strict")
        print('Original string:',string_request)
        if self.checker.acceptable(string_request):
            if string_request.find('http://') != -1:
                print("http in first line")
                url_of_page = re.findall('https?:\/+\/.+?(?=\/)',string_request)
                print('Found url',url_of_page[0])
                url_no_http = re.sub('(https?:\/\/)','',url_of_page[0])
                print('Removed http',url_no_http)
            else:   
                url_no_http = re.findall('Host: (.+)',bytes_request.decode('utf-8'))
        
            new_request = re.sub('https?:\/+\/.+?(?=\/)','',string_request)
            new_request_to_send = re.sub('[Pp]roxy.[Cc]onnection:.+','Connection: close\r',new_request)
            #divide_msg = re.search('Proxy(.+)', new_request)
            #req_no_connKeepAlive = new_request[:divide_msg.start()] + new_request[divide_msg.end():]
            #new_ready_to_send = re.sub('\n\n', '\n', req_no_connKeepAlive)
            print('The url of the page:',url_no_http)
            #print('New request1\n',new_request)
            #print('Request without Connection: Keep-Alive \n',req_no_connKeepAlive)
            print('Request with no Keel-Alive and one new line \n',new_request_to_send)
            self.handle_request(incommingSocket, new_request_to_send, url_no_http)

        else:
            print("Bad url!")
            redirect_response = self.redirect(self.badUrl_url)
            incommingSocket.send(redirect_response)
            print("The url was dirty, the client ha been redirected")


# Don't know if this will ever be used...
    def close_socket(self):
        print("About to close server socket")
        self.sock.close()

    
def main():
    serverSock = serverSocket(8080)
    while 1:
        serverSock.hear_client()


if __name__ == "__main__":
    main()

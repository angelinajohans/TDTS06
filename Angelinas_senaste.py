import socket
import threading
import re

class uglyWordsFinder:

    def need_to_investigate(self, request): #or just url?
        pic_formats = ["tif","tiff","bmp","jpg","jpeg","gif","png","eps"]
        for i in pic_formats:
            exist = 1 #request.find(i)
            if exist == 1:
                return False
            else:
                return True
        
    def acceptable(self, obj_of_interest):
        forbidden_words = ["[Bb]ritney ?[Ss]pears", "[Pp]aris ?[Hh]ilton", "[Ll]inkoping", "[Ss]ponge[Bb]ob"]
        if self.need_to_investigate(obj_of_interest):
            for i in forbidden_words:
                found_words = [1]#re.findall(i,obj_of_interest)
                if found_words != []:
                    return False
                else:
                    continue
            return True
        else:
            return True
            
class clientSocket:

    def __init__(self, webpage):
        str(webpage)
        webpage.strip('\n')
        webpage.strip(' ')
        webpage.strip('\r')
        webpage.strip('\t')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Client socket created")
        print("Trying to connect to",webpage)
        print(type(webpage))
        webpage_test = "www.overleaf.com"
        webpage_test.strip('\n')
        webpage_test.strip(' ')
        webpage_test.strip('\r')
        
        iter_vec = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]

        print("Length of webpage",len(webpage))
        print("Length of webpage_test",len(webpage_test))
        
        if webpage == webpage_test:
            print("THE STRINGS ARE EQUAL!")
        else:
            print("THE STRINGS ARE NOT EQUAL... HELP!")
        for i in iter_vec:
            if webpage[:i] == webpage_test[:i]:
                print("THE LETTERS ARE EQUAL!")
                print(webpage[:i],"=",webpage_test[:i])
            else:
                print("THE LETTERS ARE NOT EQUAL AND I DO NOT KNOW WHAT TO DO!")
                print(webpage[:i],"≠",webpage_test[:i])
                
        self.sock.connect((webpage,80))
        print("Server socket connects to",webpage,"on port 80")

    def forward_request(self, request):
        print("Entered forward_request")
        request_to_send = request.encode("utf=8", errors="strict")
        print(type(request_to_send))
        self.sock.send(request_to_send)
        webserver_msg = self.sock.recv(4000)
        return webserver_msg

    def close_socket(self):
        print("About to close client socket")
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

    def redirect(self, new_url):
        redirection_response = "HTTP/1.1 302 Found\r\nLocation: " + new_url + "\r\nContent-Type: "
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
        print("Want to create client socket and connect to",url[0])
        checker = uglyWordsFinder()
        if checker.acceptable(url):
            clientSock = clientSocket(url[0])
            print(clientSock)
            print(type(request))
            response = clientSock.forward_request(request)
            string_response = response.decode(encoding="utf-8", errors="strict")
            if checker.acceptable(string_response):
                print("The webserver message is:\n",string_response)
                incommingSocket.send(response)
                print("The webserver response has been forwarded to the client")
                clientSock.close_socket()
            else:
                print("Bad content")
                redirect_response = self.redirect(badContent_url)
                incommingSocket.send(redirect_response)
                print("The webserver response was dirty, the client has been redirected")
                clientSock.close_socket()
        else:
            print("Bad url!")
            redirect_response = self.redirect(badUrl_url)
            incommingSocket.send(redirect_response)
            print("The url was dirty, the client ha been redirected")
            clientSock.close_socket()

    def recv_from_client(self, incommingSocket):
        bytes_request = incommingSocket.recv(4000)
        print(type(bytes_request))
        string_request = bytes_request.decode(encoding="utf-8", errors="strict")
        print('Original string:',string_request)
        url_of_page = re.findall('Host: (.+)',bytes_request.decode('utf-8'))
        new_request = re.sub('https?:\/+\/.+ ','/ ',string_request)
        new_request_to_send = re.sub('[Pp]roxy.[Cc]onnection:.+','Connection: close\r',new_request)
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
        print("About to close server socket")
        self.sock.close()

    
def main():
    serverSock = serverSocket(8080)
    while 1:
        serverSock.hear_client()


if __name__ == "__main__":
    main()

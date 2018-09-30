import socket
import threading
import re
import codecs
import sys

#Contains the scanning/filtering functions
class uglyWordsFinder:
    
    #This function checks whether the input argument string contains an image 
    #and subsequently does not need to be investigated or does not contain an image
    #and should be investigated.
    #Contains image returs False
    #Does not contain image returns True
    def need_to_investigate(self, request): #or just url?
        print("In the need_to_investigate function")
        pic_formats = ["tif","tiff","bmp","jpg","jpeg","gif","png","eps"]
        
        #For every item in string list pic_formats
        #look for the format keyword in the input string
        for i in pic_formats:
            exist = request.find(i)
            
            #If the image format keyword is not found, continue with next keyword
            #else (if the keyeord is found) return True; needs to be investagated
            if exist != -1:
                print("The object does not need to be investigated")
                continue
            else:
                print("The object needs to be investigated")
                return True
        return False
        
    #This function check if the object of interest contains any forbidden words.
    #If contains fobidden words, it is unacceptable and returns False
    #If does not contain forbidden words, it is acceptable and returns True
    def acceptable(self, obj_of_interest):
        forbidden_words = ["[Bb]ritney ?[Ss]pears", "[Pp]aris ?[Hh]ilton", "[Ll]inkoping", "[Ss]ponge[Bb]ob"]
        
        #If the object of interest needs to be investigated
        #enter search for forbidden words
        #else (if no need for investigation) return True; acceptable
        if self.need_to_investigate(obj_of_interest):
            
            #For every item in forbidden words list look for the word in the object of interest.
            #If found return False; not acceptable, if not found continue with next.
            #If no words are found, return True; acceptable
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
        
#A class, as initialized creates a client socket which will be doing messag forwarding to and receiving from webserver.
#Will only be created if the url of the request does not contain any forbidden words.
class clientSocket:

    #Creates a socket and connects it to the input argument webpage (host) on a given port (80)
    def __init__(self, webpage):
        #webpage = webpage[:len(webpage)-1]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Client socket created")
        print("Trying to connect to",webpage)                
        self.sock.connect((webpage,80))
        print("Server socket connects to",webpage,"on port 80")

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

#A class, as initialized, creates and binds a server socket. When bound starts to listen for requests.
#As an object of this class i created an object of uglyWordsFindes class is also created.
class serverSocket:

    #Constat redirection urls
    badUrl_url = "http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html"
    badContent_url = "http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html"
    
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

    #Creates a redirection response using the input argument url.
    #Encodes the message into 'bytes' ready to be sent
    def redirect(self, new_url):
        redirection_response = "HTTP/1.1 302 Found\r\nLocation:" + new_url +"\r\nConnection: close\r\n\r\n"
        print("This is the redirection response\n",redirection_response)
        redirection_to_send = redirection_response.encode("utf=8", errors="strict")
        return redirection_to_send
    
    #Listens and accepts client requests
    #When a request is received a new thread takes over
    #the task and the original thread goes back to listening
    def hear_client(self):
        (incommingSocket, incommingAddress) = self.sock.accept()
        print("Connection established")
        new_thread_id = threading.Thread(target=self.recv_from_client, args=[incommingSocket])
        print("New thread created")
        print(new_thread_id)
        new_thread_id.start()
        #self.sock.listen(1)

    #Creates a client socket using the input argument url
    #Uses the client socket to send the request and receive
    #a response. Uses the in class global uglyWordsFinder word scan
    #to decide on what response to send to the client
    #Closes the client socket when done
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
        #string_data = codecs.encode(response_data,'hex')
        #print("This is the response data, when hex encoder has been applied", string_data)
        #one_more_encoding = codecs.encode(string_data, 'hex')
        string_data_response = response_data.decode(encoding="utf-8", errors="strict")
        
        #If the response does not contain forbidden words just forward the response.
        #If there are forbidden words use the redirect function.
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
            
    #Receives request from client and decodes the mesasge to a string
    #Uses the in class global uglyWordsFrider to scan the request for forbidden words
    #Modifies the request message and calls for the handle_request function 
    def recv_from_client(self, incommingSocket):
        bytes_request = incommingSocket.recv(4096)
        print(type(bytes_request))
        string_request = bytes_request.decode(encoding="utf-8", errors="strict")
        print('Original string:',string_request)
        
        #If the request does not contain any forbidden word(s) start modifying
        #If the request does contain forbidden word(s), uses the redirect function
        if self.checker.acceptable(string_request):
            
            #If there is a url with "http://", the whole url is in
            #the first line - not only the path the first line needs to be modified.
            #The http:// and host will be removed from first line and host identified.
            #If no "http://" is found the fist line does not need to be modefiend and the host is identified. 
            if string_request.find('http://') != -1:
                print("Http in first line")
                url_of_page = re.findall('http:\/+\/.+?(?=\/)',string_request)
                print('Found url',url_of_page[0])
                url_no_http = re.sub('(https?:\/\/)','',url_of_page[0])
                print('Removed http, the host is',url_no_http)
                #new_request = re.sub('http:\/+\/.+?(?=\/)','',string_request)
            else:   
                url_no_http = re.findall('Host: (.+)',bytes_request.decode('utf-8'))
        
            new_request = re.sub('http:\/+\/.+?(?=\/)','',string_request)
            
            #Modify the Connection-header
            new_request_to_send = re.sub('[Pp]roxy.[Cc]onnection:.+','Connection: close\r',new_request)
            #divide_msg = re.search('Proxy(.+)', new_request)
            #req_no_connKeepAlive = new_request[:divide_msg.start()] + new_request[divide_msg.end():]
            #new_ready_to_send = re.sub('\n\n', '\n', req_no_connKeepAlive)
            print('The url of the page:',url_no_http)
            #print('New request1\n',new_request)
            #print('Request without Connection: Keep-Alive \n',req_no_connKeepAlive)
            
            #Modify the Accept-Encoding-header
            new_request_to_send = re.sub('Accept-Encoding:(.+)\r\n', '', new_request_to_send)
            print('Request with no Keel-Alive and one new line \n',new_request_to_send)
            self.handle_request(incommingSocket, new_request_to_send, url_no_http)

        else:
            print("Bad url!")
            redirect_response = self.redirect(self.badUrl_url)
            incommingSocket.send(redirect_response)
            print("The url was dirty, the client has been redirected to\n",redirect_response)


# Don't know if this will ever be used...
    def close_socket(self):
        print("About to close server socket")
        self.sock.close()

#Creates a server socket using the by input desired port
#Starts the socket functionality     
def main():
    serverSock = serverSocket(8080)
    while 1:
        serverSock.hear_client()

#Runs the main function
if __name__ == "__main__":
    main()

import socket
import threading
import re
import codecs
import sys
from uglyWordsFinder import uglyWordsFinder
from clientSocket import clientSocket

#A class, as initialized, creates and binds a server socket. When bound starts to listen for requests.
#As an object of this class i created an object of uglyWordsFindes class is also created.
class serverSocket:

    #Constat redirection urls
    badUrl_url = 'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error1.html'
    badContent_url = 'http://www.ida.liu.se/~TDTS04/labs/2011/ass2/error2.html'
    
    def __init__(self, port_server):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Server socket created')
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', port_server))
        print('Socket is bound to port',port_server)
        self.sock.listen(10000)
        print('Server is listening')
        self.checker = uglyWordsFinder()

    #Creates a redirection response using the input argument url.
    #Encodes the message into 'bytes' ready to be sent
    def redirect(self, new_url):
        redirection_response = 'HTTP/1.1 302 Found\r\nLocation:' + new_url +'\r\nConnection: close\r\n\r\n'
        print('This is the redirection response\n',redirection_response)
        redirection_to_send = redirection_response.encode('utf=8', errors='strict')
        return redirection_to_send
    
    #Listens and accepts client requests
    #When a request is received a new thread takes over
    #the task and the original thread goes back to listening
    def hear_client(self):
        (incommingSocket, incommingAddress) = self.sock.accept()
        print('Connection established')
        new_thread_id = threading.Thread(target=self.recv_from_client, args=[incommingSocket])
        print('New thread created')
        new_thread_id.start()

    #Creates a client socket using the input argument url
    #Uses the client socket to send the request and receive
    #a response. Uses the in class global uglyWordsFinder word scan
    #to decide on what response to send to the client
    #Closes the client socket when done
    def handle_request(self, incommingSocket, request, url):
        
        send_msg_size = 0
        sent_msg_size = 0
        
        print('Want to create client socket and connect to',url)
        try:
            clientSock = clientSocket(url)
            
            print('The type of the request is:',type(request))
            response = clientSock.forward_request(request)
            print('\nThe size of the response is',sys.getsizeof(response))
            print('This is the type of the response:',type(response))
            print('Response is received\n',response)

            #If the response does not contain forbidden words just forward the response.
            #If there are forbidden words use the redirect function.
            data_position = response.find(b'\r\n\r\n')
            response_header = response[:data_position+2]
            response_data = response[data_position+4:]
            print('This is response_header:\n',response_header,'\n')
            print('This is response_data:\n',response_data,'\n')

            if self.checker.image(response_header.decode(encoding='utf-8', errors='strict')):
                print('The webserver message is:\n',response_header.decode(encoding='utf-8', errors='strict'))
                incommingSocket.send(response)
                print('The webserver response has been forwarded to the client')
                clientSock.close_socket()
            elif self.checker.acceptable_data(response_data.decode(encoding='utf-8', errors='strict')):
                incommingSocket.send(response)
                print('The webserver response has been forwarded to the client')
                clientSock.close_socket()
            else:
                print('Bad content!')
                redirect_response = self.redirect(self.badContent_url)
                incommingSocket.send(redirect_response)
                print('The webserver response was dirty, the client has been redirected')
                clientSock.close_socket()
            
            while sent_msg_size < send_msg_size:
                sent_msg = incommingSocket.send(response[sent_msg_size:])
                print('This is the sent_msg:',sent_msg)
                print('The type of the returned value when sending is:',type(sent_msg))
                sent_msg_size = sent_msg_size + sent_msg
                print('This is the sent_msg_size:',sent_msg_size,'after the plus operation')
            
            print('The webserver response has been forwarded to the client')
            clientSock.close_socket()

        except socket.gaierror:
            print('The socket could not be properly connected!')
            incommingSocket.send(b'HTTP/1.1 404 Not Found\r\n\r\n')
            
    #Receives request from client and decodes the mesasge to a string
    #Uses the in class global uglyWordsFrider to scan the request for forbidden words
    #Modifies the request message and calls for the handle_request function 
    def recv_from_client(self, incommingSocket):
        bytes_request = incommingSocket.recv(4096)

        print('The incoming request is of type:',type(bytes_request))
        string_request = bytes_request.decode(encoding='utf-8', errors='strict')
        print('Original string:\n',string_request)
        
        #If the request does not contain any forbidden word(s) start modifying
        #If the request does contain forbidden word(s), uses the redirect function
        if self.checker.acceptable_data(string_request):
            
            #If there is a url with 'http://', the whole url is in
            #the first line - not only the path the first line needs to be modified.
            #The http:// and host will be removed from first line and host identified.
            #If no 'http://' is found the fist line does not need to be modefiend and the host is identified. 
            if string_request.find('http://') != -1:
                print('Http in first line')
                url_from_first_line = re.findall('http:\/+\/(.+?)(?=\/)',string_request)
                url_no_http = url_from_first_line[0]
                string_request = re.sub('http:\/+\/.+?(?=\/)','',string_request)
            else:   
                url_from_host = re.findall('Host: (.+)',string_request)
                url_no_http = re.sub('\r','',url_from_host[0])
            
            #Modify the Connection-header
            new_request_to_send = re.sub('[Pp]roxy.[Cc]onnection:.+','Connection: close\r',string_request)
            print('The url of the page:',url_no_http)
            
            #Modify the Accept-Encoding-header
            new_request_to_send = re.sub('Accept-Encoding:(.+)\r\n', 'Accept-Encoding: \r\n', new_request_to_send)
            print('New modified request\n',new_request_to_send)
            self.handle_request(incommingSocket, new_request_to_send, url_no_http)

        else:
            print('Bad url!')
            redirect_response = self.redirect(self.badUrl_url)
            incommingSocket.send(redirect_response)
            print('The url was dirty, the client has been redirected to\n',redirect_response)


    # Don't know if this will ever be used...
    def close_socket(self):
        print('About to close server socket')
        self.sock.close()
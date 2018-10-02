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
        print'Server socket created'
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', port_server))
        print(socket.gethostname())
        print'Socket is bound to port',port_server
        self.sock.listen(1000)
        print'Server is listening'
        self.checker = uglyWordsFinder()

    #Creates a redirection response using the input argument url.
    #Encodes the message into 'bytes' ready to be sent
    def redirect(self, new_url):
        redirection_response = 'HTTP/1.1 302 Found\r\nLocation:' + new_url +'\r\nConnection: close\r\n\r\n'
        print'This is the redirection response\n',redirection_response
        redirection_to_send = redirection_response.encode('utf=8', errors='strict')
        return redirection_to_send
    
    #Listens and accepts client requests
    #When a request is received a new thread takes over
    #the task and the original thread goes back to listening
    def hear_client(self):
        (incommingSocket, incommingAddress) = self.sock.accept()
        print'Connection established'
        new_thread_id = threading.Thread(target=self.recv_from_client, args=[incommingSocket])
        print'New thread created'
        print(new_thread_id)
        new_thread_id.start()
        #self.sock.listen(1)

    #Creates a client socket using the input argument url
    #Uses the client socket to send the request and receive
    #a response. Uses the in class global uglyWordsFinder word scan
    #to decide on what response to send to the client
    #Closes the client socket when done
    def handle_request(self, incommingSocket, request, url):
        print'Want to create client socket and connect to',url
        try:
            clientSock = clientSocket(url)
            
            print(clientSock)
            print(type(request))
            response = clientSock.forward_request(request)
            print'The size of the response is',sys.getsizeof(response)
            print(type(response))
            print'Response is received\n',response
            data_position = response.find(b'\r\n\r\n')
            response_header = response[:data_position+2]
            response_data = response[data_position+4:]
            print'This is response_header:\n',response_header,'\n\n'
            print'This is response_data:\n',response_data
            #string_data = codecs.encode(response_data,'hex')
            #print('This is the response data, when hex encoder has been applied', string_data)
            #one_more_encoding = codecs.encode(string_data, 'hex')
            string_data_response = response_data.decode(encoding='utf-8', errors='strict')

            #If the response does not contain forbidden words just forward the response.
            #If there are forbidden words use the redirect function.
            if self.checker.acceptable(string_data_response):
                print'The webserver message is:\n',string_data_response
                incommingSocket.sendall(response)
                print'The webserver response has been forwarded to the client'
                clientSock.close_socket()
            else:
                print'Bad content'
                redirect_response = self.redirect(self.badContent_url)
                incommingSocket.sendall(redirect_response)
                print'The webserver response was dirty, the client has been redirected'
                clientSock.close_socket()

        except socket.gaierror:
            print'The socket could not be properly connected!'
            incommingSocket.sendall(b'HTTP/1.1 404 Not Found\r\n\r\n')
            
    #Receives request from client and decodes the mesasge to a string
    #Uses the in class global uglyWordsFrider to scan the request for forbidden words
    #Modifies the request message and calls for the handle_request function 
    def recv_from_client(self, incommingSocket):
        
        bytes_request = [b'']

        recv_part_req = incommingSocket.recv(4096)
        print'This is the revc_part_req:\n',recv_part_req
        while recv_part_req != 0:
            print'In the while loop of the request receiving function'
            bytes_request[0] = bytes_request[0]+recv_part_req
            print'The bytes_request has been appended:\n',bytes_request
            recv_part_req = incommingSocket.recv(4096)
            print'This is a new recv_part_req:\n',recv_part_req

        #bytes_request = incommingSocket.recv(4096)
        print(type(bytes_request))
        string_request = bytes_request.decode(encoding='utf-8', errors='strict')
        print'Original string:',string_request
        
        #If the request does not contain any forbidden word(s) start modifying
        #If the request does contain forbidden word(s), uses the redirect function
        if self.checker.acceptable(string_request):
            
            #If there is a url with 'http://', the whole url is in
            #the first line - not only the path the first line needs to be modified.
            #The http:// and host will be removed from first line and host identified.
            #If no 'http://' is found the fist line does not need to be modefiend and the host is identified. 
            if string_request.find('http://') != -1:
                print'Http in first line'
                url_from_first_line = re.findall('http:\/+\/(.+?)(?=\/)',string_request)
                url_no_http = url_from_first_line[0]
                print'Found url',url_no_http
                #url_no_http = re.sub('(https?:\/\/)','',url_of_page[0])
                #print('Removed http, the host is',url_no_http)
                string_request = re.sub('http:\/+\/.+?(?=\/)','',string_request)
            else:   
                url_from_host = re.findall('Host: (.+)',string_request)
                url_no_http = re.sub('\r','',url_from_host[0])
        
            #new_request = re.sub('http:\/+\/.+?(?=\/)','',string_request)
            
            #Modify the Connection-header
            new_request_to_send = re.sub('[Pp]roxy.[Cc]onnection:.+','Connection: close\r',string_request)
            #divide_msg = re.search('Proxy(.+)', new_request)
            #req_no_connKeepAlive = new_request[:divide_msg.start()] + new_request[divide_msg.end():]
            #new_ready_to_send = re.sub('\n\n', '\n', req_no_connKeepAlive)
            print'The url of the page:',url_no_http
            #print('New request1\n',new_request)
            #print('Request without Connection: Keep-Alive \n',req_no_connKeepAlive)
            
            #Modify the Accept-Encoding-header
            new_request_to_send = re.sub('Accept-Encoding:(.+)\r\n', 'Accept-Encoding: \r\n', new_request_to_send)
            print'Request with no Keel-Alive and one new line \n',new_request_to_send
            self.handle_request(incommingSocket, new_request_to_send, url_no_http)

        else:
            print'Bad url!'
            redirect_response = self.redirect(self.badUrl_url)
            incommingSocket.sendall(redirect_response)
            print'The url was dirty, the client has been redirected to\n',redirect_response


    # Don't know if this will ever be used...
    def close_socket(self):
        print'About to close server socket'
        self.sock.close()
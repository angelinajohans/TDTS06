import socket
import os

##serverPort = 8000
##webPage = "www.liu.se"
##
##serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##print("Server socket created:")
##print(serverSocket)
###serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
##serverSocket.bind((socket.gethostname(), serverPort))
##print("Server socket with hostname",socket.gethostname(),"is bound to",serverPort)
##serverSocket.listen(1)
##
##clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##print("Client socket is created:")
##print(clientSocket)
##clientSocket.connect((webPage, 80))
##print("Client socket is connected to",webPage)
##
##while 1:
##    (clientSocket, clientAddress) = serverSocket.accept()
##    print("Have received a connection from",clientSocket,",",clientAddress)
##    child = os.fork()
    
class serverSocket:

    def __init__(self, port_server):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Server socket is created")
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((socket.gethostname(), port_server))
        print("Socket is bound to",port_server)
        self.sock.listen(10)


def main():
    servsock = serverSocket(8000)


if __name__ == "__main__":
    main()
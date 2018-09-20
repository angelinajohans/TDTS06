import socket
import os
    
class serverSocket:
    
    def __init__(self, port_server):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Server socket created")
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((socket.gethostname(), port_server))
        print(socket.gethostname())
        print("Socket is bound to port",port_server)
        self.sock.listen(10)
        print("Server is listening")

    def hear_client(self):
        (clientSocket, clientAddress) = self.sock.accept()
        print("Connection established")
        child = os.fork()
        self.sock.close()
        return(clientSocket)

    def recv_from_client(self, clientSocket):
        msg = clientSocket.recv(6000)
        print(msg)


    def close_socket(self):
        self.sock.close()
    
class clientSocket:

    def __init__(self, webpage):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Client socket created")
        self.sock.connect((webpage, 80))
        print("Server socket connects to", webpage, "on port 80")

    
def main():
    serverSock = serverSocket(8080)
    while 1:
        clientSock = serverSock.hear_client()
##        print(procRunning.clientSocket)
##        print(procRunning.clientAddress)
        serverSock.recv_from_client(clientSock)

if __name__ == "__main__":
   main()
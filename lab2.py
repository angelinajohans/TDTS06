import socket
import threading
import re
import re
    
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
        #self.sock.close()
        #print(os.getpid(), "closed socket")

    def recv_from_client(self, incommingSocket):
        hardmsg = incommingSocket.recv(4000)
        msg = hardmsg.decode(encoding="utf-8", errors="strict")
        # m = re.search('^Upgr:(.*)', msg)
        mreg = re.search('(?<=www.)\w+', msg)
        print('First message with regex:', mreg.group(0))
        # m = re.search('https?:\ / \ / (?!.*:\ / \ /)\S +', msg)
        print ('bytesmessage', hardmsg)
        print('stringmseeage', msg)
        # print ('https message is', m)


# Don't know if this will ever be used...
    def close_socket(self):
        self.sock.close()
    
class clientSocket:

    def __init__(self, webpage):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Client socket created")
        self.sock.connect((webpage, 80))
        print("Server socket connects to", webpage, "on port 80")

class searcher_researcher:

    def find_url(self, recv_msg):
        position_url = recv_mssg.find("://")
        if position_url == -1:
            position_url = recv_msg.find("Host:")
            url_end = recv_msg[(position_url + 6):].find("\r\n")
            url = recv_msg[(position_url + 6):-((len(recv_msg) - (url_end) - 1))]
        else:
            url_end = recv_msg[(position_url + 3):].find(" ")
            url = recv_msg[(position_url + 3):-((len(recv_msg) - (url_end) - 1))]
    
def main():
    serverSock = serverSocket(8000)
    while 1:
        serverSock.hear_client()
        print("Next print is the msg")


if __name__ == "__main__":
    main()

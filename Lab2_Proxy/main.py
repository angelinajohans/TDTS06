from serverSocket import serverSocket

#Creates a server socket using the by input desired port
#Starts the socket functionality     
def main():
    proxy_socket = input('\nEnter the desired port number: ')
    print'You chose to create a server socket on port',proxy_socket
    try:
        serverSock = serverSocket(int(proxy_socket))
        while 1:
            serverSock.hear_client()
    except ValueError:
        print'\nInvalid value, enter a value higher than 8000!'
        main()

    except OverflowError:
        print'\nInvalid value, enter a value higher than 8000 but less than 65000!'
        main()

    except PermissionError:
        print'\nInvalid value, enter a value higher than 8000!'
        main()

#Runs the main function
if __name__ == '__main__':
    main()
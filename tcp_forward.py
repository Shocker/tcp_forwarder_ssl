import socket
import sys
import threading
import os
import signal
import ssl

if len(sys.argv) < 6:
    print('Usage:\n\tpython tcp_forward.py <certificate file> <listen host> <listen port> <remote host> <remote port> [debug]')
    print('Example:\n\tpython cert.pem tcp_forward.py localhost 8080 www.google.com 80')
    sys.exit(0)        

try:
    certFile = sys.argv[1]
    listenHost = sys.argv[2]
    listenPort = int(sys.argv[3])
    targetHost = sys.argv[4]
    targetPort = int(sys.argv[5])
    debugOutput = len(sys.argv) > 6
except Exception as e:
    print("Invalid parameters: %s" % (e))
    exit()

listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
contextClient = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

def main():
    try:
        # prepare SSL client socket context
        contextClient.load_cert_chain(certfile=certFile)
    except Exception as e:
        print("Invalid certificate: %s" % (e))
        os.kill(os.getpid(), signal.SIGKILL)

    try:
        # start listening for clients
        listenSocket.bind((listenHost, listenPort))
        listenSocket.listen(5)
    except Exception as e:
        print("Cannot bind/listen: %s" % (e))
        os.kill(os.getpid(), signal.SIGKILL)

    print("*** listening on %s:%i" % ( listenHost, listenPort ))

    thrd = threading.Thread(target=server, args=())
    thrd.start()
    thrd.join()

def server(*settings):
    try:
        while True:
            # wait for new client connection
            clientSocketHandler, clientAddress = listenSocket.accept()
            print("*** new connection from %s:%i to %s:%i" % ( clientAddress, listenPort, targetHost, targetPort ))
            # convert to SSL socket
            clientSocket = contextClient.wrap_socket(clientSocketHandler, server_side=True)
            
            # create SSL socket to target
            serverSocketHandler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            contextServer = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            serverSocket = contextServer.wrap_socket(serverSocketHandler, server_hostname=targetHost)
            serverSocket.connect((targetHost, targetPort))

            threading.Thread(target=forward, args=(clientSocket, serverSocket, "client -> server")).start()
            threading.Thread(target=forward, args=(serverSocket, clientSocket, "server -> client")).start()
    finally:
        threading.Thread(target=server, args=()).start()

def forward(source, destination, description):
    data = ' '
    while data:
        try:
            data = source.recv(1024)
            if debugOutput:
                print("*** %s [%d bytes]: %s" % ( description, len(data) if data else -1, data ))
        except Exception as e:
            print(e)
            break
        finally:
            if data:
                try:
                    destination.sendall(data)
                except Exception as e:
                    print("Failed sending data: %s" % (e))
            else:
                try:
                    source.shutdown(socket.SHUT_RD)
                except Exception as e:
                    print(e)
                try:
                    destination.shutdown(socket.SHUT_WR)
                except Exception as e:
                    print(e)

if __name__ == '__main__':
    main()

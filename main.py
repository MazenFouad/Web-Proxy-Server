import sys
from socket import *

if len(sys.argv) <= 1:
    print(
        'Usage: "python ProxyServer.py server_ip"\n[server_ip: It is the IP Address Of Proxy Server]')
    sys.exit(2)

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
server_ip = sys.argv[1]
server_port = 8888  # Choose a port number for the proxy server
tcpSerSock.bind((server_ip, server_port))
tcpSerSock.listen(5)

counter = 0
max_iterations = 10

while True:
    # Start receiving data from the client
    counter += 1
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    message = tcpCliSock.recv(1024).decode('utf8')
    print("here", message)

    # Extract the filename from the given message
    print(message.split("/")[1])
    filename = message.split()[1].partition("/")[2]
    print(filename)
    fileExist = False
    filetouse = "/" + filename
    print(filetouse)

    try:
        # Check whether the file exists in the cache
        f = open(filetouse[1:], "r")
        outputdata = f.readlines()
        fileExist = True

        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode('utf8'))
        tcpCliSock.send("Content-Type: text/html\r\n".encode('utf8'))
        for line in outputdata:
            tcpCliSock.send(line.encode('utf8'))
        print('Read from cache')
        f.close()

    except IOError:
        if not fileExist:
            # Create a socket on the proxy server
            c = socket(AF_INET, SOCK_STREAM)
            hostn = filename.replace("www.", "", 1)
            print(hostn)
            try:
                # Connect to the socket to port 80
                c.connect((hostn, 80))

                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                fileobj = c.makefile('wr', 1)
                fileobj.write("GET "+"http://" + filename + " HTTP/1.0\n\n")
                fileobj.flush()

                # Read the response into buffer
                buffer = fileobj.readlines()

                # Create a new file in the cache for the requested file
                tmpFile = open("./" + filename, "wb")
                for line in buffer:
                    tmpFile.write(line.encode('utf8'))
                    tcpCliSock.send(line.encode('utf8'))

                tmpFile.close()
                c.close()

            except Exception as e:
                print("Error: ", e)
                if c:
                    c.close()

        else:
            # HTTP response message for file not found
            tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode('utf8'))
            tcpCliSock.send("Content-Type: text/html\r\n".encode('utf8'))
            tcpCliSock.send("\r\n".encode('utf8'))
            tcpCliSock.send(
                "<html><body><h1>404 Not Found</h1></body></html>\r\n".encode('utf8'))

    # Close the client socket
    tcpCliSock.close()

    # Terminate the server if a specific condition is met
    # For example, you can add a condition to exit the loop and terminate the server by pressing Ctrl+C
    # if some specific command or condition is received from the client, you can also add the necessary code here.
    if counter >= max_iterations:
        break

# Close

tcpSerSock.close()
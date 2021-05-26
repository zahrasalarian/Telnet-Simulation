import socket, ssl


# TCP-socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 50000))
#while 1:
#    data = conn.recv(1024)
#    if not data:
#        break
#    conn.sendall(data)
#    print(data)

mode = input('You can choose between non-TLS and TLS:\n')

####################################### non-TLS connection (you can't send encrypted messages in this mode)
if mode == 'non-TLS':
    s.listen(1)
    (conn, address) = s.accept()
    while True:
        data = conn.recv(32)
        if data == b'upload':
            print('Command: Upload')
            text_file = 'fileProj.txt'
        
            #Receive, output and save file
            with open(text_file, "wb") as fw:
                print("Receiving..")
                while True:
                    print('receiving')
                    data = conn.recv(32)
                    #if data == b'BEGIN':
                    #    continue
                    if data == b'ENDED':
                        print('Breaking from file write')
                        break
                    else:
                        print('Received: ', data.decode('utf-8'))
                        fw.write(data)
                        print('Wrote to file', data.decode('utf-8'))
                fw.close()
                print("Received..")
                #break
        elif data == b'exec':
            cmd_to_exec = conn.recv(32)
            print('yo I got it')
        elif data == b'send':
            while 1:
                data = conn.recv(1024)
                if not data:
                    break
                #conn.sendall(data)
                print(data.decode('utf-8'))
        elif data == b'send -e':
            #while 1:
            #    data = conn.recv(1024)
            #    if not data:
            #        break
            #    #conn.sendall(data)
            #    print(data)
            #    break
            connstream = ssl.wrap_socket(conn, server_side=True, certfile="server.crt", keyfile="server.key")
            data = connstream.read()
            print(data)

    conn.close()

        #Append and send file
        #print('Opening file ', text_file)
        #with open(text_file, 'ab+') as fa:
        #    print('Opened file')
        #    print("Appending string to file.")
        #    string = b"Append this to file."
        #    fa.write(string)
        #    fa.seek(0, 0)
        #    print("Sending file.")
        #    while True:
        #        data = fa.read(1024)
        #        conn.send(data)
        #        if not data:
        #            break
        #    fa.close()
        #    print("Sent file.")
        #break

else:
    s.listen(5)
    (conn, address) = s.accept()
    connstream = ssl.wrap_socket(conn, server_side=True, certfile="server.crt", keyfile="server.key")
    while True:
    #data = conn.recv(32)
    #if data == b'send -e':
        #while 1:
        #    data = conn.recv(1024)
        #    if not data:
        #        break
        #    #conn.sendall(data)
        #    print(data)
        #    break
        data = connstream.read().decode()
        print(data)

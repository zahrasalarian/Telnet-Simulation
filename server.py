import socket, ssl, sys, os
import subprocess

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

def rec_file(file_name, s):
    with open(file_name, "wb") as fw:
        print("Receiving..")
        while True:
            print('receiving')
            data = s.recv(1024)
            #if data == b'BEGIN':
            #    continue
            if not data:
                print('Breaking from file write')
                break
            else:
                print('Received: ', data.decode('utf-8'))
                fw.write(data)
                print('Wrote to file', data.decode('utf-8'))
        fw.close()
        print("Received..")
        s.close()
                
def send_file(file_name, s):
    #Send file
    with open(file_name, 'rb') as fs: 
        for data in fs:
            s.sendall(data)
        fs.close()
    s.close()
####################################### non-TLS connection (you can't send encrypted messages in this mode)
if mode == 'non-TLS':
    s.listen(1)
    (conn, address) = s.accept()
    while True:
        data = conn.recv(1024).decode('utf-8').split()
        #print("message {}".format(data))
        
        if data[0] == 'upload':
            print('Command: Upload')
            text_file = 'rec_from_client.txt'
            #Receive file
            rec_file(text_file, conn)
            break

        elif data[0] == 'exec':
            cmd_to_exec = data[1]
            proc = subprocess.Popen(cmd_to_exec, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            # Write to file 
            with open("stdout.txt", "w+", encoding='utf-8') as text_file:
                text_file.write('stdout:\n')
                text_file.write(stdout.decode())
                text_file.write('stderr:\n')
                text_file.write(stderr.decode())
            #Send file
            send_file('stdout.txt', conn)
            break

        elif data[0] == 'send':
            message = data[1]
            print(message)
            conn.sendall('Message recceived'.encode('utf-8'))

    conn.close()
else:
    s.listen(5)
    (conn, address) = s.accept()
    connstream = ssl.wrap_socket(conn, server_side=True, certfile="server.crt", keyfile="server.key")
    while True:
        data = connstream.read().decode()
        print(data)
        connstream.write('Message recceived'.encode('utf-8'))

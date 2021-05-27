import socket, sys, os
import subprocess
import sqlite3, ssl
from sqlite3 import Error

# TCP-socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 50000))
                
def send_file(file_name, s):
    #Send file
    fw = open(file_name, 'rb')
    data = fw.read(1024)
    while(data):
        s.send(data)
        data = fw.read(1024)
    s.send(b'done')
    print("Completed sending.")
    fw.close()

def rec_file(file_name, s):
    fw = open(file_name, 'wb')
    while True:
        print('Receiving data...')
        data = s.recv(1024)
        print(data)
        print(data[-4:])
        if data[-4:] ==b'done':
            print('Completed receiving.')
            fw.write(data[:-4])
            break
        fw.write(data)
    fw.close()  

# Select mode
mode = input('You can choose between non-TLS and TLS:\n')

####################################### non-TLS connection (you can't send encrypted messages in this mode)
if mode == 'non-TLS':
    s.listen(1)
    (conn, address) = s.accept()
    while True:
        not_decoded = conn.recv(1024)

        print('not decoded data: {}'.format(map(ord, not_decoded)))
        data = not_decoded.decode('utf-8').split()
        print(data)
        #print("message {}".format(data))
        
        if data[0] == 'upload':
            print('Command: Upload')
            text_file = 'rec_from_client.txt'
            #Receive file
            rec_file(text_file, conn)
            #break

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
            #break

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
        # insert into database
        create_users = "INSERT INTO users (command) VALUES (?)"
        execute_query(connection, create_users, ('telnet send -e'+ data,))
        
        print(data)
        connstream.write('Message recceived'.encode('utf-8'))

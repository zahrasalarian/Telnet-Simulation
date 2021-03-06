import sqlite3, ssl
from sqlite3 import Error
import socket, sys, os
import subprocess, time
import rsa, pickle, threading


####################################### send get request to google.com
def get_google():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('www.google.com', 80))
    s.sendall("GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n".encode('utf-8'))
    print (s.recv(4096))
    s.close()

####################################### check open ports
def get_open_ports():
    ips = ['127.0.0.1']#, '185.211.88.131']
    for ip in ips:
        for port in range(65535):      #check for all available ports
            try:
                serv = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # create a new socket
                serv.bind((ip,port)) # bind socket with address
            except:
                print('[OPEN] Port open : {} for {}'.format(port, ip)) #print open port number
            serv.close() #close connection
    print('done')

####################################### send mail to aut webmail
def send_email():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("asg.aut.ac.ir", 25))
    recv = s.recv(1024).decode()
    print("Connection request response: " + recv)
    # HELO 
    s.send("HELO aut.ac.ir\r\n".encode('utf-8'))
    recv1 = s.recv(1024).decode()
    print("HeLO command response: " + recv1)
    # MAIL FROM
    s.send("MAIL FROM:<zasalarian2000@gmail.com>\r\n".encode())
    recv2 = s.recv(1024).decode()
    print("MAIL FROM command response: " + recv2)
    # RCPT TO
    s.send("RCPT TO:<amberbrown2000@aut.ac.ir>\r\n".encode())
    recv3 = s.recv(1024)
    recv3 = recv3.decode()
    print("RCPT TO command response: " + recv3)
    # DATA 
    s.send("DATA\r\n".encode())
    recv4 = s.recv(1024).decode()
    print("DATA command response: " + recv4)
    # msg
    msg = "\r\n Sup, dude? \r\n.\r\n"
    s.send(msg.encode())
    recv_msg = s.recv(1024)
    print("Response to sending message body: " + recv_msg.decode())
    # QUIT
    s.send("QUIT\r\n".encode())
    recv5 = s.recv(1024)
    print("Quit command response: "+ recv5.decode())
    print('done')
    s.close() 

####################################### Database 
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query, values):
    cursor = connection.cursor()
    try:
        cursor.execute(query, values)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

####################################### Send and Receive file functions
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
        print(data[-4:])
        if data[-4:] ==b'done':
            print('Completed receiving.')
            fw.write(data[:-4])
            break
        fw.write(data)
    fw.close()

####################################### Log 
def save_log(c_or_s, data): 
    # Open a file with access mode 'a'
    with open("log.txt", "a") as file_object:
        file_object.write(c_or_s +": ")
    if not isinstance(data, str):
        file_object = open("log.txt", 'ab')
        file_object.write(data)
    else:
        file_object = open("log.txt", 'a')
        file_object.write(data)
    with open("log.txt", "a") as file_object:
        file_object.write('\n')
####################################### Server and Client part
# Choose between server and client
#c_or_s = int(input('For being server enter 0 and for being client enter 1\n'))

# Server
#if c_or_s == 0:
def server_runner(port):
    # TCP-socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', port))
    s.listen(1)
    (conn, address) = s.accept()
    handshake = conn.recv(1024).decode('utf-8')
    print(handshake)
    if handshake == 'Hi server':
        conn.sendall('Hi client'.encode('utf-8'))
    while True:
        not_decoded = conn.recv(1024)
        data = not_decoded.decode('utf-8').split()
        
        # UPLOAD
        if data[0] == 'upload':
            print('Command: Upload')
            text_file = 'recfclient_' + data[1]
            #Receive file
            rec_file(text_file, conn)
            #break

        # EXEC
        elif data[0] == 'exec':
            print(data)
            cmd_to_exec = data[1]
            for d in data[2:]:
                cmd_to_exec += ' ' + d
            print(cmd_to_exec)
            proc = subprocess.Popen(cmd_to_exec, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            # Write to file 
            with open("stdout_stderr.txt", "w+", encoding='utf-8') as text_file:
                text_file.write('stdout:\n')
                text_file.write(stdout.decode())
                text_file.write('stderr:\n')
                text_file.write(stderr.decode())
            #Send file
            send_file('stdout_stderr.txt', conn)

        # SEND
        elif data[0] == 'send' and data[1] != '-e':
            message = data[1]
            for c in data[2:]:
                message += ' ' + c
            print(message)
            conn.sendall('Message recceived'.encode('utf-8'))
        
        # SEND -E
        elif data[0] == 'send' and data[1] == '-e':
            # manual encryption
            ## generate public and private keys for encryption
            publicKey, privateKey = rsa.newkeys(512)
            # send public key to client
            to_send = pickle.dumps(publicKey)
            conn.send(to_send)            
            # receive message
            encMessage = conn.recv(1024)
            decMessage = rsa.decrypt(encMessage, privateKey).decode()
            print(decMessage)
            conn.sendall('Message recceived'.encode('utf-8'))

            continue
            # tls encryption
            # close simple connection
            conn.close()
            # build TLS connection
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('localhost', 23))
            s.listen(5)
            (conn, address) = s.accept()
            connstream = ssl.wrap_socket(conn, server_side=True, certfile="server.crt", keyfile="server.key")
            # Rec message
            data = connstream.read(1024).decode()
            print(data)
            connstream.write('Message recceived'.encode('utf-8'))
            # close tls connection
            connstream.close()
            # open simple connection
            s.listen(1)
            (conn, address) = s.accept()

# Client
#elif c_or_s == 1:
def client_runner(port):
    # create table for commands
    connection = create_connection("history.sqlite")
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT NOT NULL
    );
    """
    execute_query(connection, create_users_table, ())   
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = 'localhost'
    host_port = port
    
    try:
        s.connect((host_name, host_port))
        s.send('Hi server'.encode('utf-8'))
        save_log('Client', 'Hi server')
        print("Connection is alright")
        ack = s.recv(1024)
        print(ack.decode('utf-8'))
        save_log('Server', ack)

    except:
        print('connecting failed!')
    while True:
        command = input()
        # seve log
        save_log('Command', command)
        # insert into database
        create_users = "INSERT INTO users (command) VALUES (?)"
        execute_query(connection, create_users, (command,))

        command = command.split()
        # UPLOAD
        if command[1] == "upload":
            cmd = command[1] + ' ' + command[2]
            s.send(cmd.encode('utf-8'))
            # Send file
            send_file(command[2], s)

        # EXEC
        elif command[1] == 'exec':
            # Send cmd to exec
            cmd_to_exec = command[1] + ' ' + command[2]
            for c in command[3:]:
                cmd_to_exec += ' ' + c
            s.send(cmd_to_exec.encode('utf-8'))
            #Receive, output and save file
            rec_file('stdout_stderr_from_server.txt', s)

        # SEND
        elif command[1] == 'send' and command[2] != '-e':
            message = command[1]
            for c in command[2:]:
                message += ' ' + c
            save_log('Client', message)
            s.send(message.encode('utf-8'))
            ack = s.recv(1024)
            save_log('Server', ack)
            print(ack.decode('utf-8'))

        # SEND Encrypted
        elif command[1] == 'send' and command[2] == '-e':
            # manual encryption
            message = command[1] + ' ' + command[2]
            s.send(message.encode('utf-8'))

            # receive public key from client
            publicKey = s.recv(1024)
            publicKey = pickle.loads(publicKey)

            message = command[3]
            for c in command[4:]:
                message += ' ' + c
            encMessage = rsa.encrypt(message.encode(), publicKey)
            save_log('Client', encMessage)
            s.send(encMessage)
            ack = s.recv(1024)
            save_log('Server', ack)
            print(ack.decode('utf-8'))

            continue
            # tls encryption
            message = command[1] + ' ' + command[2]
            s.send(message.encode('utf-8'))
            s.close()
            time.sleep(3)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ssl_sock = ssl.wrap_socket(s, ca_certs="server.crt", cert_reqs=ssl.CERT_REQUIRED)
            #Connect To The TLS Host
            ssl_sock.connect((host_name,host_port))
            # Send message
            msg = command[3]
            for c in command[4:]:
                msg += ' ' + c
            ssl_sock.write(msg.encode('utf-8'))
            ack = ssl_sock.read().decode()
            print(ack)
            # close tls connection
            s.close()
            # open simple connection
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', 23))


        # HISTORY
        elif command[1] == 'history':
            select_users = "SELECT * from users"
            cmds = execute_read_query(connection, select_users)
            print('Recent commands are:')
            for cmd in cmds:
                print(cmd)

        # LOG


cmd = int(input("if you want to sent a GET request to google.com enter 0\nif you want to scan ips for open ports enter 1\nif you want to send email enter 2\nif you want to work with server and client enter 3\n"))
if cmd == 0:
    get_google()
elif cmd == 1:
    get_open_ports()
elif cmd == 2:
    send_email()
else: 
    port = int(input("Please enter the port of your server\n"))
    sThread = threading.Thread(target=server_runner, args=(port,))
    sThread.start()
    print("socket is listening")
    dec = int(input("if you want to use client enter 0 and for doing nothing enter 1\n"))
    if dec == 0:
        port = int(input("Please enter the port of your client\n"))
        cThread = threading.Thread(target=client_runner, args=(port,))
        cThread.start()
import socket
import sqlite3, ssl
from sqlite3 import Error

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = 'localhost'
host_port = 50000
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

# create table for commands
connection = create_connection("history.sqlite")
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  command TEXT NOT NULL
);
"""
execute_query(connection, create_users_table, ())   

#######################################
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
    
# select mode
mode = input('You can choose between non-TLS and TLS:\n')
####################################### non-TLS connection (you can't send encrypted messages in this mode)

if mode == 'non-TLS':
    s.connect(('localhost', 50000))
    while True:
        command = input()
        # insert into database
        create_users = "INSERT INTO users (command) VALUES (?)"
        execute_query(connection, create_users, (command,))

        command = command.split()
        # UPLOAD
        if command[1] == "upload":
            cmd = command[1] + ' ' + command[2]
            s.send(command[1].encode('utf-8'))
            # Send file
            send_file(command[2], s)

        # EXEC
        elif command[1] == 'exec':
            # Send cmd to exec
            cmd_to_exec = command[1] + ' ' + command[2]
            s.send(cmd_to_exec.encode('utf-8'))
            #Receive, output and save file
            rec_file('stdout_from_server.txt', s)

        # SEND
        elif command[1] == 'send' and command[2] != '-e':
            message = command[1] + ' ' + command[2]
            s.send(message.encode('utf-8'))
            ack = s.recv(1024)
            print(ack.decode('utf-8'))

        # HISTORY
        elif command[1] == 'history':
            select_users = "SELECT * from users"
            cmds = execute_read_query(connection, select_users)
            print('Recent commands are:')
            for cmd in cmds:
                print(cmd)
    s.close()

####################################### TLS connection (you only can send encrypted messages in this mode)
else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(s, ca_certs="server.crt", cert_reqs=ssl.CERT_REQUIRED)
    #Connect To The Host
    ssl_sock.connect((host_name,host_port))
    while True:
        command = input().split()
        if command[1] == 'send' and command[2] == '-e':
            msg = command[3]
            ssl_sock.write(msg.encode('utf-8'))
            ack = ssl_sock.read().decode()
            print(ack)


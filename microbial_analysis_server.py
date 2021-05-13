import socket
import threading
import sys, json
import time, datetime

DATA_TYPE = ['SEND_NOISE', 'SEND_UV280', 'SEND_UV365', 'SEND_UV_COMBO']
REQ_TYPE = ['REQ_TIME', 'REQ_RESULT']
ENDCHAR = '}\n\n'
BUFSIZE = 1024

def handle_client(clnt_sock, addr):
    while True:
        print("client address : {0}, port : {1} ".format(addr[0], addr[1]))
        try:
            buffer = clnt_sock.recv(BUFSIZE)
            recv_data = ''
            while buffer:
                recv_data += buffer.decode('ASCII')
                if recv_data.find(ENDCHAR) > 0:
                    break
                buffer = clnt_sock.recv(BUFSIZE)
            
            print("Recv Data : ", recv_data)
        
        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                sleep(1)
                print('No data available')
            else:
                # a "real" error occurred
                print(e)
                clnt_sock.close()
                sys.exit(1)
        
        try:
            j_data = json.loads(recv_data)
            type = j_data['TYPE']
            print(j_data['TYPE'])
        except json.JSONDecodeError:
            #send nack
            print("json error")
            clnt_sock.close()
            sys.exit(1)

        if type == 'REQ_TIME':
            send_time(clnt_sock)
        elif type == 'REQ_RESULT':
            send_result(clnt_sock)
        elif type in DATA_TYPE:
            send_reply(clnt, type)
    
    clnt_sock.close()

def send_time(sock):
    now = datetime.datetime.now()
    
    json_object = {
            "TYPE": "REQ_TIME",
            "DATE": [now.year, now.month, now.day],
            "TIME": [now.hour, now.minute, now.second]
    }
    json_string = json.dumps(json_object) + '\n\n'
    sock.sendall(json_string.encode())
    print("Send Data : ", json_string)

def send_result(sock):
    json_object = {
            "TYPE": "REQ_RESULT",
            "RESULT":
            {
                "DISEASE" : "INFLUENZA",
                "ACCURACY" : 99.9
            }
    }
    json_string = json.dumps(json_object) + '\n\n'
    sock.sendall(json_string.encode())
    print("Send Data : ", json_string)

def send_reply(sock, type):
    json_object = {
            "TYPE": type,
            "VALUE": "ACK"
    }
    json_string = json.dumps(json_object) + '\n\n'
    sock.sendall(json_string.encode())
    print("Send Data : ", json_string)

if __name__ == '__main__':
    IPADDR = ''
    PORT = 20000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
    server_socket.bind((IPADDR, PORT));
    server_socket.listen();

    try:
        while True:
            client_socket, addr = server_socket.accept();
            client_socket.setblocking(0) #non-blocking
            th = threading.Thread(target=handle_client, args=(client_socket, addr));
            th.start();
    except socket.error as e:
        print(e)
        sys.exit(1)
    finally:
        server_socket.close();

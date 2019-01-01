import socket
import sys
import time

if __name__ == '__main__':
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('socket1 created!')

    s1.bind(('127.0.0.1', 4347))
    print('socket1 bind complete')


    s1.listen(10)
    print('socket1 listening...')

    data = str()
    conn, addr = s1.accept()
    for i in range(100):
        byte = conn.recv(1024)
        s = str(byte, 'utf-8')
        data += s
        if s == '\n':
            conn.close()
            break
    print(data)
    s1.close()





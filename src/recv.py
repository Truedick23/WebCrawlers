import socket
import threading
import time
import sys
import os
import struct
import matplotlib

def deal_data(conn, addr):
    print('Accept new connection from {0}'.format(addr))
    conn.send(bytes('Hi, Welcome to the server!', 'utf-8'))
    while 1:
        fileinfo_size = struct.calcsize('128sl')
        buf = conn.recv(fileinfo_size)
        if buf:
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(b'\00')
            new_filename = os.path.join('./', 'new_' + str(fn, 'utf-8'))
            print('file new name is {0}, filesize is {1}'.format(new_filename, filesize))
            recvd_size = 0
            fp = open(new_filename, 'wb')
            print('start receiving...')
            num = 0
            while not recvd_size == filesize:
                if filesize - recvd_size > 3:
                    data1 = conn.recv(1)
                    data2 = conn.recv(1)
                    data3 = conn.recv(1)
                    print(data1, data2, data3)
                    d1 = int.from_bytes(data1, byteorder='little')
                    d2 = int.from_bytes(data2, byteorder='little')
                    d3 = int.from_bytes(data3, byteorder='little')

                    if data1 == bytes(40) or data2 == bytes(40) or data3 == bytes(40):
                        print('End of file!', num)
                        print(data1, data2, data3)
                        num = num + 1
                    d21 = d2 % 16
                    d22 = d2 / 16

                    Num1 = d21 * 256 + d1
                    Num2 = int(d22 * 256 + d3)

                    res1 = Num1.to_bytes(10, byteorder='big')
                    res2 = Num2.to_bytes(10, byteorder='big')
                    # d = struct.unpack("h", data)
                    # print(bin(d[0]))
                    # print('Data1:', Num1)
                    # print('Data2:', Num2)
                    recvd_size += len(data1)+len(data2)+len(data3)
                    fp.write(data1)
                    fp.write(data2)
                    fp.write(data1)
                else:
                    data = conn.recv(filesize - recvd_size)
                    print(data)
                    # d = struct.unpack("h", data)
                    # print(bin(d[0]))
                    recvd_size = filesize
                    fp.write(data)
            fp.close()
            print('end receive...')
        conn.close()
        break


def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((('127.0.0.1', 6663)))
        s.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    while 1:
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()


if __name__ == '__main__':
    socket_service()
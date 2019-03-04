import socket
import sys
import os
import struct
def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 6663))
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print(s.recv(3))
    filepath = 'ECG.data'
    if os.path.isfile(filepath):
        fileinfo_size = struct.calcsize('128sl')
        print(os.path.basename(filepath))
        print(os.stat(filepath).st_size)
        fhead = struct.pack('128sl', bytes(os.path.basename(filepath), 'utf-8'),
                            os.stat(filepath).st_size)
        s.send(fhead)
        print('client filepath: {0}'.format(filepath))
        fp = open(filepath, 'rb')
        while 1:
            data = fp.read(3)
            if not data:
                print('{0} file send over...'.format(filepath))
                break
            s.send(data)
    s.close()
if __name__ == '__main__':
    socket_client()

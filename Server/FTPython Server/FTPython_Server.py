import ctypes
import socket
import os
import thread

wd = "C:\\FTPFiles\\"

def GET(client, fN):
    fN = wd + fN
    if os.path.isfile(fN):
        size = os.path.getsize(fN)
        client.send('Found ' + str(size))
                   
        f = open(fN, 'rb')
        l = f.read(1024)
        while l:
            print '1'
            client.send(l)
            print '2'
            l = f.read(1024)
            print '3'
        f.close()
        print '4'
    else:
        client.send('Not Found')

def MGET(client, fL):
    fL = fL.split('|')
    for fN in fL:
        GET(client, fN)
        print 'YYY'

def clientThread(client, ip):
    loggedin = encrypt = compress = False
    client.send('220 FTPython')
    while True:
        r = client.recv(1024).strip().split(' ', 1)
        r[0] = r[0].upper()
        print ip[0] + '>',
        for i in r:
            print i,
        print ''
        if r[0] == 'QUIT':
            break
        elif loggedin:
            if r[0] == 'GET':
                GET(client, r[1])
            elif r[0] == 'MGET':
                MGET(client, r[1])
            elif r[0] == 'COMPRESS':
                compress = not compress
                client.send('Compression is now ' + ('enabled' if compress else 'disabled') + '.')
            elif r[0] == 'ENCRYPT':
                encrypt = not encrypt
                client.send('Encryption is now ' + ('enabled' if encrypt else 'disabled') + '.')
            elif r[0] == 'NORMAL':
                compress = encrypt = False
                client.send('Compression and encryption are now disabled.')
            else:
                client.send('202 Command Not Implemented')
        elif r[0] == 'USER':
            #Check User
            client.send('331 Need Password')
        elif r[0] == 'PASS':
            #Check Password
            client.send('230 Logged In')
            #client.send('430 Incorrect Login')
            loggedin = True
        else:
            client.send('202 Command Not Implemented')
    client.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 60383))
    s.listen(20)
    while True:
        print socket.gethostname()
        client, r = s.accept()
        thread.start_new_thread(clientThread, (client, r))
        print 'Found', r[0]

ctypes.windll.kernel32.SetConsoleTitleA("FTPython Server")
print 'FTPython Server\n'
main()
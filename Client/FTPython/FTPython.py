import ctypes
import getpass
import socket
import time

def trySend(s, i):
    try:
        if len(i) > 0:
            s.send(i)
    except:
        print 'Server Disconnected'

def trySendSecure(s, i):
    print 'Not Implemented'

def main():
    #ip = raw_input('Server Address- ')

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #s.connect(('10.20.122.203', 85))
            s.connect((socket.gethostbyname('MichaelSurface'), 60383))
            i = s.recv(1024)
            print i
            break
        except:
            print 'Server Not Found'
            time.sleep(2)

    while i.startswith('230') == False:
        while i.startswith('331') == False:
            i = raw_input('Username- ')
            trySend(s, 'USER ' + i)
            i = s.recv(1024)
        print i
        i = getpass.getpass('Password- ')
        trySend(s, 'PASS ' + i)
        i = s.recv(1024)
        print i

    while True:        
        i = raw_input('> ')
        while len(i) == 0:
            i = raw_input('> ')
        trySend(s, i)
        cM = i.split(' ', 1)
        if cM[0].upper() == 'GET' or cM[0].upper() == 'MGET':
            fL = cM[1].split('|')
            for fN in fL:
                ret = s.recv(4096).split(' ')
                if ret[0] =='Found':
                    f = open(fN,'wb')
                    print 'Filesize- ' + ret[1] + ' bytes'
                    
                    dl = 0
                    while dl < int(ret[1]):
                        print str(dl/int(ret[1])) + '%'
                        f.write(s.recv(4096))
                        dl = dl + 4096
                    f.close()
                    print '100%'
        elif cM[0].upper() == 'QUIT':
            print 'Disconnected from Server'
            break
        else:
            print s.recv(4096)
    s.close()

ctypes.windll.kernel32.SetConsoleTitleA("FTPython")
print 'Welcome to FTPython\n'

main()

# CD            <dir>
# LS            -
# DIR           -
# *GET           <file>
# PUT           <file>
# MGET          <folder> || *.* || *.<ext> || <name>.* || <name>|<name>
# MPUT          <folder> || *.* || *.<ext> || <name>.* || <name>|<name>
# ASCII-EC      Enable ASCII, disable binary
# BINARY        Enable binary, disable ASCII
# *QUIT         Disconnect from the server
# *COMPRESS     Enable/disable compression
# *ENCRYPT      Enable/disable encryption
# *NORMAL       Turn off encryption and compression
# 
# CRC for each packet
# Asynchronously send packets
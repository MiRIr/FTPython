import ctypes
import getpass
import socket
import thread
import zlib
import glob
import os

def Send(s, i):
	try:
		s.send(i)
	except:
		print 'The server is no longer connected'

def Passive(ip):
	pC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	pC.connect((ip, 832))
	
	return pC

def SendFile(fileName, ip, binary, compress, encrypt):
	pC = Passive(ip)
	if os.path.isfile(fileName):
		pC.send(str(os.path.getsize(fileName)))

		f = open(fileName, 'rb' if binary else 'r')
		l = f.read(4096)
		while l:
			if compress:
				cData = zlib.compress(l, zlib.Z_BEST_COMPRESSION)
				pC.send(cData if len(cData) < 4096 else l)
				pC.recv(5)
			else:
				pC.send(l)
			l = f.read(4096)
		f.close()
		print 'Server has finished downloading ' + fileName
	else:
		pC.send('-1')
	pC.close()

def SendMultipleFiles(s, files, ip, binary, compress, encrypt):
	fileList = glob.glob(files)
	for f in fileList:
		f = os.path.basename(f)
		Send(s, 'PUT ' + f)
		SendFile(f, ip, binary, compress, encrypt)

def ReceiveFile(fileName, ip, binary, compress, encrypt):
	pC = Passive(ip)
	fileSize = int(pC.recv(1024))
	if fileSize > -1:
		print 'Downloading ' + fileName
		f = open(fileName, 'wb' if binary else 'w')
		while True:
			data = pC.recv(4096)
			if not data:
				break
			if compress:
				f.write(data if len(data) == 4096 else zlib.decompress(data))
				pC.send('Go')
			else:
				f.write(data)
		f.close()
		print 'Finished downloading ' + fileName
	else:
		print fileName + ' does not exist'
	pC.close()

def ReceiveMultipleFiles(s, fileName, ip, binary, compress, encrypt):
	pC = Passive(ip)
	fileListString = str(pC.recv(8192))
	fileList = fileListString.split('|')
	print fileListString
	pC.close()
	for f in fileList:
		f = os.path.basename(f)
		Send(s, 'GET ' + f)
		ReceiveFile(f, ip, binary, compress, encrypt)

def ServerOutput(s):
	while True:
		try:
			out = str(s.recv(4096))
			print out
		except:
			break

def main():
	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		ip = None
		compress = encrypt = False
		binary = True
		
		def Send(i):
			try:
				s.send(i)
			except:
				print 'The server is no longer connected'

		while True:
			try:
				ip = raw_input('Server Address- ')
				s.connect((ip, 831))
				i = s.recv(1024)
				print i
				break
			except:
				print 'Server not found'

		while True:
			i = raw_input('USER ')
			Send('USER ' + i)
			response = str(s.recv(1024))
			print response
			if response.startswith('331'):
				break

		while True:
			i = getpass.getpass('PASS ')
			Send('PASS ' + i)
			response = str(s.recv(1024))
			print response
			if response.startswith('230'):
				break
	
		thread.start_new_thread(ServerOutput, (s,))
		while True:
			i = raw_input()
			while len(i) == 0:
				i = raw_input()
			iSplit = i.split(' ', 1)
			command = iSplit[0].upper()
			if command == 'CD' or command == 'LS' or command == 'DIR':
				Send(i)
			elif command == 'GET':
				Send(i)
				ReceiveFile(iSplit[1], ip, binary, compress, encrypt)
			elif command == 'MGET':
				Send(i)
				ReceiveMultipleFiles(s, iSplit[1], ip, binary, compress, encrypt)
			elif command == 'PUT':
				Send(i)
				SendFile(iSplit[1], ip, binary, compress, encrypt)
			elif command == 'MPUT':
				SendMultipleFiles(s, iSplit[1], ip, binary, compress, encrypt)
			elif command == 'ASCII':
				binary = False
				Send(i)
			elif command == 'BINARY':
				binary = True
				Send(i)
			elif command == 'COMPRESS':
				compress = not compress
				Send(i)
			elif command == 'ENCRYPT':
				encrypt = not encrypt
				Send(i)
			elif command == 'NORMAL':
				compress = encrypt = False
				Send(i)
			elif command == 'QUIT':
				Send(i)
				break
		s.close()
		print 'Please Enter a New Server Address'

ctypes.windll.kernel32.SetConsoleTitleA("FTPython")
print 'Welcome to FTPython\n'

main()
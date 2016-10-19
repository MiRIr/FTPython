import ctypes
import socket
import os
import thread
import random
import zlib
import glob

def Passive():
	pC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	pC.bind((socket.gethostname(), 832))
	pC.listen(20)
	client, r = pC.accept()

	return client

def ReceiveFile(fileName, binary, compress, encrypt):
	pC = Passive()
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

def SendFile(fileName, binary, compress, encrypt):
	pC = Passive()
	if os.path.isfile(fileName):
		pC.send(str(os.path.getsize(fileName)))

		f = open(fileName, 'rb' if binary else 'r')
		l = f.read(4096)
		while l:
			if compress:
				cData = zlib.compress(l, zlib.Z_BEST_COMPRESSION)
				pC.send(cData if len(cData) < 4096 else l)
				pC.recv(10)
			else:
				pC.send(l)
			l = f.read(4096)
		f.close()
		print 'Client has finished downloading ' + fileName
	else:
		pC.send('-1')
	pC.close()

def checkEmail(s):
	if '@' in s:
		s2 = s.split('@')
		if len(s2[0]) > 0 and len(s2[1]) > 2 and '.' in s2[1]:
			s3 = s2[1].split('.')
			if len(s3[0]) > 0 and len(s3[1]) > 0:
				return True
	return False

def clientThread(client, ip):
	client.send('220 FTPython')
	wd = 'F:\\'
	encrypt = compress = False
	binary = True
	anonymous = True

	while True:
		try:
			out = str(client.recv(1024))
			print out
			out = out.split(' ', 1)
			out[0] = out[0].upper().strip()
			if out[0] == 'QUIT':
				break
			elif anonymous:
				if out[0] == 'USER' and len(out) == 2:
					if out[1] == 'anonymous':
						client.send('331 Password required')
						anonymous = 1
					else:
						client.send('530 Incorrect Username')
				elif out[0] == 'PASS' and len(out) == 2 and anonymous == 1:
					if checkEmail(out[1]):
						client.send('230 Logged on')
						anonymous = False
					else:
						client.send('530 Incorrect Username or Password')
				else:
					client.send('You need to log in first.')
			elif out[0] == 'CD':
				if out[1] == '..':
					wd = os.path.dirname(wd)
					client.send('The working directory is now ' + wd)
				elif os.path.isdir(os.path.join(wd, out[1])):
					wd = os.path.join(wd, out[1])
					client.send('The working directory is now ' + wd)
				else:
					client.send('Directory ' + out[1] + ' not found')
			elif out[0] == 'LS':
				tmpDir = wd
				if len(out) > 1:
					tmpDir = os.path.join(wd, out[1])
				if os.path.isdir(tmpDir):
					ls = os.listdir(tmpDir)
					client.send('\n'.join(ls))
				else:
					client.send(tmpDir + ' is not a valid directory')
			elif out[0] == 'DIR' and len(out) > 1:
				if not os.path.exists(os.path.join(wd, out[1])):
					os.makedirs(os.path.join(wd, out[1]))
					client.send('Directory ' + out[1] + ' created')
				else:
					client.send('Directory ' + out[1] + ' already exists')
			elif out[0] == 'GET' and len(out) > 1:
				SendFile(os.path.join(wd, out[1]), binary, compress, encrypt)
			elif out[0] == 'MGET' and len(out) > 1:
				fileList = glob.glob(os.path.join(wd, out[1]))
				pC = Passive()
				pC.send('|'.join(fileList))
				pC.close()
			elif out[0] == 'PUT' and len(out) > 1:
				ReceiveFile(os.path.join(wd, out[1]), binary, compress, encrypt)
			elif out[0] == 'ASCII':
				binary = False
				client.send('Switched to ASCII mode')
			elif out[0] == 'BINARY':
				binary = True
				client.send('Switched to binary mode')
			elif out[0] == 'ENCRYPT':
				encrypt = not encrypt
				client.send('Encryption is now ' + ('enabled' if encrypt else 'disabled'))
			elif out[0] == 'COMPRESS':
				compress = not compress
				client.send('Compression is now ' + ('enabled' if compress else 'disabled'))
			elif out[0] == 'NORMAL':
				compress = encrypt = False
				client.send('Compression and encryption are now disabled')
		except:
			break

	print ip[0] + ' has disconnected'
	client.close()

def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((socket.gethostname(), 831))
	s.listen(20)
	while True:
		client, r = s.accept()
		thread.start_new_thread(clientThread, (client, r))
		print 'Found ' + r[0]

ctypes.windll.kernel32.SetConsoleTitleA("FTPython Server")
print 'FTPython Server\n'
main()
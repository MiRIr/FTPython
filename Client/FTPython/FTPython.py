import ctypes
import getpass
import socket
import time
import thread

dataChannel = None
binary = True

def Send(s, i):
	try:
		s.send(i + '\n')
	except:
		print 'The server is no longer connected.'

def ServerOutput(s):
	while True:
		try:
			out = str(s.recv(4096))
			print out
			global dataChannel
			if out.startswith('227'):
				response = out.split('(')[1].split(',')
				ip = response[0] + '.' + response[1] + '.' + response[2] + '.' + response[3]
				port = int(response[4]) * 256 + int(response[5].replace(')', ''))
				dataChannel = (dataChannel, ip, port)
			elif out.startswith('150'):
				global binary
				if (dataChannel[0].upper().startswith('RETR') or dataChannel[0].upper().startswith('GET')) and binary:
					thread.start_new_thread(DownloadFile, (dataChannel,))
				elif dataChannel[0].upper().startswith('LIST') or dataChannel[0].upper().startswith('MLSD') or not binary:
					thread.start_new_thread(HandleASCII, (dataChannel,))
				dataChannel = None

		except:
			break
			
def DownloadFile(info):
	try:
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		c.connect((info[1], info[2]))

		f = open(info[0].split(' ', 1)[1], 'wb')
		while True:
			data = c.recv(4096)
			if not data:
				break
			f.write(data)
		f.close()
		print 'Finished ' + info[0].split(' ', 1)[1]
	except:
		pass

def HandleASCII(info):
	try:
		c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		c.connect((info[1], info[2]))

		listing = ''
		while True:
			data = c.recv(16)
			if not data:
				break
			listing = listing + data
		print listing
	except:
		pass

def main():
	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
			Send(s, 'USER ' + i)
			response = str(s.recv(1024))
			print response
			if response.startswith('331'):
				break

		while True:
			i = getpass.getpass('PASS ')
			Send(s, 'PASS ' + i)
			response = str(s.recv(1024))
			print response
			if response.startswith('230'):
				break
	
		thread.start_new_thread(ServerOutput, (s,))
		while True:
			i = raw_input()
			while len(i) == 0:
				i = raw_input()
			if i.upper() == 'QUIT':
				break
			if i.upper().startswith('RETR ') or i.upper().startswith('GET ') or i.upper().startswith('MLSD ') or i.upper().startswith('LIST '):
				Send(s, 'PASV')
				Send(s, i)
				global dataChannel
				dataChannel = i
			elif i.upper().startswith('ASCII'):
				global binary
				binary = not binary
			else:
				Send(s, i)
		s.close()

ctypes.windll.kernel32.SetConsoleTitleA("FTPython")
print 'Welcome to FTPython\n'

main()

# CD	CWD		<dir>
# LS	LIST	-
# DIR	MLSD	-
# GET	RETR	<file>
# PUT			<file>
# MGET			<folder> || *.* || *.<ext> || <name>.* || <name>|<name>
# MPUT			<folder> || *.* || *.<ext> || <name>.* || <name>|<name>
# ASCII-EC		Enable ASCII, disable binary
# BINARY		Enable binary, disable ASCII
# QUIT			Disconnect from the server
# COMPRESS		Enable/disable compression
# ENCRYPT		Enable/disable encryption
# NORMAL		Turn off encryption and compression
# 
# CRC for each packet
# Asynchronously send packets
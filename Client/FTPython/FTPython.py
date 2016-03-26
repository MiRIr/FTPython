import ctypes
import getpass
import socket
import time
import thread

dataChannels = []
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
			if out.startswith('227'):
				response = out.split('(')[1].split(',')
				ip = response[0] + '.' + response[1] + '.' + response[2] + '.' + response[3]
				port = int(response[4]) * 256 + int(response[5].replace(')', ''))
				global dataChannels
				dataChannels[0] = (dataChannels[0],) + (ip, port)
		except:
			break

def HandleDataChannels():
	global dataChannels
	while True:
		if len(dataChannels) > 0:
			if len(dataChannels[0]) == 3:
				global binary
				if (dataChannels[0][0].upper().startswith('RETR') or dataChannels[0][0].upper().startswith('GET')) and binary:
					thread.start_new_thread(DownloadFile, (dataChannels[0],))
					dataChannels.pop(0)
				elif dataChannels[0][0].upper().startswith('LIST') or dataChannels[0][0].upper().startswith('MLSD') or not binary:
					thread.start_new_thread(HandleASCII, (dataChannels[0],))
					dataChannels.pop(0)
			
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
	#ip = raw_input('Server Address- ')

	while True:
		while True:
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect(('10.0.0.2', 831))
				i = s.recv(1024)
				print i
				break
			except:
				print 'Server Not Found'
				time.sleep(1)

		Send(s, 'USER LANLauncher')
		Send(s, 'PASS')
	
		thread.start_new_thread(ServerOutput, (s,))
		thread.start_new_thread(HandleDataChannels, ())
		while True:
			i = raw_input()
			while len(i) == 0:
				i = raw_input()
			if i.upper() == 'QUIT':
				break
			if i.upper().startswith('RETR ') or i.upper().startswith('GET ') or i.upper().startswith('MLSD ') or i.upper().startswith('LIST '):
				Send(s, 'PASV')
				Send(s, i)
				global dataChannels
				dataChannels.insert(0, i)
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
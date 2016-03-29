import ctypes
import socket
import os
import thread
import random

def clientThread(client, ip):
	client.send('220 FTPython')
	wd = 'F:\\'
	loggedin = encrypt = compress = False
	dataChannel = None

	def SendFile(info): #port, fileName
		fileName = wd + info[1].strip()

		if os.path.isfile(fileName):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print 'Opening data channel on port ' + str(info[0])
			s.bind((socket.gethostname(), info[0]))
			s.listen(1)
			channel, r = s.accept()
			while True:
				if ip[0] == r[0]:
					print 'Client connected to data channel'
					break
				else:
					channel.close()
					channel, r = s.accept()
				break
			f = open(fileName, 'rb')
			l = f.read(4096)
			while l:
				channel.send(l)
				l = f.read(4096)
			f.close()
			print 'Client has finished downloading ' + info[1]
			client.send('226 Successfully transferred ' + info[1])
			channel.close()
		else:
			print fileName + ' was not found'
			client.send('550 File not found')

	while True:
		try:
			out = str(client.recv(4096))
			print out
			if out.upper().startswith('QUIT'):
				break
			elif loggedin:
				if out.upper().startswith('PASV'):
					dataChannel = random.randint(32768, 65535)
					client.send('227 Entering Passive Mode (' + ip[0].replace('.', ',') + ',' + str(dataChannel / 256) + ',' + str(dataChannel % 256) + ')')
				elif out.upper().startswith('RETR') or out.upper().startswith('GET'):
					response = out.split(' ', 1)
					if dataChannel:
						dataChannel = (dataChannel, response[1])
						client.send('150 Opening data channel to send ' + response[1])
						thread.start_new_thread(SendFile, (dataChannel,))
						dataChannel = None
					else:
						client.send('500 Use the PASV command to create a data channel.')
			elif out.upper().startswith('USER'):
				client.send('331 Password required')
			elif out.upper().startswith('PASS'):
				client.send('230 Logged on')
				loggedin = True
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
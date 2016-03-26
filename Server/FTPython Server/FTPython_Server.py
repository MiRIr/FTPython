import ctypes
import socket
import os
import thread
import random

def clientThread(client, ip):
	wd = 'F:\\Games\\LANLauncher\\Server\\Data\\'
	loggedin = encrypt = compress = False
	client.send('220 FTPython')

	def SendFile(info): #port, fileName
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print 'Opening Data Channel on Port ' + str(info[0])
		s.bind((socket.gethostname(), info[0]))
		s.listen(1)
		channel, r = s.accept()
		while True:
			if ip[0] == r[0]:
				print 'Client Connected to Data Channel'
				break
			else:
				channel.close()
				channel, r = s.accept()
			break

		fN = wd + info[1].strip()
		if os.path.isfile(fN):
			f = open(fN, 'rb')
			l = f.read(4096)
			while l:
				channel.send(l)
				l = f.read(4096)
			f.close()
			print 'Client has finished downloading ' + info[1]
			client.send('226 Successfully transferred ' + info[1])
		else:
			print info[1] + ' was not found'
			client.send('550 File not found')
		channel.close()

	dataChannel = None
	while True:
		try:
			out = str(client.recv(4096))
			print out
			if out.upper().startswith('QUIT'):
				break
			elif out.upper().startswith('PASV'):
				port = random.randint(32768, 65535)
				client.send('227 Entering Passive Mode (' + ip[0].replace('.', ',') + ',' + str(port / 256) + ',' + str(port % 256) + ')')
				dataChannel = port
			elif out.upper().startswith('RETR') or out.upper().startswith('GET'):
				response = out.split(' ', 1)
				if dataChannel:
					dataChannel = (dataChannel, response[1])
					thread.start_new_thread(SendFile, (dataChannel,))
					dataChannel = None
				else:
					client.send('500 Use the PASV command to create a data channel.')
				#thread to handle data channel
				#+Command
			#elif handleLIST
		except:
			break

	print ip[0] + ' has disconnected.'
	client.close()

def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((socket.gethostname(), 831))
	s.listen(20)
	while True:
		print socket.gethostname()
		client, r = s.accept()
		thread.start_new_thread(clientThread, (client, r))
		print 'Found ' + r[0]

ctypes.windll.kernel32.SetConsoleTitleA("FTPython Server")
print 'FTPython Server\n'
main()
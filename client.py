import socket,ssl
import getpass
import time
import sys
import threading
from rich import print
import random
import hashlib
import pickle
import datetime
import struct


context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

IP = "206.189.128.208"
PORT = 443
user = ''

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client = context.wrap_socket(client,server_hostname="209.38.82.81")
client.connect((IP,PORT))
socket.timeout(5)
print(f"[CONNECTED +] Connection Established!")

colors = ["#eda4a4","#edc8a4","#ede6a4","#e6edb4","#e1fa3e","#bcfa98","#5efc03","#1cfc03","#03fc66","#c5fcdb","#c5fcec","#c5eefc","#00bbff"]
colors2 = ["yellow","bright_red","#cecef5","#8c8eff","#b8b6ba","#ce8ff2","#db76d8","#ff00b3","#f76dab","#b06d74"]

def decorative_box(text):
    line = "★" * (len(text) + 4)
    padding = " " * (len(text) + 4)

    print(padding + line + padding)
    print(padding + f"* [#41e007]{text}[/#41e007] *" + padding)
    print(padding + line + padding)

decorative_box("PRIVATE CHAT ROOM ")

print("[#6df2e5]LOGIN TO CONTINUE[/#6df2e5]")

class HandleUserInteraction:
	def __init__(self,**kwargs):
		self.user = ""
		self.color = random.choice(colors)
		self.color2 = random.choice(colors2)
		self.authenticate()

	def send_pickle(self, msg):
	    data = pickle.dumps(msg)
	    length = struct.pack('!I', len(data))  # 4 bytes, big-endian
	    client.sendall(length + data)

	def recv_pickle(self):
	  
	    length_data = b''
	    while len(length_data) < 4:
	        more = client.recv(4 - len(length_data))
	        if not more:
	            raise EOFError("Connection closed before reading length")
	        length_data += more
	    (length,) = struct.unpack('!I', length_data)

	   
	    data = b''
	    while len(data) < length:
	        more = client.recv(length - len(data))
	        if not more:
	            raise EOFError("Connection closed before receiving full data")
	        data += more

	    return pickle.loads(data)



	def UserInteraction(self):
		print("[#a7b5eb]\nType Message in the blank space and hit enter to send![/#a7b5eb]")

		threading.Thread(target=self.startchatting,args=()).start()
		threading.Thread(target=self.receive_messages,args=()).start()



	def receive_messages(self):
		while True:
			try:
				# messages = client.recv(50048)
				messages = self.recv_pickle()
				if messages:
					# messages = pickle.loads(messages)
					print(f"{messages['user']}-# {messages['message']}")#

				else:
					pass

			except Exception as e:
				
				break


	def send_MESSAGES_Fx(self,text):
		date = str(datetime.datetime.now()).split(" ")[1].split(".")[0].split(":")
		time = date.pop()
		tz = f"{date[0]}:{date[1]}"
		if (text == "") or (text == " "):
				pass

		else:
			try:
				text2 = f"[{self.color}]{text}[/{self.color}] {tz}"
				usr = f"[bright_red](User)-[/bright_red][{self.color2}]{user}[/{self.color2}]"
				# client.send(pickle.dumps({
				# 	"user":usr,
				# 	"message":text2
				# 	}))
				self.send_pickle({
					"user":usr,
					"message":text2
					})

		

				if text == "bye":
					usr = f"{user}"

					# client.send(pickle.dumps({
					# 	"user":usr,
					# 	'message':text
					# 	}))
					self.send_pickle({
						"user":usr,
						'message':text
						})
					client.close()
					print("[green]Logged Out Successfully!.[/green]")

					return False

			except Exception as e:
				# print(e)
				print("[bright_red]Chat closed!.[/bright_red]")
				return False

	def startchatting(self):
		global user

		while True:
		
			text = input("")
			if len(text) > 2048:
				print("[yellow]text too long[/yellow]")
			else:
				resp = self.send_MESSAGES_Fx(text)
				if resp == False:
					break
				
			

			
			
	def authenticate(self):
		global user 
		while True:
			try:
				self.user = input(f"Username [default {getpass.getuser()}]:")
				if self.user == "":
					self.user = getpass.getuser()
				self.passwd = input(f"Chatroom Password:")

				# client.send(pickle.dumps({
				# 	'user':self.user,
				# 	'passwd':self.passwd
				# 	}))
				self.send_pickle({
					'user':self.user,
					'passwd':self.passwd
					})
				# print("sent login data")


				# resp = pickle.loads(client.recv(5048))
				resp = self.recv_pickle()
				# print("received login data")

				if resp['status'] == "200 OK":
					print(resp['message'])
					user = self.user
					break

				elif resp['status'] == "400 ERROR":
					print(f"[bright_red]{resp['message']}.[/bright_red]")
					continue

				else:
					print(f"[bright_red]{resp['message']}.[/bright_red]")
					continue

			except Exception as e:
				print("[bright_red]An error occured while processing your data.[/bright_red]")
				print(e)

		print("[#abf0a8]To Leave the chat room, just type 'bye' and hit enter\n[/#abf0a8]")
		self.UserInteraction()






HandleUserInteraction()

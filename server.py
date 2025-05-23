#!/usr/bin/python3

import socket,ssl
import threading
import logging
import sys
import hashlib
import pickle
import time
import configparser
import struct

config = configparser.ConfigParser()
config.read('config.ini')

passwords = config['secrets']['passwd_list'].split(',')

logging.basicConfig(level=logging.INFO,filename='tcpsslActivity.log',filemode='a+',
	format="%(asctime)s - %(levelname)s - %(message)s")

try:
	context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	context.load_cert_chain(certfile='cert.pem',keyfile='key.pem')
	logging.info("Started SSL encryption")


except Exception as e:
	print(f"Failed to initiate secure connection,",e)
	logging.error(f"Failed to initiate secure connection {e}")
	sys.exit()


IP = "0.0.0.0"
PORT = 443
ADDR = (IP,PORT)

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP, PORT))

server.listen()

logging.info("Server started...")
print("Server started...")

class ChatServerSystem():
	def __init__(self,**kwargs):
		self.users = []
		self.usernames = []
		self.running = True
		self.start()


	def broadcast_pickle(self,pickle_data):
		length = struct.pack('!I', len(pickle_data)) 
		conn.sendall(length + pickle_data)

	def send_pickle(self,conn, msg):
		if not conn:
			return None
		else:
			try:
			    data = pickle.dumps(msg)
			    length = struct.pack('!I', len(data)) 
			    conn.sendall(length + data)

			except Exception as e:
				logging.error(e)
				return False

	def recv_pickle(self,conn):
	  
	    length_data = b''
	    if not conn:
	    	return None 

    	
	    try:
		    while len(length_data) < 4:
		        more = conn.recv(4 - len(length_data))
		        if not more:
		            logging.error("Connection closed before reading length")
		            return None

		        length_data += more
		    (length,) = struct.unpack('!I', length_data)

		   
		    data = b''
		    while len(data) < length:
		        more = conn.recv(length - len(data))
		        if not more:
		            logging.error("Connection closed before receiving full data")
		            return None

		        data += more

		    return pickle.loads(data)

	    except Exception as e:
	    	logging.error(e)
	    	return None


	def send_messages(self,message):
		try:
			for user in self.users:
				self.send_pickle(user,message)

		except Exception as e:
			logging.error(f"Messaging failed {e}")
			print(e)


	def start(self):
		while self.running:
			conn,addr = server.accept()
			conn_secure = context.wrap_socket(conn,server_side=True)
			print(f"[ACCEPTED +]Connection From {addr}")
			logging.info(f"[ACCEPTED +]Connection From {addr}")
			
			threading.Thread(target=self.authenticate,args=(conn_secure,addr[0])).start()

	def authenticate(self,client,addr):
		while True:
			try:
				recv_login = self.recv_pickle(client)
				
				if not recv_login:
					logging.warning(f"Received no data during login — closing client connection {addr}")
					client.close()
					return
					
				else:
					user,passwd = recv_login['user'],hashlib.sha256(recv_login['passwd'].encode()).hexdigest()

					if user != "kali:)":
					
						if (passwd in passwords) and not (user in self.usernames):
							break

						elif user in self.usernames:
							self.send_pickle(client,{'status':'400 ERROR','user':'system','message':"Username Taken already"})
							continue
						
						else:
							
							self.send_pickle(client,{'status':'400 ERROR','user':'system','message':"wrong credentials"})
							continue

					else:break

			except Exception as e:
				logging.error(e)


		self.users.append(client)
		self.usernames.append(user)
		threading.Thread(target=self.handle_client,args=(client,addr)).start()
		self.send_pickle(client,{'status':'200 OK','user':'system','message':f"\n[#89f562]Joined Chatroom[/#89f562] {len(self.users)} Active users\n"})



	def handle_client(self,client,addr):
		user  = None
		
		try:
			while True:
				resp = self.recv_pickle(client)
				if not resp:
					logging.info(f"Client at {addr} disconnected or sent no data.")
					break

				self.send_messages(resp)

				if resp['message'] == 'bye':
					user = resp.get('user')
					break 

			
		except Exception as e:
			logging.error(f"Error {e}")
			logging.info(f"(User)-@({addr}) disconnected")


		finally:
			try:
				if client in self.users:
					index = self.users.index(client)
					user = self.usernames[index]
					self.users.remove(client)
					self.usernames.pop(index)
					client.close()

					logging.info(f"Cleaned up user {user} from {addr}")

					self.send_messages({
					"user": "notification",
					"message": f"{user or 'A user'} left the chat."
					})

			except Exception as e:
				logging.error(f"Cleanup error: {cleanup_error}")


ChatServerSystem()
	
		

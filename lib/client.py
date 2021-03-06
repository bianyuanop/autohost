from base64 import b64encode
from hashlib import md5
from lib.quirks.network import Network
from lib.quirks.unitSync import UnitSync
from serverlauncher import ServerLauncher
from termcolor import colored
import lib.quirks.hosterCTL

import time



class Client():

	def __init__(self, battlePort, startDir):
		self.network = Network()
		self.network.connect('ulti-wiki.eterea.uk')
		self.battlePort=battlePort
		self.startDir=startDir
	
	def sysCTLTrigger(self):
		while True:
			self.network.receive()
		#return "word to split"
			while self.network.hasCmd():
				#print("aaanetwork has cmd!")
				chatBuffer=self.network.nextCmd()
				#print(chatBuffer)
				#self.network.receive()
				if 'sysctl' in chatBuffer:
					return chatBuffer
				elif 'SAID' in chatBuffer and 'Autohost' not in chatBuffer:
					return 'msgRelay '+chatBuffer

	
	def login(self, username, password, local_ip='*', cpu=0):
		password = b64encode(md5(password).digest()).decode('utf8')
		command = 'LOGIN %s %s %i %s' % (username, password, cpu, local_ip)
		self.network.send(command)



	def openBattle(self,username, battle_type, nat_type, password, port, max_players, mod_hash, rank, map_hash, engine_name, engine_version, map_name, title, game_name):
		self.network.receive()
		command = 'OPENBATTLE %i %i %s %i %i %i %i %i %s\t%s\t%s\t%s\t%s' % (battle_type, nat_type, password, port, max_players, mod_hash, rank, map_hash, engine_name, engine_version, map_name, title, game_name)
		self.network.send(command)
		while True:
			self.network.receive()
			while self.network.hasCmd():
				response=self.network.nextCmd()
				if 'BATTLEOPENED' in response and username in response:
					return response.split()[1]


	def updateBInfo(self,mapHash, mapName):
		command = 'UPDATEBATTLEINFO 1 0 %s %s' % (mapHash, mapName)
		if lib.quirks.hosterCTL.isInetDebug:
			print('sending '+command)
		self.network.send(command)

	def startBattle(self):
		statsCode=self.__binToDeci('1011011')
		command = 'MYSTATUS '+str(statsCode)
		self.network.send(command)
	
	def stopBattle(self):
		statsCode=self.__binToDeci('1011010')
		command = 'MYSTATUS '+str(statsCode)
		self.network.send(command)

	def keepalive(self,username):
		command = 'PING'
		self.network.send(command)
		while (True):
			try:
				self.network.send(command)
				if lib.quirks.hosterCTL.isInetDebug:
					print(colored('[INET]', 'grey','on_green'), colored(username+': keeping alive', 'white', 'on_green'))
				else:
					#print(colored('[INET]', 'grey','on_green'), colored(username+': keeping alive', 'white', 'on_green'),end = "\r")
					pass
				time.sleep(10)
			except:
				return;

	def ping(self,username):
		command = 'PING'
		self.network.send(command)
	
	
	def joinChat(self, channel):
		command = 'JOIN '+channel
		self.network.send(command)
		
	def sayChat(self, channel, msg):
		command = 'SAY '+channel+" "+msg
		self.network.send(command)

	def exit(self):
		self.network.disconnect()
		
	def getUserinChat(self,channel,selAccount,teamConf):
		self.joinChat(channel)
		#print('aaa')
		pindex=0
		playerMatrix={}
		while True:
			#print('bbb')
			self.network.receive()
			while self.network.hasCmd():
				#print('ccc')
				response=self.network.nextCmd().split()
				#print(colored('[INFO]', 'cyan'), response)
				try:
					if 'CLIENTS' in response[0]:
						if channel in response[1]:
							self.leaveChat(channel)
							#print('self acc: '+selAccount)
							 
							response.remove(selAccount)
							response.remove('Autohost_CTL')
							response=response[2:]
							#print (response)
							#print('aaaa')
							for i in response:
								playerMatrix[i]={'team':0,'muted':0,'isAI':False,'index':pindex,'isLeader':False, 'isChicken': False, 'isSpector': False}
								#print('bbb')
								#print (playerMatrix[i])
								pindex+=1
								
						
							for j in teamConf.split():
								if j.startswith('GPT'):
									playerMatrix[j]={'team':0,'muted':0,'isAI':True,'index':pindex,'isLeader':False, 'isChicken': False, 'isSpector': False}
									pindex+=1
								elif j.startswith('Chicken'):
									playerMatrix[j]={'team':0,'muted':0,'isAI':False,'index':pindex,'isLeader':False, 'isChicken': True, 'isSpector': False}
									pindex+=1

							return playerMatrix
				except:
					continue

	def leaveChat(self, channel):
		command = 'LEAVE '+channel
		self.network.send(command)

	def clearBuffer(self, username):
		self.network.receive()	
		while(self.network.hasCmd()):
			#self.network.nextCmd()
			if lib.quirks.hosterCTL.isInetDebug:
				#print(lib.quirks.hosterCTL.isInetDebug)
				print(colored('[INET]', 'grey'), colored(username+': '+self.network.nextCmd(), 'white'))
			else:
				#print(colored('[INET]', 'grey'), colored(username+': '+self.network.nextCmd(), 'white'),end = "\r")
				self.network.nextCmd()
				
	def __decimalToBinary(self, n): 
		return bin(n).replace("0b", "") 
	
	def __binToDeci(self,n):
		return int(n, 2)

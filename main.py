#from lib.message_queue import Deliver
import time
import threading
import os
from lib.client import Client
import _thread
import threading
from multiprocessing import Queue
from hoster import Battle #ability to open battles
from lib.quirks.autohost_factory import AutohostFactory #ability to change credential to host battles
from termcolor import colored
import lib.cmdInterpreter
from lib.quirks.hosterCTL import hosterCTL, isInetDebug
from hoster import deliver
#from multiprocessing import SimpleQueue
password = b'password'
map_file = 'Comet'
mod_file = 'Zero-K-master.sdd'
engineName = 'Spring'
engineVersion = '104.0.1-1435-g79d77ca maintenance'
gameName = 'Zero-K v1.8.3.5'
q = Queue()
battlePort = 2000
startDir = os.getcwd()


lib.quirks.hosterCTL.isInetDebug=True   #turn true to enable network msg inspection

if __name__ == "__main__":
	
	print(colored('[INFO]', 'green'), colored('Main: Initing.', 'white'))
	client = Client(battlePort,startDir)
	autohost=AutohostFactory()
	
	client.login('Autohost_CTL',password)
	print(colored('[INFO]', 'green'), colored('Autohost_CTL: Logging in', 'white'))
	client.clearBuffer('Autohost_CTL')
	
	client.joinChat('bus')
	print(colored('[INFO]', 'green'), colored('Autohost_CTL: Joining Battle Chat.', 'white'))
	client.clearBuffer('Autohost_CTL')
	
	_thread.start_new_thread( client.keepalive,('Autohost_CTL',))
	client.clearBuffer('Autohost_CTL')


	

	BtlPtr=0
	battle=[]
# ,'gemType': 'default', 'isPasswded': False, 'passwd':"", 'mapFile': 'comet_catcher_redux.sd7', 'modFile': '0465683c70018f80a17b92ed78174d19.sdz', 'engineName': 'Spring', 'engineVersion': '104.0.1-1435-g79d77ca maintenance', 'mapName': 'Comet Catcher Redux', 'roomName': 'Test Room', 'gameName': 'Zero-K v1.8.3.5'
	
	while True:

		#client.ping('Autohost_CTL')
		servermsg=client.sysCTLTrigger()
		user=servermsg.split()[2]
		msg=lib.cmdInterpreter.cmdRead(servermsg[3:])[1]
		###COMMANDS BELOW ARE HOST ONLY. NON POLLABLE. HOSTER NOT EXECUTING IF THOSE ARE NOT GENERATED BY HOST#############
		###The logic of the interpreter is that the main ctl code grabs any ctl command and associates them with the battle id they were coming from. hoster periodically checks the bid associated commands in the dictionary. If such commands exist, hoster checks the issuer. If the issuer isn't the host, it is discarded.
		if 'host' in msg:
			battle.append( Battle(msg['user'],startDir,q, autohost, password, map_file, mod_file, engineName, engineVersion, msg['title'], gameName, 2000+BtlPtr))  # change username, password annd room name everytime call this line
			battle[BtlPtr].start() #this is non blocking, the loop continues to check cmds
			BtlPtr+=1
		else:
			# adding the ctl to Message queue, when all ctl been got and processed, the `hoster.py` call task_done then back to `main.py` to move to next command
			ctl = None
			if 'map' in msg:
				ctl = {
					"bid": msg['bid'],
					"msg": 'chmap '+msg['map']+' '+user	
				}
			if 'leave' in msg:
				ctl = {
					"bid": msg['bid'],
					"msg": "left "+user
				}
			if 'start' in msg:
				ctl = {
					"bid": msg['bid'],
					"msg": "start "+user  
				}
			if 'leader' in msg:
				ctl = {
					"bid": msg['bid'],
					"msg":"leader "+msg['leader']+" "+user
				}
			if 'player' in msg:
				ctl = {
					"bid": msg['bid'],
					"msg": "changeTeams "+user+" "+msg['player']
				}
				#print ("sending："+"changeTeams "+user+" "+msg['player'])

			deliver.put(ctl)
			deliver.join()
	#time.sleep(10)
	#battle2 = Battle(startDir,q, autohost, password, map_file, mod_file, engineName, engineVersion, mapName, 'aaa', gameName, battlePort)  # change username, and room name everytime call this line
	#time.sleep(1)
	#battle2.start()
	
	print(colored('[INFO]', 'green'), colored('Main: Halting.', 'white'))
	time.sleep(10)



####################################################################################
# socket Stuff
# from Rohan's optional lecture https://github.com/rnvarma/15112-CA-Optional-Lecture-Code
####################################################################################

import socket
from _thread import *
from queue import Queue
import time

HOST = ""
PORT = 50014
serverMsg = Queue(100)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


####################################################################################
# classes
####################################################################################

class Player(object):
	def __init__(self, x,y,Cindex=None,ID=None):
		self.x,self.y = x,y
		self.ID = ID
		self.pictures = [PhotoImage(file = "images/Leo_0.gif"),
						PhotoImage(file = "images/DD_0.gif"),
						PhotoImage(file = "images/Rodi_0.gif"),
						PhotoImage(file = "images/Irene_0.gif"),
						PhotoImage(file = "images/Leo_1.gif"),
						PhotoImage(file = "images/DD_1.gif"),
						PhotoImage(file = "images/Rodi_1.gif"),
						PhotoImage(file = "images/Irene_1.gif"),
						PhotoImage(file = "images/Leo_2.gif"),
						PhotoImage(file = "images/DD_2.gif"),
						PhotoImage(file = "images/Rodi_2.gif"),
						PhotoImage(file = "images/Irene_2.gif"),
						PhotoImage(file = "images/Leo_3.gif"),
						PhotoImage(file = "images/DD_3.gif"),
						PhotoImage(file = "images/Rodi_3.gif"),
						PhotoImage(file = "images/Irene_3.gif")]
		self.Cindex = Cindex
		self.picture = self.pictures[Cindex] if Cindex != None else self.pictures[0]
		self.maxBomb = 1
		self.speed = 8
		self.explodeRange = 1
		self.bombCount = 0
		self.offBomb = set()
		self.ready = False
		self.timerCount = 0
		self.dead = False

	def move(self,dx,dy):
		self.x += round(dx*self.speed)
		self.y += round(dy*self.speed)

	def draw(self,canvas):
		canvas.create_oval(self.x-14,self.y-10,self.x+14,self.y+10,fill = "gray")
		canvas.create_image(self.x,self.y-25,image = self.picture)

	def offBound(self,left,top,right,bottom):
		if self.x<left or self.x>right or self.y<top or self.y>bottom:
			return True

	def killed(self,board):
		col = round(self.x/40)-1
		row = round(self.y/40)-1
		if board[row][col] == 0:
			return True

	def moveTo(self,x,y,canvas):
			self.x = x
			self.y = y
			canvas.coords(self.picture,self.x,self.y)

	def __str__(self):
		return ("Player" + str(self.ID))


####################################################################################


class gameObject(object):
	def __init__(self,x,y):
		self.x,self.y = x,y

	def draw(self,canvas):
		self.image = canvas.create_image(self.x,self.y,image = self.picture)

	def isCollision(self,other):
		if self.x+20+17>other.x>self.x-20-17 and self.y+20+17>other.y>self.y-20-17:
			return True


class item(gameObject):
	def __init__(self,x,y,type):
		super().__init__(x,y)
		self.type = type
		self.pictures = []
		for i in range(3):
			filename = "images/item_%d.gif"%i
			self.pictures.append(PhotoImage(file = filename))
		self.picture = self.pictures[self.type]

	def isCollision(self,other):
		if self.x+15+17>other.x>self.x-15-17 and self.y+15+17>other.y>self.y-15-17:
			return True


class obstacle(gameObject):
	def __init__(self,x,y):
		super().__init__(x,y)
		self.pictures = []
		for i in range(2):
			filename = "images/obstacle_%d.gif"%i 
			self.pictures .append(PhotoImage(file = filename))
		self.picture = self.pictures[0]
		self.destructTime = 0
		
	def burnt(self,board):
		(col,row) = self.x//40-1,self.y//40-1
		if board[row][col] == 0:
			return True


class NonRemovableObstacle(obstacle):
	def __init__(self,x,y):
		super().__init__(x,y)
		filename = "images/NRobstacle_0.gif" 
		self.picture = PhotoImage(file = filename)

	def burnt(self,board):
		pass


class Bomb(gameObject):
	def __init__(self,x,y,ID=-1):
		super().__init__(x,y)
		self.col,self.row = round(self.x/40)-1,round(self.y/40)-1
		self.pictures = []
		for i in range(9):
			filename = "images/bomb_%d.gif"%i 
			self.pictures .append(PhotoImage(file = filename))
		self.picture = self.pictures[0]
		self.timerCount = 0
		self.exploding = False
		self.onceOff = False
		self.drawList = []
		self.ID = ID

	def off(self,x,y):
		if self.onceOff ==False:
			if self.x+20<=x-17 or self.x-20>=x+17 or self.y+20<=y-17 or self.y-20>=y+17:
				self.onceOff = True



####################################################################################



class Board(object):
	def __init__(self):
		self.size = 40
		self.margin = 20
		self.row,self.col = 11,15
		self.board = [[-1 for i in range(self.col)] for j in range(self.row)]

	def draw(self,canvas):
		for row in range(self.row):
			for col in range(self.col):
				left,top = self.margin + self.size*col,self.margin + self.size*row
				right,bottom = left + self.size, top + self.size
				canvas.create_rectangle(left,top,right,bottom)



####################################################################################
# tkinter
# animation barebone from http://www.cs.cmu.edu/~112/notes/events-example0.py
####################################################################################


from tkinter import *
import copy
import random

def init(data):
	# startScreen
	data.mode = "startScreen"
	data.startScreen = PhotoImage(file = "images/start_0.gif")
	data.helpScreen = PhotoImage(file = "images/help_0.gif")
	data.buttonX,data.buttonY = 260,380
	data.Sindex = 0
	
	# charSelect
	data.charSelects = []
	for i in range(5):
		filename = "images/charSelect_%d.gif"%i
		data.charSelects.append(PhotoImage(file = filename))
	data.charSelect = data.charSelects[1]
	data.squareX,data.squareY = 52,75
	data.Cindex = 0

	# readyConnect
	data.inputIP = ""
	data.connected = False
	data.informMsg = "connected"
	data.mapSelect = False
	data.mapNum = 0
	data.premap = []
	for mapPre in range(3):
		filename = "images/mapPre_%d.gif"%mapPre
		data.premap.append(PhotoImage(file = filename))
	data.readyConnect = PhotoImage(file = "images/readyConnect_0.gif")
	data.readies = []
	for j in range(3):
		filename = "images/ready_%d.gif"%j
		data.readies.append(PhotoImage(file = filename))

	#playGame
	data.backgrounds = [PhotoImage(file = "images/background_0.gif"),
							PhotoImage(file = "images/background_1.gif")]
	data.charas = []
	for k in range(8):
		filename = "images/head_%d.gif"%k
		data.charas.append(PhotoImage(file = filename))
	data.board = Board()
	data.me = Player(40,40,data.Cindex)
	data.otherStrangers = []
	data.maps = [
  [[-1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1],
   [-1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1],
   [ 1,  1,  2,  2,  1,  1,  1,  1,  1,  1,  1,  2,  2,  1,  1],
   [ 1,  1,  2,  2,  1,  1,  1,  1,  1,  1,  1,  2,  2,  1,  1],
   [ 1,  1,  1,  1,  1,  1,  2,  2,  2,  1,  1,  1,  1,  1,  1],
   [ 1,  1,  1,  1,  1,  1,  2,  2,  2,  1,  1,  1,  1,  1,  1],
   [ 1,  1,  1,  1,  1,  1,  2,  2,  2,  1,  1,  1,  1,  1,  1],
   [ 1,  1,  2,  2,  1,  1,  1,  1,  1,  1,  1,  2,  2,  1,  1],
   [ 1,  1,  2,  2,  1,  1,  1,  1,  1,  1,  1,  2,  2,  1,  1],
   [-1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1],
   [-1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1]],

   [[ -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1 ],
    [ -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1 ],
    [  1,  1,  1,  2,  1,  1,  1,  2,  1,  1,  2,  2,  2,  1,  1 ],
    [  1,  1,  2,  2,  1,  1,  2,  2,  1,  1,  1,  1,  2,  1,  1 ],
    [  1,  1,  1,  2,  1,  1,  1,  2,  1,  1,  1,  2,  1,  1,  1 ],
    [  1,  1,  1,  2,  1,  1,  1,  2,  1,  1,  2,  1,  1,  1,  1 ],
    [  1,  1,  1,  2,  1,  1,  1,  2,  1,  1,  2,  1,  1,  1,  1 ],
    [  1,  1,  2,  2,  2,  1,  2,  2,  2,  1,  2,  2,  2,  1,  1 ],
    [  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1 ],
    [ -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1 ],
    [ -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1 ]],

    [[ -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1],
     [ -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1],
     [  1,  1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1],
     [  1,  1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1],
     [  1,  1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1],
     [  1,  1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1],
     [  1,  1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1],
     [  1,  1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1],
     [  1,  1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1],
     [ -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1],
     [ -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1]]
     ]
	data.map = data.maps[data.mapNum]

	data.itemMap = [
	 [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
     [ -1,  1, -1, -1, -1, -1, -1, -1, -1, -1,  2, -1,  3, -1, -1],
     [ -1, -1, -1, -1,  2, -1, -1,  1, -1, -1, -1,  1, -1, -1, -1],
     [  2, -1,  2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
     [ -1, -1, -1, -1, -1, -1, -1, -1, -1,  1, -1, -1,  2, -1, -1],
     [ -1,  3, -1,  1,  1, -1,  1, -1, -1, -1, -1, -1, -1, -1, -1],
     [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
     [ -1, -1, -1, -1, -1, -1,  3, -1, -1, -1, -1,  2, -1, -1, -1],
     [ -1, -1, -1, -1,  3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
     [ -1,  2, -1, -1, -1, -1,  2,  1, -1, -1, -1, -1, -1,  3, -1],
     [ -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]

	data.items = []
	for i in range(len(data.itemMap)):
		for j in range(len(data.itemMap[0])):
			if data.itemMap[i][j]==1:
				data.items.append(item(40*(j+1),40*(i+1),0))
			elif data.itemMap[i][j]==2:
				data.items.append(item(40*(j+1),40*(i+1),1))
			elif data.itemMap[i][j]==3:
				data.items.append(item(40*(j+1),40*(i+1),2))

	data.obstacle = []
	data.msg = ""
	data.bombs = []
	data.nowExploding = set()
	data.gameOver = False
	data.win = False


def message(data):
	if not serverMsg.empty():
		msg = serverMsg.get(False)
		if msg.startswith ("newPlayer"):
			msg = msg.split()
			newPID = int(msg[1])
			x,y = 40,40
			if newPID == 1:
				x,y = 600,40
			elif newPID == 2:
				x,y = 40,440
			elif newPID == 3:
				x,y = 600,440
			data.otherStrangers.append(Player(x,y,None,newPID))
		elif msg.startswith ("Welcome"):
			msg = msg.split()
			myID = int(msg[2])
			data.me.ID = myID
			if myID == 1:
				data.me.x,data.me.y = 600,40
			elif myID == 2:
				data.me.x,data.me.y = 40,440
			elif myID == 3:
				data.me.x,data.me.y = 600,440
		else:
			msg = msg.split()
			PID = int(msg[0])
			if msg[1] == "Cindex":
				for stranger in data.otherStrangers:
					if stranger.ID == PID:
						Cindex = int(msg[2])
						stranger.Cindex = Cindex
						stranger.picture = stranger.pictures[Cindex]
			elif msg[1] == "Start":
				data.mapNum = int(msg[2])
				data.map = data.maps[data.mapNum]
				

				for i in range(len(data.map)):
					for j in range(len(data.map[0])):
						if data.map[i][j]==1:
							data.obstacle.append(obstacle(40*(j+1),40*(i+1)))
						elif data.map[i][j]==2:
							data.obstacle.append(NonRemovableObstacle(40*(j+1),40*(i+1)))

				data.mode = "playGame"
			elif msg[1] == "Ready":
				for stranger in data.otherStrangers:
					if stranger.ID == PID:
						stranger.ready = True


def handleServerMsg(server,):
	server.setblocking(1)
	msg = ""
	command = ""
	while True:
		msg += server.recv(100).decode("UTF-8")
		command = msg.split("\n")
		while (len(command) > 1):
			readyMsg = command[0]
			msg = "\n".join(command[1:])
			print("msgRec: ",readyMsg)
			serverMsg.put(readyMsg)
			command = msg.split("\n")




####################################################################################
# mode dispatcher
# from http://www.cs.cmu.edu/~112/notes/notes-animations-examples.html#modeDemo
####################################################################################



def mousePressed(event, data):
	if (data.mode == "startScreen"): startScreenMousePressed(event, data)
	elif (data.mode == "playGame"):   playGameMousePressed(event, data)
	elif (data.mode == "help"):	   helpMousePressed(event, data)
	elif (data.mode == "charSelect"): charSelectMousePressed(event,data)
	elif (data.mode == "readyConnect"): readyConnectMousePressed(event,data)

def keyPressed(event, data):
	if (data.mode == "startScreen"): startScreenKeyPressed(event, data)
	elif (data.mode == "playGame"):   playGameKeyPressed(event, data)
	elif (data.mode == "help"):	   helpKeyPressed(event, data)
	elif (data.mode == "charSelect"): charSelectKeyPressed(event,data)
	elif (data.mode == "readyConnect"): readyConnectKeyPressed(event,data)

def timerFired(data):
	if (data.mode == "startScreen"): startScreenTimerFired(data)
	elif (data.mode == "playGame"):   playGameTimerFired(data)
	elif (data.mode == "help"):	   helpTimerFired(data)
	elif (data.mode == "charSelect"): charSelectTimerFired(data)
	elif (data.mode == "readyConnect"): readyConnectTimerFired(data)

def redrawAll(canvas, data):
	if (data.mode == "startScreen"): startScreenRedrawAll(canvas, data)
	elif (data.mode == "playGame"):   playGameRedrawAll(canvas, data)
	elif (data.mode == "help"):	   helpRedrawAll(canvas, data)
	elif (data.mode == "charSelect"): charSelectRedrawAll(canvas,data)
	elif (data.mode == "readyConnect"): readyConnectRedrawAll(canvas,data)


####################################################################################
# startScreen mode
####################################################################################

def startScreenMousePressed(event, data):
	if 260<event.x<380 and 380<event.y<430:
		data.mode = "charSelect"
	elif 260<event.x<380 and 440<event.y<490:
		data.mode = "help"

def startScreenKeyPressed(event, data):
	if event.keysym == "Up" and data.Sindex == 1:
		data.Sindex -= 1
		data.buttonY -= 60
	elif event.keysym == "Down" and data.Sindex == 0:
		data.Sindex += 1
		data.buttonY += 60
	elif event.keysym == "Return":
		if data.Sindex == 1:
			data.mode = "help"
		elif data.Sindex == 0:
			data.mode = "charSelect"

def startScreenTimerFired(data):
	pass

def startScreenRedrawAll(canvas, data):
	buttonWidth,buttonHeight = 120,50
	canvas.create_image(data.width/2,data.height/2,image = data.startScreen)
	canvas.create_rectangle(260,380,380,430)
	canvas.create_rectangle(260,440,380,490)
	canvas.create_text(320,405,text = "Start")
	canvas.create_text(320,465,text = "Instruction")
	canvas.create_rectangle(data.buttonX,data.buttonY,data.buttonX+buttonWidth,
						data.buttonY+buttonHeight,outline = "Black",width = 3)
	
####################################################################################
# help mode
####################################################################################

def helpMousePressed(event, data):
	data.mode = "startScreen"

def helpKeyPressed(event, data):
	data.mode = "startScreen"

def helpTimerFired(data):
	pass

def helpRedrawAll(canvas, data):
	canvas.create_image(data.width/2,data.height/2,image = data.helpScreen)

	
####################################################################################
# charSelect mode
####################################################################################

def charSelectMousePressed(event, data):
	squareWidth,squareHeight = 115, 145
	if 75<event.y<220:
		if 52<event.x<167:
			data.Cindex = 0
			data.squareX = 52
		if 52+140<event.x<167+140:
			data.Cindex = 1
			data.squareX = 52+140
		if 52+140*2<event.x<167+140*2:
			data.Cindex = 2
			data.squareX = 52+140*2
		if 52+140*3<event.x<167+140*3:
			data.Cindex = 3
			data.squareX = 52+140*3
		data.charSelect = data.charSelects[data.Cindex+1]
	if 460 <event.x<560 and 400<event.y<460:
		data.me.picture = data.me.pictures[data.Cindex]
		data.mode = "readyConnect"

def charSelectKeyPressed(event, data):
	if event.keysym == "Right" :
		data.Cindex = (data.Cindex + 1)%4
		data.squareX = 52 + 140*data.Cindex
		data.charSelect = data.charSelects[data.Cindex+1]
	elif event.keysym == "Left":
		data.Cindex = (data.Cindex - 1)%4
		data.squareX = 52 + 140*data.Cindex
		data.charSelect = data.charSelects[data.Cindex+1]
	elif event.keysym == "Return":
		data.me.picture = data.me.pictures[data.Cindex]
		data.mode = "readyConnect"
	elif event.keysym == "Escape":
		data.mode = "startScreen"

def charSelectTimerFired(data):
	pass

def charSelectRedrawAll(canvas, data):
	squareWidth,squareHeight = 115,145
	canvas.create_image(data.width/2,data.height/2,image = data.charSelects[0])
	canvas.create_rectangle(data.squareX,data.squareY,data.squareX+squareWidth,
						data.squareY+squareHeight,outline = "Yellow",width = 3)
	canvas.create_image(data.width/2,data.height/2,image = data.charSelect)


####################################################################################
# readyConnect mode
####################################################################################

def clear(data):
	for stranger in data.otherStrangers:
		if stranger.ready == False:
			return False
	return True

def readyConnectMousePressed(event, data):
	if data.connected:
		data.me.ready = True
		data.server.send(bytes("Ready\n","UTF-8"))
		if data.me.ID == 0 and clear(data):
			data.server.send(bytes("Start %d\n"%data.mapNum,"UTF-8"))
			data.map = data.maps[data.mapNum]

			for i in range(len(data.map)):
				for j in range(len(data.map[0])):
					if data.map[i][j]==1:
						data.obstacle.append(obstacle(40*(j+1),40*(i+1)))
					elif data.map[i][j]==2:
						data.obstacle.append(NonRemovableObstacle(40*(j+1),40*(i+1)))

			data.mode = "playGame"

def readyConnectKeyPressed(event, data):
	if event.keysym == "BackSpace":
		if data.inputIP!="":
			data.inputIP = data.inputIP[:-1]

	elif event.keysym == "Escape":
		if data.connected== False:
			data.mode = "charSelect"

	elif event.keysym == "Return":
		if data.connected == False:
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			data.server = server
			HOST = data.inputIP
			server.connect((HOST,PORT))
			data.connected = True
			print("connected to server")
		
			start_new_thread(handleServerMsg,(server,))

	elif data.connected == False:
		if event.char in "0123456789.":
			data.inputIP += event.char

	elif data.connected and data.me.ID == 0:
		if event.keysym == "Left":
			data.mapNum = (data.mapNum-1)%3
		elif event.keysym == "Right":
			data.mapNum = (data.mapNum+1)%3

def readyConnectTimerFired(data):
	number = random.randint(1,5)
	if data.me.ready == False and data.connected==True:
		if data.otherStrangers != [] and number == 1:
			data.server.send(bytes("Cindex %d\n"%data.Cindex,"UTF-8"))
	message(data)
	if data.me.ID == 0 and clear(data):
		data.mapSelect = True
	pass

def readyConnectRedrawAll(canvas, data):
	canvas.create_image(data.width/2,data.height/2,image = data.readyConnect)
	canvas.create_text(data.width/2,15,text = "↓Type the IP you're trying to connect to↓",font = "Arial 15 bold")
	canvas.create_text(data.width/2,35,text = data.inputIP)
	canvas.create_line(260,45,380,45)
	if data.connected:
		canvas.create_text(data.width/2,60,text = data.informMsg, font = "Arial 15 bold")
		try:
			imagePosX = 90 if data.me.ID%2==0 else 440
			imagePosY = 160 if data.me.ID//2==0 else 360
			canvas.create_image(imagePosX,imagePosY,image = data.me.picture)
			for stranger in data.otherStrangers:
				SimagePosX = 90 if stranger.ID%2==0 else 440
				SimagePosY = 160 if stranger.ID//2==0 else 360
				canvas.create_image(SimagePosX,SimagePosY,image = stranger.picture)
		except:
			pass
		if not data.me.ready:
			canvas.create_image(data.width/2,data.height/2,image = data.readies[0])
		else:
			canvas.create_image(data.width/2,data.height/2,image = data.readies[1])
		if data.me.ID == 0 and clear(data):
			canvas.create_image(data.width/2,data.height/2,image = data.readies[2])
	if data.mapSelect:
		canvas.create_polygon(40,460,40,490,30,475,fill = "yellow")
		canvas.create_polygon(160,460,160,490,170,475,fill = "yellow")
		canvas.create_rectangle(48,437,152,515,fill = "yellow",width = 0)
		canvas.create_image(100,475,image = data.premap[data.mapNum])
		canvas.create_text(100,425,text = "Use arrow keys to select map",fill = "white",font = "arial 10 bold")


####################################################################################
# playGame mode
####################################################################################

def playGameMessage(data):
	if not serverMsg.empty():
		msg = serverMsg.get(False)
		msg = msg.split()
		PID = int(msg[0])
		if msg[1] == "bomb":
			col,row = int(msg[2]),int(msg[3])
			data.bombs.append(Bomb((col+1)*40,(row+1)*40,PID))
			data.board.board[row][col] = 1

		elif msg[1] == "Dead":
			for stranger in data.otherStrangers:
				if stranger.ID == PID:
					deathForStranger(stranger)

		elif msg[1] == "Win":
			data.gameOver = True

		else:
			dx = int(msg[1])
			dy = int(msg[2])
			for stranger in data.otherStrangers:
				if stranger.ID == PID:
					stranger.moveTo(dx,dy,data.canvas)
					break

def IWon(data):
	for stranger in data.otherStrangers:
		if stranger.dead == False:
			return False
	data.me.picture = data.me.pictures[data.Cindex+12]
	return True

def playGameMousePressed(event, data):
	if data.gameOver:
		if data.width/2-40<event.x<data.width/2+40 and data.height/2-20<event.y<data.height/2+20:
			data.server.send(bytes("bye\n","UTF-8"))
			data.server.shutdown(1)
			data.server.close()
			init(data)
			data.mode = "startScreen"
	pass

#################################
# movement
#################################

def isLegalMove(data,dx,dy):
	left,top,right,bottom = 38,30,data.width-38,data.height-70
	if data.me.offBound(left,top,right,bottom):
		data.me.move(-dx,-dy)
	for obstacle in data.obstacle:
			if obstacle.isCollision(data.me):
				data.me.move(-dx,-dy)
	for bomb in data.me.offBomb:
		if bomb.isCollision(data.me):
			data.me.move(-dx,-dy)


def playGameKeyPressed(event, data):
	if event.keysym == "space" and data.me.dead == False:
		col = round((data.me.x)/40)-1
		row = round((data.me.y)/40)-1
		if data.me.bombCount<=data.me.maxBomb-1 and data.board.board[row][col]!=1:
			data.bombs.append(Bomb((col+1)*40,(row+1)*40,data.me.ID))
			data.board.board[row][col] = 1
			msg = "bomb" + " " + str(col)+ " " + str(row) + "\n"
			data.server.send(bytes(msg,"UTF-8"))
			data.me.bombCount+=1
	elif data.me.dead == False:
		if event.keysym =="Up":
			data.me.move(0,-1)
			isLegalMove(data,0,-1)
			
		if event.keysym =="Down":
			data.me.move(0,1)
			isLegalMove(data,0,1)

		if event.keysym =="Right":
			data.me.move(1,0)
			isLegalMove(data,1,0)

		if event.keysym =="Left":
			data.me.move(-1,0)
			isLegalMove(data,-1,0)

		data.msg = str(data.me.x) + " " + str(data.me.y)

	if data.me.dead or data.gameOver:
		return


#################################
# explosion
#################################

def explodeBoard(data,bomb):
	rows,cols = len(data.board.board),len(data.board.board[0])
	row,col = bomb.row,bomb.col
	data.board.board[row][col] = 0
	directions = [(0,-1),(0,1),(-1,0),(1,0)]
	removeList = []
	me = data.me
	if me.ID != bomb.ID:
		for stranger in data.otherStrangers:
			if stranger.ID == bomb.ID:
				me = stranger
	for i in range(1,1+me.explodeRange):
		for direction in directions:
			curRow,curCol = direction[0]*i,direction[1]*i
			if 0<= row + curRow < rows and 0<= col + curCol < cols:
				if data.map[row + curRow][col + curCol] != -1:
					removeList.append(direction)
				data.board.board[row + curRow][col + curCol] = 0
				if direction == (0,-1): index = 0
				elif direction == (0,1): index = 1
				elif direction == (-1,0): index = 2
				else: index = 3
				bomb.drawList.append((index,row + curRow,col + curCol))
		for direction in removeList:
			directions.remove(direction)
		removeList = []

def drawBomb(data,bomb):
	for pair in bomb.drawList:
		(row,col) = pair[1:]
		data.canvas.create_image(40*(col+1),40*(row+1),image = bomb.pictures[pair[0]+5])

def explosion(data):
	removeList = []
	for bomb in data.bombs:
		bomb.timerCount += 1
		if bomb.timerCount ==26:
			bomb.picture = bomb.pictures[1]
			bomb.exploding = True
			explodeBoard(data,bomb)
		if bomb.timerCount >26:
			data.nowExploding.add(bomb)
			# bomb.picture = bomb.pictures[2]
		if bomb.timerCount >29:
			bomb.drawList = []
			data.nowExploding.remove(bomb)
			bomb.picture = bomb.pictures[3]
		if bomb.timerCount >30:
			removeList.append(bomb)
		if bomb.timerCount<=25 and bomb.timerCount%4 == 0:
			bomb.picture = bomb.pictures[4] if bomb.picture == bomb.pictures[0] else bomb.pictures[0]
	for bomb in removeList:
		if bomb.ID == data.me.ID:
			data.me.bombCount -= 1
		if bomb in data.me.offBomb:
			data.me.offBomb.remove(bomb)
		data.bombs.remove(bomb)
		data.board.board = copy.deepcopy(data.map)


def death(data):
	if data.me.killed(data.board.board) and data.me.timerCount == 0:
		data.me.picture = data.me.pictures[data.Cindex+8]
		data.me.timerCount+=1
	elif data.me.killed(data.board.board) and 2>=data.me.timerCount >=1:
		data.me.picture = data.me.pictures[data.Cindex+4]
		data.me.timerCount+=1
	elif data.me.killed(data.board.board) and data.me.timerCount == 3:
		data.me.dead = True
		deadmsg = "Dead\n"
		data.server.send(bytes(deadmsg,"UTF-8"))
		data.server.send(bytes(deadmsg,"UTF-8"))

def deathForStranger(stranger):
	if stranger.timerCount == 0:
		stranger.picture = stranger.pictures[stranger.Cindex+8]
		stranger.timerCount += 1
	elif 1<= stranger.timerCount <= 2:
		stranger.picture = stranger.pictures[stranger.Cindex+4]
		stranger.timerCount += 1
	elif stranger.timerCount == 3:
		stranger.dead = True


def burntDown(data):
	removeList = []
	for obstacle in data.obstacle:
		if obstacle.burnt(data.board.board):
			removeList.append(obstacle)
			obstacle.picture = obstacle.pictures[1]
			obstacle.destructTime += 1
	for obstacle in removeList:
		obstacle.destructTime += 1
		if obstacle.destructTime >3:
			(col,row) = obstacle.x//40-1,obstacle.y//40-1
			data.map[row][col]=-1
			data.obstacle.remove(obstacle)


def dealItem(data):
	removeList = []
	for item in data.items:
		if item.isCollision(data.me):
			removeList.append(item)
			if item.type == 0:
				data.me.maxBomb +=1
			elif item.type == 1:
				data.me.speed += 0.5
			elif item.type == 2:
				data.me.explodeRange +=1
		else:
			for stranger in data.otherStrangers:
				if item.isCollision(stranger):
					removeList.append(item)
					if item.type == 2:
						stranger.explodeRange +=1
	for item in removeList:
		data.items.remove(item)


def playGameTimerFired(data):
	explosion(data)
	burntDown(data)
	death(data)

	if data.msg:
		msg = data.msg + "\n"
		data.server.send(bytes(msg,"UTF-8"))
		data.msg = ""

	for bomb in data.bombs:
		bomb.off(data.me.x,data.me.y)
		if bomb.onceOff==True and bomb not in data.me.offBomb:
			data.me.offBomb.add(bomb)

	dealItem(data)
	playGameMessage(data)

	if IWon(data) and not data.gameOver:
		winmsg = "Win\n"
		data.server.send(bytes(winmsg,"UTF-8"))
		data.win = True
		data.gameOver = True

	if data.gameOver and not data.win:
		for stranger in data.otherStrangers:
			if stranger.dead ==False:
				stranger.picture = stranger.pictures[stranger.Cindex+12]

#################################
# draw stuffs
#################################

def drawHead(canvas,data):
	if data.me.dead == False:
		canvas.create_image(45+159*data.me.ID,492,image = data.charas[data.Cindex])
	else:
		canvas.create_image(45+159*data.me.ID,492,image = data.charas[data.Cindex+4])
	for stranger in data.otherStrangers:
		if stranger.dead == False:
			canvas.create_image(45+159*stranger.ID,492,image = data.charas[stranger.Cindex])
		else:
			canvas.create_image(45+159*stranger.ID,492,image = data.charas[stranger.Cindex+4])

def drawMe(canvas,data):
	canvas.create_polygon((data.me.x-5,data.me.y-60),(data.me.x+5,data.me.y-60),(data.me.x,5+data.me.y-60),fill = "Yellow")

def drawResult(canvas,data):
	canvas.create_rectangle(50,130,data.width-50,data.height-130,fill = "grey", stipple="gray75")
	canvas.create_image(520,340,image = data.me.picture)
	if data.win:
		canvas.create_text(data.width/2, 160, text = "Win!",font = "Arial 20 bold")
	else:
		canvas.create_text(data.width/2, 160, text = "Lose",font = "Arial 20 bold")
	for ID in range(4):
		if data.me.ID == ID:
			canvas.create_rectangle(100,180+ID*50,140,214+ID*50,fill = "white")
			if data.win:
				canvas.create_image(120,200+ID*50,image = data.charas[data.Cindex])
			else:
				canvas.create_image(120,200+ID*50,image = data.charas[data.Cindex+4])
		for stranger in data.otherStrangers:
			if stranger.ID == ID:
				canvas.create_rectangle(100,180+ID*50,140,214+ID*50,fill = "white")
				if stranger.dead == False:
					canvas.create_image(120,200+ID*50,image = data.charas[stranger.Cindex])
				else:
					canvas.create_image(120,200+ID*50,image = data.charas[stranger.Cindex+4])
	canvas.create_rectangle(data.width/2-40,data.height/2-20,data.width/2+40,data.height/2+20,fill = "white")
	canvas.create_text(data.width/2,data.height/2,text = "New Game")


def playGameRedrawAll(canvas, data):
	canvas.create_image(data.width/2,data.height/2-20,image = data.backgrounds[0])
	# data.board.draw(canvas)
	for item in data.items:
		item.draw(canvas)
	for bomb in data.bombs:
		bomb.draw(canvas)
	for bomb in data.nowExploding:
		drawBomb(data,bomb)
	for obstacle in data.obstacle:
		obstacle.draw(canvas)
	canvas.create_image(data.width/2,data.height/2,image = data.backgrounds[1])
	for stranger in data.otherStrangers:
		if stranger.dead == False:
			stranger.draw(canvas)
	drawHead(canvas,data)
	if data.me.dead == False:
		data.me.draw(canvas)
		drawMe(canvas,data)
	if data.gameOver:
		drawResult(canvas,data)

####################################
# use the run function as-is
####################################

def run(width=640, height=520):
	def redrawAllWrapper(canvas, data):
		canvas.delete(ALL)
		redrawAll(canvas, data)
		canvas.update()	

	def mousePressedWrapper(event, canvas, data):
		mousePressed(event, data)
		redrawAllWrapper(canvas, data)

	def keyPressedWrapper(event, canvas, data):
		keyPressed(event, data)
		redrawAllWrapper(canvas, data)

	def timerFiredWrapper(canvas, data):
		timerFired(data)
		redrawAllWrapper(canvas, data)
		# pause, then call timerFired again
		canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
	# Set up data and call init
	class Struct(object): pass
	root = Tk() 
	data = Struct()
	data.server = server
	data.serverMsg = serverMsg
	data.width = width
	data.height = height
	data.timerDelay = 100 # milliseconds
	# create the root and the canvas
	root.resizable(width=FALSE, height=FALSE)
	canvas = Canvas(root, width=data.width, height=data.height)
	canvas.pack()
	data.canvas = canvas
	init(data)
	# set up events
	root.bind("<Button-1>", lambda event:
							mousePressedWrapper(event, canvas, data))
	root.bind("<Key>", lambda event:
							keyPressedWrapper(event, canvas, data))
	timerFiredWrapper(canvas, data)
	# and launch the app
	root.mainloop()  # blocks until window is closed
	data.server.send(bytes("bye\n","UTF-8"))
	print("bye!")

run()

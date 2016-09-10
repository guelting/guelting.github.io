import socket
from _thread import *
from queue import Queue
import time

HOST = "128.237.185.120"
PORT = 50014

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((HOST,PORT))

print("connected to server")

serverMsg = Queue(100)

def handleServerMsg(server,):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += server.recv(100).decode("UTF-8")
        print(repr(msg))
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            print("msgRec: ",readyMsg)
            serverMsg.put(readyMsg)
            command = msg.split("\n")

start_new_thread(handleServerMsg,(server,))



class Player(object):
    def __init__(self, x,y,ID=None):
        self.x,self.y = x,y
        self.ID = ID
        self.picture =PhotoImage(file = "images/Leo_1.gif")
        self.maxBomb = 1
        self.bombCount = 0

    def move(self,dx,dy):
        self.x += dx*8
        self.y += dy*8

    def draw(self,canvas):
        canvas.create_oval(self.x-18,self.y-10,self.x+18,self.y+10,fill = "grey")
        canvas.create_image(self.x,self.y-30,image = self.picture)

    def offBound(self,left,top,right,bottom):
        if self.x<left or self.x>right or self.y<top or self.y>bottom:
            return True

    def killed(self,board):
        col = round(self.x/40)-1
        row = round(self.y/40)-1
        if board[row][col] == 0:
            print("boom")

    def moveTo(self,x,y,canvas):
            self.x = x
            self.y = y
            canvas.coords(self.picture,self.x,self.y)

class gameObject(object):
    def __init__(self,x,y):
        self.x,self.y = x,y

    def draw(self,canvas):
        self.image = canvas.create_image(self.x,self.y,image = self.picture)

    def isCollision(self,other):
        if self.x+20+17>other.x>self.x-20-17 and self.y+20+17>other.y>self.y-20-17:
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
            print("bam")
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
        for i in range(5):
            filename = "images/bomb_%d.gif"%i 
            self.pictures .append(PhotoImage(file = filename))
        self.picture = self.pictures[0]
        self.timerCount = 0
        self.exploding = False
        self.ID = ID


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

from tkinter import *

####################################
# customize these functions
####################################

def init(data):
    data.backgrounds = [PhotoImage(file = "images/background_0.gif"),PhotoImage(file = "images/background_1.gif")]
    data.board = Board()
    data.me = Player(40,40)
    data.otherStrangers = []
    data.obstacle = ([obstacle(40*i,40*j) for i in range (3,14,2) for j in [1,11]] + 
            [NonRemovableObstacle(40*i,40*j) for i in range (4,14,2) for j in [1,11]] + 
            [obstacle(40*i,40*j) for i in range(2,15) for j in [2,10]] +
            [obstacle(40*i,40*j) for i in range(1,16) for j in range(3,10)])
    data.msg = ""
    data.bombs = []

def mousePressed(event, data):
    # use event.x and event.y
    pass


# def keyReleased(event,data):
#     if event.keysym in data.keys:
#         data.keys.remove(event.keysym)

def isLegalMove(data,dx,dy):
    left,top,right,bottom = 38,30,data.width-38,data.height-30
    if data.me.offBound(left,top,right,bottom):
        data.me.move(-dx,-dy)
    for obstacle in data.obstacle:
            if obstacle.isCollision(data.me):
                data.me.move(-dx,-dy)

def keyPressed(event, data):
    if event.keysym == "space":
        col = round((data.me.x)/40)-1
        row = round((data.me.y)/40)-1
        print(row,col)
        if data.me.bombCount<=data.me.maxBomb-1:
            data.bombs.append(Bomb((col+1)*40,(row+1)*40,data.me.ID))
            data.board.board[row][col] = 1
            data.msg = "bomb" + " " + str(col)+ " " + str(row)
            data.me.bombCount+=1
    else:
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


#################################
# movement & explosion
#################################

def explodeBoard(data,bomb):
    (row,col) = (bomb.row,bomb.col)
    up = (row-1,col)
    down = (row+1,col)
    left = (row,col-1)
    right = (row,col+1)
    for direction in [up,down,left,right]:
        if 0<=direction[0]<11 and 0<=direction[1]<15:
            data.board.board[direction[0]][direction[1]] = 0

def explosion(data):
    removeList = []
    for bomb in data.bombs:
        bomb.timerCount += 1
        if bomb.timerCount >25:
            bomb.picture = bomb.pictures[1]
            bomb.exploding = True
            explodeBoard(data,bomb)
        if bomb.timerCount >26:
            bomb.picture = bomb.pictures[2]
        if bomb.timerCount >29:
            bomb.picture = bomb.pictures[3]
        if bomb.timerCount >30:
            removeList.append(bomb)
        if bomb.timerCount<=25 and bomb.timerCount%4 == 0:
            bomb.picture = bomb.pictures[4] if bomb.picture == bomb.pictures[0] else bomb.pictures[0]
    for bomb in removeList:
        if bomb.ID == data.me.ID:
        	data.me.bombCount -= 1
        data.bombs.remove(bomb)
        data.board.board = [[-1 for i in range(data.board.col)] for j in range(data.board.row)]


def death(data):
    pass

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
            data.obstacle.remove(obstacle)

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
            print (x,y)
            data.otherStrangers.append(Player(x,y,newPID))
        elif msg.startswith ("Welcome"):
            msg = msg.split()
            myID = int(msg[2])
            data.me.ID = myID
            print(myID)
            if myID == 1:
                data.me.x,data.me.y = 600,40
            elif myID == 2:
                data.me.x,data.me.y = 40,440
            elif myID == 3:
                data.me.x,data.me.y = 600,440
        else:
            msg = msg.split()
            PID = int(msg[0])
            if msg[1] == "bomb":
                print("bomb!")
                col,row = int(msg[2]),int(msg[3])
                data.bombs.append(Bomb((col+1)*40,(row+1)*40))
                data.board.board[row][col] = 1
            else:
                dx = int(msg[1])
                dy = int(msg[2])
                for stranger in data.otherStrangers:
                    if stranger.ID == PID:
                        stranger.moveTo(dx,dy,data.canvas)
                        # isLegalMove(data,stranger)
                        break

def timerFired(data):
    explosion(data)
    burntDown(data)
    data.me.killed(data.board.board)

    if data.msg:
        msg = data.msg + "\n"
        data.server.send(bytes(msg,"UTF-8"))
        data.msg = ""

    start_new_thread(message,(data,))




def redrawAll(canvas, data):
    canvas.create_image(data.width/2,data.height/2,image = data.backgrounds[0])
    # data.board.draw(canvas)
    for bomb in data.bombs:
        bomb.draw(canvas)
    for obstacle in data.obstacle:
        obstacle.draw(canvas)
    canvas.create_image(data.width/2,data.height/2,image = data.backgrounds[1])
    data.me.draw(canvas)
    for player in data.otherStrangers:
        player.draw(canvas)
    # draw in canvas
    pass

####################################
# use the run function as-is
####################################

def run(width=640, height=480):
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

    # def keyReleasedWrapper(event, canvas, data):
    #     keyReleased(event, data)

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
    # root.bind("<KeyRelease>",lambda event:
    #                         keyReleasedWrapper(event,canvas,data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run()

import socket
from _thread import *
from queue import Queue

HOST = "128.237.217.143"
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
    """docstring for Player"""
    def __init__(self, x,y,ID=None):
        self.x,self.y = x,y
        self.ID = ID

    def draw(self,canvas):
        canvas.create_oval(x-20,y-20,x+20,y+20,fill = "blue")
        
####################################
# TKINTER
####################################

from tkinter import *

def init(data):
    # load data.xyz as appropriate
    data.me = Player(data.width/2,data.height/2)
    data.otherStrangers = []
    pass

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    if event.keysym == "Up":
        data.me.y -= 5
        msg = "0 -1"
    if event.keysym == "Down":
        data.me.y += 5
        msg = "0 1"
    if event.keysym == "Right":
        data.me.x += 5
        msg = "1 0"
    if event.keysym == "Left":
        data.me.x -= 5
        msg = "-1 0"
    msg = msg + "\n"
    print("msgSent: ",repr(msg))
    data.server.send(bytes(msg,"UTF-8"))

def timerFired(data):
    if not serverMsg.empty():
        msg = serverMsg.get(False)
        if msg.startswith ("newPlayer"):
            msg = msg.split()
            newPID = int(msg[1])
            data.otherStrangers.append(Player(data.width/2,data.height/2,newPID))
        elif msg.startswith ("Welcome"):
            msg = msg.split()
            myID = int(msg[2])
            data.me.ID = myID
        else:
            msg = msg.split()
            PID = int(msg[0])
            dx = int(msg[1])
            dy = int(msg[2])
            for stranger in data.otherStrangers:
                if stranger.ID == PID:
                    stranger.x += dx *5
                    stranger.y += dy *5
                    break

def redrawAll(canvas, data):
    canvas.create_text(0,0,text = ("Player "+str(data.me.ID)),anchor = "nw")
    # draw in canvas
    canvas.create_oval(data.me.x-20,data.me.y-20,data.me.x+20,data.me.y+20,fill = "red")
    canvas.create_polygon((data.me.x,data.me.y+25),(data.me.x-10,data.me.y+33),(data.me.x+10,data.me.y+33),fill = "yellow")
    for stranger in data.otherStrangers:
        canvas.create_oval(stranger.x-20,stranger.y-20,stranger.x+20,stranger.y+20,fill = "blue")

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
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
    data = Struct()
    data.server = server
    data.serverMsg = serverMsg
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(400, 200)
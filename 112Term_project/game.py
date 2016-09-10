# events-example0.py
# Barebones timer, mouse, and keyboard events

from tkinter import *

class Player(object):
    def __init__(self, x,y,canvas,ID=None):
        self.x,self.y = x,y
        self.ID = ID
        self.picture =PhotoImage(file = "images/Leo_1.gif")
        self.image = canvas.create_image(self.x,self.y,image = self.picture)

    def move(self,dx,dy,canvas):
        self.x += dx*4
        self.y += dy*4
        print(self.x,self.y)
        canvas.coords(self.image, self.x, self.y)

class obstacle(object):
    def __init__(self,x,y,canvas):
        self.x,self.y = x,y
        self.picture = PhotoImage(file = "images/obstacle_0.gif")
        self.image = canvas.create_image(self.x,self.y,image = self.picture)
        
    def isCollision(self,other):
        if self.x+40>other.x + 20>self.x and self.y+40>other.y+20>self.y:
            return True

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


####################################
# customize these functions
####################################

def init(data):
    data.image = PhotoImage(file = "images/background_0.gif")
    data.backGround = data.canvas.create_image(data.width/2,data.height/2,image = data.image)
    data.board = Board() # These are eventually going to disappear.
    data.board.draw(data.canvas) #here just for debugging
    data.me = Player(41,40,data.canvas)
    data.obstacle = obstacle(80,80,data.canvas)

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    if event.keysym == "Up":
        data.me.move(0,-1,data.canvas)
        if data.obstacle.isCollision(data.me):
             data.me.move(0,+1,data.canvas)
    if event.keysym == "Down":
        data.me.move(0,1,data.canvas)
        if data.obstacle.isCollision(data.me):
             data.me.move(0,-1,data.canvas)
    if event.keysym == "Right":
        data.me.move(1,0,data.canvas)
        if data.obstacle.isCollision(data.me):
             data.me.move(-1,0,data.canvas)
    if event.keysym == "Left":
        data.me.move(-1,0,data.canvas)
        if data.obstacle.isCollision(data.me):
             data.me.move(+1,0,data.canvas)

def timerFired(data):
    pass

####################################
# use the run function as-is
####################################
def run(width=640, height=480):

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)

    # def mouseMovedWrapper(event,canvas,data):
    #     mouseMoved(event,data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)

    # def keyReleasedWrapper(event, canvas, data):
    #     keyReleased(event, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    # create the root and the canvas
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    data.canvas = canvas
    init(data)
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    # root.bind("<Motion>", lambda event:
    #                         mouseMovedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    # root.bind("<KeyRelease>",lambda event:
    #                         keyReleasedWrapper(event,canvas,data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run()
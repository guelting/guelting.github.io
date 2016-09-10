# events-example0.py
# Barebones timer, mouse, and keyboard events



class Player(object):
    def __init__(self, x,y,ID=None):
        self.x,self.y = x,y
        self.ID = ID
        self.picture =PhotoImage(file = "images/Leo_1.gif")
        self.maxBomb = 1

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
    def __init__(self,x,y):
        super().__init__(x,y)
        self.col,self.row = round(self.x/40)-1,round(self.y/40)-1
        self.pictures = []
        for i in range(5):
            filename = "images/bomb_%d.gif"%i 
            self.pictures .append(PhotoImage(file = filename))
        self.picture = self.pictures[0]
        self.timerCount = 0
        self.exploding = False


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
    data.obstacle = ([obstacle(40*i,40*j) for i in range (3,14,2) for j in [1,11]] + 
            [NonRemovableObstacle(40*i,40*j) for i in range (4,14,2) for j in [1,11]] +
            [obstacle(40*i,40*j) for i in range(2,15) for j in [2,10]] +
            [obstacle(40*i,40*j) for i in range(1,16) for j in range(3,10)])
    data.keys = []
    data.bombs = []

def mousePressed(event, data):
    # use event.x and event.y
    pass


def keyReleased(event,data):
    if event.keysym in data.keys:
        data.keys.remove(event.keysym)

def keyPressed(event, data):
    if event.keysym == "space":
        col = round((data.me.x)/40)-1
        row = round((data.me.y)/40)-1
        print(row,col)
        if len(data.bombs)<data.me.maxBomb:
            data.bombs.append(Bomb((col+1)*40,(row+1)*40))
            data.board.board[row][col] = 1
    elif event.char == 't':
        print("ah")
        data.me.moveTo(600,440,data.canvas)
    elif event.keysym not in data.keys:
        data.keys.append(event.keysym)


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

def isLegalMove(data,dx,dy):
    left,top,right,bottom = 38,30,data.width-38,data.height-30
    if data.me.offBound(left,top,right,bottom):
        data.me.move(-dx,-dy)
    for obstacle in data.obstacle:
            if obstacle.isCollision(data.me):
                data.me.move(-dx,-dy)

def timerFired(data):
    explosion(data)
    if "Up" in data.keys:
        data.me.move(0,-1)
        isLegalMove(data,0,-1)
        
    if "Down" in data.keys:
        data.me.move(0,1)
        isLegalMove(data,0,1)

    if "Right" in data.keys:
        data.me.move(1,0)
        isLegalMove(data,1,0)

    if "Left" in data.keys:
        data.me.move(-1,0)
        isLegalMove(data,-1,0)

    data.me.killed(data.board.board)
    burntDown(data)



def redrawAll(canvas, data):
    canvas.create_image(data.width/2,data.height/2,image = data.backgrounds[0])
    # data.board.draw(canvas)
    for bomb in data.bombs:
        bomb.draw(canvas)
    for obstacle in data.obstacle:
        obstacle.draw(canvas)
    canvas.create_image(data.width/2,data.height/2,image = data.backgrounds[1])
    data.me.draw(canvas)
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

    def keyReleasedWrapper(event, canvas, data):
        keyReleased(event, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    root = Tk() 
    data = Struct()
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
    root.bind("<KeyRelease>",lambda event:
                            keyReleasedWrapper(event,canvas,data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run()
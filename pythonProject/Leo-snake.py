
from tkinter import *
import random

def init(data):
    data.cellWidth = 50
    data.rows = 10
    data.cols = 10
    data.margin = 5 # margin around grid
    data.snake = [(data.rows/2, data.cols/2)]
    data.direction = (0, 0) # (drow, dcol)
    placeFood(data)
    data.timerDelay = 250
    data.gameOver = False
    data.paused = True
    loadImages(data)
    data.moveRange = list(range(4))
    data.stepnum = 0

def loadImages(data):
    moves = 16 
    data.images = [ ]
    for move in range(moves):
        num = move+1
        filename = "images_leo/Leo_%d.gif" % num
        data.images.append(PhotoImage(file=filename))
    data.chick = [ ]
    chicks = 4
    for chick in range(chicks):
        num = chick+1
        filename = "images_leo/Chick_%d.gif" % num
        data.chick.append(PhotoImage(file=filename))

def getImage(data, move):
    return data.images[move]

def getChick(data, move):
    return data.chick[move]

# getCellBounds from grid-demo.py
def getCellBounds(row, col, data):
    x0 = data.margin + col * data.cellWidth
    x1 = x0 + data.cellWidth
    y0 = data.margin + row * data.cellWidth
    y1 = y0 + data.cellWidth
    return (x0, y0, x1, y1)

def mousePressed(event, data):
    pass

def keyPressed(event, data):
    data.paused = False
    if (event.keysym == "p"): data.paused = True; return
    elif (event.keysym == "r"): init(data); return
    if (data.paused or data.gameOver): return
    if (event.keysym == "Up"):
        data.direction = (-1, 0)
        data.moveRange = list(range(12,16))
    elif (event.keysym == "Down"):
        data.direction = (+1, 0)
        data.moveRange = list(range(0,4))
    elif (event.keysym == "Left"):
        data.direction = (0, -1)
        data.moveRange = list(range(4,8))
    elif (event.keysym == "Right"):
        data.direction = (0, +1)
        data.moveRange = list(range(8,12))
    # for debugging, take one step on any keypress
    elif event.keysym == 'space':
    	takeStep(data)

def timerFired(data):
    if (data.paused or data.gameOver): return
    takeStep(data)

def takeStep(data):
    data.stepnum += 1
    (drow, dcol) = data.direction
    (headRow, headCol) = data.snake[0]
    (newRow, newCol) = (headRow+drow, headCol+dcol)
    if ((newRow < 0) or (newRow >= data.rows) or
        (newCol < 0) or (newCol >= data.cols) or
        ((newRow, newCol) in data.snake)):
        data.gameOver = True
    else:
        data.snake.insert(0, (newRow, newCol))
        if (data.foodPosition == (newRow, newCol)):
            placeFood(data)
        else:
            # didn't eat, so remove old tail (slither forward)
            data.snake.pop()

def placeFood(data):
    data.foodPosition = None
    row0 = random.randint(0, data.rows-1)
    col0 = random.randint(0, data.cols-1)
    for drow in range(data.rows):
        for dcol in range(data.cols):
            row = (row0 + drow) % data.rows
            col = (col0 + dcol) % data.cols
            if (row,col) not in data.snake:
                data.foodPosition = (row, col)
                return

def drawBoard(canvas, data):
    for row in range(data.rows):
        for col in range(data.cols):
            (x0, y0, x1, y1) = getCellBounds(row, col, data)
            canvas.create_rectangle(x0, y0, x1, y1, fill="white")

def drawSnake(canvas, data):
    for (row, col) in data.snake[1:]:
        (x0, y0, x1, y1) = getCellBounds(row, col, data)
        chick = data.stepnum%2
        image = getChick(data,chick)
        canvas.create_image(x0+data.cellWidth/2, y0+10, image=image)
    (hRow,hCol) = data.snake[0]
    (hx0,hy0,hx1,hy1) = getCellBounds(hRow,hCol,data)
    move = data.moveRange[data.stepnum%4]
    image = getImage(data, move)
    canvas.create_image(hx0+data.cellWidth/2,hy0+10, image=image)

def drawFood(canvas, data):
    if (data.foodPosition != None):
        (row, col) = data.foodPosition
        image = getChick(data,2)
        (x0, y0, x1, y1) = getCellBounds(row, col, data)
        canvas.create_image(x0+data.cellWidth/2, y0+20, image=image)

def drawGameOver(canvas, data):
    if (data.gameOver):
        canvas.create_text(data.width/2, data.height/2, text="Game over!",
                           font="Arial 26 bold")
        canvas.create_text(data.width/2,data.height/2+40, text = "모은 병아리 : %d 마리"%(len(data.snake)-1))
        canvas.create_text(data.width/2,data.height/2+70,text = ">>R 키로 재시도<<")


def redrawAll(canvas, data):
#    drawBoard(canvas, data)
    image = getChick(data,3)
    canvas.create_image(data.width/2,data.height/2,image=image)
    drawFood(canvas, data)
    drawSnake(canvas, data)
    drawGameOver(canvas, data)
    if data.paused:
        msg1 = '방향키로 방향을 바꿀 수 있습니다.'
        msg2 = '벽이나 병아리에 부딪히지 않게 조심하며'
        msg4 = '레오와 함께 병아리를 모아주세요.'
        msg5 = '>>>방향키로 이동!<<<'
        canvas.create_text(data.width/2,data.height/2-70,text = msg1)
        canvas.create_text(data.width/2,data.height/2-50,text = msg2)
        canvas.create_text(data.width/2,data.height/2-30,text = msg4)
        canvas.create_text(data.width/2,data.height/2-10,text = msg5)
        msg3 = '화살표 :: 이동\n P :: 일시정지\n R :: 재시작'
        canvas.create_text(30,30,text = msg3,anchor = 'nw')


####################################
# use the run function as-is
####################################

def run(width, height):
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
    # Create root before calling init (so we can create images in init)
    root = Tk()
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 250 # milliseconds
    init(data)
    # create the root and the canvas
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

def playGame(rows,cols):
    cellWidth = 50
    margin = 20
    width = cellWidth * cols + margin
    height =  cellWidth * rows + margin
    run(width,height)

playGame(10,10)
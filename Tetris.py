# events-example0.py
# Barebones timer, mouse, and keyboard events
# hw7c Min Hwang shwang1
# collaboration with Kimberly Lim Jinxia

from tkinter import *
import random
import copy

####################################
# mode dispatcher
####################################

def mousePressed(event, data):
    if (data.mode == "playGame"):
        playGameMousePressed(event, data)
    elif (data.mode == "gameOver"):
        gameOverMousePressed(event, data)
    elif (data.mode == "pause"):
        pauseMousePressed(event, data)

def keyPressed(event, data):
    if (data.mode == "playGame"):
        playGameKeyPressed(event, data)
    elif (data.mode == "gameOver"):
        gameOverKeyPressed(event, data)
    elif (data.mode == "pause"):
        pauseKeyPressed(event, data)

def timerFired(data):
    if (data.mode == "playGame"):
        playGameTimerFired(data)
    elif (data.mode == "gameOver"):
        gameOverTimerFired(data)
    elif (data.mode == "pause"):
        pauseTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "playGame"):
        playGameRedrawAll(canvas, data)
    elif (data.mode == "gameOver"):
        gameOverRedrawAll(canvas, data)
    elif (data.mode == "pause"):
        pauseRedrawAll(canvas, data)

####################################
# customize these functions
####################################

def defPieces():
    #Seven "standard" pieces (tetrominoes)
    iPiece = [[ True,  True,  True,  True]]
    jPiece = [[ True, False, False ],
              [ True, True,  True]]
    lPiece = [[ False, False, True],
              [ True,  True,  True]]
    oPiece = [[ True, True],
              [ True, True]]
    sPiece = [[ False, True, True],
              [ True,  True, False ]]
    tPiece = [[ False, True, False ],
              [ True,  True, True]]
    zPiece = [[ True,  True, False ],
              [ False, True, True]]

    tetrisPieces = [ iPiece, jPiece, lPiece, oPiece, sPiece, tPiece, zPiece ]
    tetrisPieceColors = [ "red", "yellow", "magenta",
                          "pink", "cyan", "green", "orange" ]
    return tetrisPieces,tetrisPieceColors

def init(data):
    data.mode = "playGame"
    data.rows = 15
    data.cols = 10
    data.margin = 50
    data.board=[['blue'for col in range(data.cols)]for row in range(data.rows)]
    data.emptyColor = 'blue'
    data.cellsize = 30
    data.tetrisPieces,data.tetrisPieceColors = defPieces()
    data.fallingPieceRow = 0 #falling from top row
    data.fallingPieceCol = data.cols//2
    newFallingPiece(data)
    data.score = 0

def newFallingPiece(data):
    data.fallingPiece = random.choice(data.tetrisPieces)
    data.fallingPieceColor = random.choice(data.tetrisPieceColors)

def fallingPieceIsLegal(data):
    fallingPieceRows = len(data.fallingPiece)
    fallingPieceCols = len(data.fallingPiece[0])
    for row in range(fallingPieceRows):
        for col in range(fallingPieceCols):
            if data.fallingPiece[row][col]:
                coloredRow = row+data.fallingPieceRow
                coloredCol = col+data.fallingPieceCol-fallingPieceCols//2
                #out of board
                if (coloredRow<0 or coloredCol<0 or 
                    coloredRow>= data.rows or coloredCol>= data.cols):
                    return False
                #board already filled
                elif data.board[coloredRow][coloredCol] != data.emptyColor:
                    return False
    return True

def makeMove(drow,dcol,data):
    data.fallingPieceCol += dcol
    data.fallingPieceRow += drow
    if not fallingPieceIsLegal(data): #if illegal - undo
        data.fallingPieceCol -= dcol
        data.fallingPieceRow -= drow
        return False
    return True

def placeFallingPiece(data):
    fallingPieceRows = len(data.fallingPiece)
    fallingPieceCols = len(data.fallingPiece[0])
    for row in range(fallingPieceRows):
        for col in range(fallingPieceCols):
            if data.fallingPiece[row][col]:
                coloredRow = row+data.fallingPieceRow
                coloredCol = col+data.fallingPieceCol-fallingPieceCols//2
                data.board[coloredRow][coloredCol] = data.fallingPieceColor
                #fill the board with the color

def removeFullRows(data):
    newBoard = []
    count = 0
    for row in data.board:
        if data.emptyColor in row:
            newBoard.append(copy.deepcopy(row))
        else: count += 1 #number of rows that I want to add at the top
    data.score += count **2
    data.board = ([[data.emptyColor for col in range(data.cols)] 
        for i in range(count)]+newBoard)
#################
# Rotating list
#################

def rev(list):
    return list[::-1]

def take_col(dlist,colnum):
    col = []
    for row in range(len(dlist)):
        col.append(dlist[row][colnum])
    return col

def step_one(dlist): #transpose
    stepone = []
    for row in range(len(dlist[0])):
        stepone.append(take_col(dlist,row))
    return stepone

def rotate(dlist): #reverse the rows
    dlist = step_one(dlist)
    steptwo = rev(dlist)
    return steptwo

#################
# Rotating tetris
#################

def rotateFallingPiece(data):
    data.fallingPiece = rotate(data.fallingPiece)
    if not fallingPieceIsLegal(data):
        data.fallingPiece = rotate(rotate(rotate(data.fallingPiece)))
    pass

#####################
# tkinter functions
#####################

def playGameMousePressed(event, data):
    # use event.x and event.y
    pass

def playGameKeyPressed(event, data):
    # use event.char and event.keysym
    # for now, for testing purposes, just choose a new falling piece
    # whenever ANY key is pressed!
    if event.keysym == "Left": makeMove(0,-1,data)
    elif event.keysym == "Right": makeMove(0,1,data)
    elif event.keysym == "Down": makeMove(1,0,data)
    elif event.keysym == "Up": rotateFallingPiece(data)
    elif event.char == 'n': newFallingPiece(data)
    elif event.char == 'p': data.mode = "pause"

def playGameTimerFired(data):
    data.timerDelay = 500
    makeMove(+1,0,data)
    if makeMove(+1,0,data) == False:
        placeFallingPiece(data)
        data.fallingPieceRow = 0 #falling from top row
        data.fallingPieceCol = data.cols//2
        newFallingPiece(data)
        if not fallingPieceIsLegal(data): data.mode = "gameOver"

#####################
# draw functions
#####################

def drawGame(canvas,data):
    canvas.create_rectangle(0,0,data.width,data.height,fill = "orange")
    drawBoard(canvas,data)

def drawBoard(canvas,data):
    for row in range(data.rows):
        for col in range(data.cols):
            drawCell(canvas,data,row,col,color = data.board[row][col])

def drawFallingPiece(canvas,data):
    fallingPieceRows = len(data.fallingPiece)
    fallingPieceCols = len(data.fallingPiece[0])
    for row in range(fallingPieceRows):
        for col in range(fallingPieceCols):
            if data.fallingPiece[row][col]:
                coloredRow = row+data.fallingPieceRow
                coloredCol = col+data.fallingPieceCol-fallingPieceCols//2
                color = data.fallingPieceColor
                drawCell(canvas,data,coloredRow,coloredCol,color)
                
def drawCell(canvas,data,row,col,color):
    bM = 1 #cel outline black margin
    left,top = data.margin + data.cellsize*col,data.margin+data.cellsize*row
    right,bottom = left+data.cellsize,top+data.cellsize
    canvas.create_rectangle(left,top,right,bottom,fill = "black")
    canvas.create_rectangle(left+bM,top+bM,right-bM,bottom-bM,fill = color)
            
def playGameRedrawAll(canvas, data):
    drawGame(canvas,data)
    drawFallingPiece(canvas,data)
    removeFullRows(data)
    canvas.create_text(30,30, text = "Score : %d"%data.score)
    # draw in canvas
    pass


####################################
# Pause
####################################

def pauseMousePressed(event, data):
    pass

def pauseKeyPressed(event, data):
    data.mode = "playGame"
    pass

def pauseTimerFired(data):
    pass

def pauseRedrawAll(canvas, data):
    canvas.create_text(data.width/2,data.height/2,text = "Paused",
        font = "Arial 25 bold")
    canvas.create_text(data.width/2,data.height/2+50,
        text = "(press any key to resume)",font = "Arial 10")


####################################
# Game Over
# Game over screen
####################################

def gameOverMousePressed(event, data):
    pass

def gameOverKeyPressed(event, data):
    data.mode = "playGame"
    init(data)
    pass

def gameOverTimerFired(data):
    pass

def gameOverRedrawAll(canvas, data):
    canvas.create_text(data.width/2,data.height/2,text = "Game Over",
        font = "Arial 25 bold")
    canvas.create_text(data.width/2,data.height/2+50,
        text = "Retry?(press space!)",font = "Arial 10")


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

def playTetris():
    rows = 15
    cols = 10
    cellsize = 30
    margin = 50
    width = cols*cellsize+2*margin
    height = rows*cellsize+2*margin
    run(width,height)

playTetris()


##################################################
##################################################
#Testfunctions
##################################################
##################################################

def testRev():
    assert(rev([1,2,3,4]) == [4,3,2,1])
    assert(rev([1]) == [1])
    assert(rev([]) == [])
    print("rev passed")

def testtake_col():
    assert(take_col([[1,2,3],[2,3,4],[3,4,5]],0) == [1,2,3])
    assert(take_col([[1,2,3],[2,3,4],[3,4,5]],1) == [2,3,4])
    assert(take_col([[1,2,3],[2,3,4],[3,4,5]],2) == [3,4,5])
    print("take_col passed")

def teststep_one():
    assert(step_one([[1,2,3],[2,3,4],[3,4,5]]) == 
        [[1, 2, 3], [2, 3, 4], [3, 4, 5]])
    assert(step_one([[1,2,3],[2,3,4]]) == [[1, 2], [2, 3], [3, 4]])
    assert(step_one([[1,2],[2,3],[3,4]]) == [[1, 2, 3], [2, 3, 4]])
    print("step_one passed")

def testrotate():
    assert(rotate([[1,2,3],[2,3,4],[3,4,5]]) == 
        [[3, 4, 5], [2, 3, 4], [1, 2, 3]])
    assert(rotate([[1,2,3],[2,3,4]]) == [[3, 4], [2, 3], [1, 2]])
    assert(rotate([[1,2],[2,3],[3,4]]) == [[2, 3, 4], [1, 2, 3]])
    print("rotate passed")
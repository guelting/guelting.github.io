# deltaGraphicsDemo2.py

# Fast version of deltaGraphicsDemo1.py
# This time, using delta graphics.

# Displays lots (~1000) random rectangles that do
# not move.

# Then moves an oval over the top of them.  Also changes
# the oval's size and color to show that we can.

# Only delta updated the oval, not the rectangles

from tkinter import *
import random

def drawRectangles(canvas):
    for (left, top, right, bottom, color) in canvas.data["rects"]:
        canvas.create_rectangle(left, top, right, bottom, fill=color)

def drawOval(canvas):
    left = canvas.data["ovalX"] % 400
    width = 5 + left / 5   
    color = hexColor(left * 255/ 400, left * 255/ 400, 0)
    oval = canvas.create_oval(left, 250, left+width, 300, fill=color)
    canvas.data["oval"] = oval # store for delta updates

def deltaDrawOval(canvas):
    oval = canvas.data["oval"]
    left = canvas.data["ovalX"] % 400
    width = 5 + left / 5   
    color = hexColor(left * 255/ 400, left * 255/ 400, 0)
    # change oval's bounds
    canvas.coords(oval, (left, 250, left+width, 300) )
    # change oval's color
    canvas.itemconfig(oval, fill=color)
    
def redrawAll(canvas):
    # called once, by init
    canvas.delete(ALL)
    drawRectangles(canvas)
    drawOval(canvas)

def deltaDraw(canvas):
    deltaDrawOval(canvas)
    
def timerFired(canvas):
    canvas.data["ovalX"] += 10
    deltaDraw(canvas)
    delay = 10 # milliseconds
    canvas.after(delay, timerFired, canvas)

def hexColor(red, green, blue):
    return ("#%02x%02x%02x" % (red, green, blue))

def randomColor():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return hexColor(red, green, blue)

def init(canvas):
    canvas.width = canvas.winfo_reqwidth()-4
    canvas.height = canvas.winfo_reqheight()-4
    rects = []
    rectCount = 1000
    for i in range(rectCount):
        left = random.randint(0,450)
        right = left + random.randint(5,50)
        top = random.randint(0,450)
        bottom = top + random.randint(5,50)
        color = randomColor()
        rects.append((left, top, right, bottom, color))
    canvas.data["rects"] = rects
    canvas.data["ovalX"] = 200
    redrawAll(canvas)

########### copy-paste below here ###########

def run():
    # create the root and the canvas
    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    canvas = Canvas(root, width=500, height=500)
    canvas.pack(fill=BOTH, expand=YES)
    # Store canvas in root and in canvas itself for callbacks
    root.canvas = canvas.canvas = canvas
    # Set up canvas data and call init
    canvas.data = { }
    init(canvas)
    # set up events
    # root.bind("<Button-1>", leftMousePressed)
    # root.bind("<KeyPress>", keyPressed)
    timerFired(canvas)
    # and launch the app
    root.mainloop()  # This call BLOCKS (so your program waits until you close the window!)

run()
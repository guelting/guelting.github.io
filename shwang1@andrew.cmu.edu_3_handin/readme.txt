README - Bomberman

1. 
This program uses python3. Python3 must be installed beforehand.
The module used are sockets and tkinter, which comes with python3 installation. Therefore no further installs are needed.

2.
Bomberman is multi-player(up to 4 people) battle royal game based on server.
If you share IP address, you can play the game with anybody however far you are apart.

3.
Once python3 is installed, the running process follows:
 (a) Open terminal and navigate to the directory with .py files and images folder is. 
    (a)-1 images folder must be unzipped(if it was in zip file) and should stay on same directory with client.py
    (a)-2 If you are windows user, use cmd 
 (b) run ".py" files with python3 in terminal (eg. >>>python3 host.py)
    (b)-1 host.py file must be run first. Type your public IP address. Make sure you share this informaiton with other clients.
             This file is only required to run once on one computer, the computer that opens the server.
    (b)-2 Once host.py is running and client.py is open, other process are self-explanatory. Follow the instructions in game.

4. 
In game
 (a) Start screen
    (a)-1 click or use [arrow key+enter] to select. 
 (b) Character select
    (b)-1 select your character and click [go button] or use [arrow key+enter].
 (c) Ready connect
    (c)-1 type 12 digit IP address (with dots eg. [111.111.111.111]) you want to connect. Make sure you don't get it wrong. 
             Press enter when you are done.
    (c)-2 once connected you will see the instuctions on screen
        (c)-2-A. If you are not the first player(1P), click the screen to get ready and wait.
        (c)-2-B. If you are 1P, you will get to select the map. Use arrow keys to select the map you want.
                      When every players are ready, the sign on the screen will change to [Go]. Click once more to start the game.
 (d) Game
    (d)-1 Move with arrow keys
    (d)-2 Place bomb with space bar. bomb explodes in cross shape.
    (d)-3 try to kill all your opponents.
    (d)-4 You die when you are exposed to the flame too long. Until you can't see your character on screen it means you are alive.
    (d)-5 Game ends when there are only one surviver.



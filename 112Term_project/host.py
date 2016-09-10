import socket
from _thread import *
from queue import Queue

HOST = "128.237.185.120"
PORT = 50014
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
server.listen(BACKLOG)
print("looking for connection")

clientele = []
cID = 0
serverChannel = Queue(100)

def handleClient(client, cID, serverChannel):
    client.setblocking(1)
    msg = ""
    while True:
        msg += client.recv(100).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            sendMsg = str(cID) + " " + readyMsg
            serverChannel.put(sendMsg)
            command = msg.split("\n")

def serverThread(clientele, serverChannel):
    while True:
        msg = serverChannel.get(True, None)
        print("msg recv: ", msg)
        senderID, msg = int(msg.split()[0]), " ".join(msg.split()[1:])
        if (msg):
            for (client,cID) in clientele:
                if cID != senderID:
                    sendMsg = str(senderID) + " " + msg + "\n"
                    client.send(sendMsg.encode("UTF-8"))
            serverChannel.task_done()


start_new_thread(serverThread,(clientele,serverChannel))

while True:
    client,address = server.accept()
    for (oldClient,userID) in clientele:
        msgToOld = "newPlayer " + str(cID) + " entered\n"
        msgToNew = "newPlayer " + str(userID) + " entered\n"
        oldClient.send(msgToOld.encode("UTF-8"))
        client.send(msgToNew.encode("UTF-8"))
    IDmsg = "Welcome Player " + str(cID) + "\n"
    client.send(IDmsg.encode("UTF-8"))
    clientele.append((client,cID))
    print("connection recieved")
    start_new_thread(handleClient,(client,cID,serverChannel,))
    cID += 1
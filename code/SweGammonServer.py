import threading
import time
import socket
import json
import re
import Queue

threadLock = threading.Lock()

class Users(object):
    def __init__(self):
        self.users = []
    def userNameExist(self, userName):
        if self.users is None or len(self.users) == 0:
            return False
        for user in self.users:
            if user.userName == userName:
                return True
        return False

    def findUser(self, userName):
        for user in self.users:
            if user.userName == userName:
                return user
        return None

    def findUserFromConnection(self, con):
        for user in self.users:
            if user.con == con:
                return user
        return None

    def addUser(self, user):
        self.users.append(user)

class User(object):
    def __init__(self, userName, con, address):
        self.userType = ''
        self.userName = userName
        self.userIpAddress = address[0]
        self.userPort = address[1]
        self.userHeartbeatFails = 0
        self.con = con
        self.seqid = 0
        self.color = ' '

class GameState(object):
    def __init__(self):
        self.dice = [0,0]
        self.buttons = [[1,0,0],[0,0,0]]
        #[white,black] pieces
        #first tuple is not used. it is for index usability.
        self.positions = [[0,0],
                          [2,0],[0,0],[0,0],[0,0],[0,0],[0,5],
                          [0,0],[0,3],[0,0],[0,0],[0,0],[5,0],
                          [0,5],[0,0],[0,0],[0,0],[3,0],[0,0],
                          [5,0],[0,0],[0,0],[0,0],[0,0],[0,2]]
        self.gatheringZone = [0,0]
        self.brokenZone = [0,0]

class Game(object):
    def __init__(self):
        self.gameState = GameState()
        self.previousGameState = GameState()
        self.whitePlayer = None
        self.blackPlayer = None
        self.watchers = []

    def setPlayers(self, user1, user2):
        self.whitePlayer = user1
        self.blackPlayer = user2

    def addWatcher(self, user):
        self.watchers.append(user)



class WaitingRoom(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.players = Queue.Queue()
        self.watchers = Queue.Queue()

    def addToQueue(self, user):
        if user.userType == 'P':
            self.players.put(user)
        elif user.userType == 'W':
            self.watchers.put(user)
    def run(self):
        while running:
            time.sleep(3)
            if self.players.qsize() > 1:
                game = Game()
                whitePlayer = self.players.get()
                whitePlayer.color = 'W'
                blackPlayer = self.players.get()
                blackPlayer.color = 'B'
                game.setPlayers(whitePlayer, blackPlayer)
                ServerCommandHandler.sendChoosePlayResponse(game, whitePlayer, blackPlayer)


class JsonDict(dict):
    def __init__(self, seqid):
        dict.__init__(self)
        self["seqid"] = seqid

class ServerCommandHandler(object):
    def requestParser(self,req):
        reqList = re.split('  ',req)
        threadLock.acquire
        print reqList
        threadLock.release
        return reqList[0], reqList[1]

    def handleCommand(self, req, con, address):
        try:
            command, jsonString = self.requestParser(req)
            threadLock.acquire
            print command + ' ' + jsonString
            threadLock.release
            decoded = json.loads(jsonString)
            if command == 'LOGIN':
                self.receiveLoginCommand(decoded, con, address)
            elif command == 'SPLAY':
                self.receiveChoosePlayCommand(decoded, con, address)
        except ValueError, e:
            print 'valueerror:' +  e.message
        except KeyError, e:
            print 'keyerror:' +  e.message
        except TypeError, e:
            print 'typeerror:' +  e.message

    def receiveLoginCommand(self, decoded, con, address):
        seqid = decoded['seqid']
        userName = decoded['username']
        if users.userNameExist(userName):
            self.sendLoginResponse(True, seqid, userName, con)
        else:
            user = User(userName, con, address)
            users.addUser(user)
            self.sendLoginResponse(False, seqid, userName, con)

    def sendLoginResponse(self, error, seqid, userName, con):
        self.dict = JsonDict(seqid)
        if error:
            self.dict["message"] = userName + ' already exists. Please choose another username.'

        jsonPart = json.dumps(self.dict)
        message = 'LOGSC  ' + jsonPart
        sendManager = ServerSendManager(con, message)
        threads.append(sendManager)
        sendManager.start()

    def receiveChoosePlayCommand(self, decoded, con, address):
        seqid = decoded['seqid']
        user = users.findUserFromConnection(con)
        if user == None:
            self.sendErrorResponse(seqid, 'Technical error. User not connected', con)
        else:
            user.userType = 'P'
            user.seqid = seqid
            waitingRoom.addToQueue(user)

    @staticmethod
    def sendChoosePlayResponse(game, user, opponentUser):
        dict1 = JsonDict(user.seqid)
        dict1["color"] = user.color
        dict1["opponent"] = opponentUser.userName
        dict1["gamestate"] = game.gameState.__dict__
        jsonPart = json.dumps(dict1)
        message = 'SPLSC  ' + jsonPart
        sendManager1 = ServerSendManager(user.con, message)
        threads.append(sendManager1)
        sendManager1.start()

        dict2 = JsonDict(opponentUser.seqid)
        dict2["color"] = opponentUser.color
        dict2["opponent"] = user.userName
        dict2["gamestate"] = game.gameState.__dict__
        jsonPart = json.dumps(dict2)
        message = 'SPLSC  ' + jsonPart
        sendManager2 = ServerSendManager(opponentUser.con, message)
        threads.append(sendManager2)
        sendManager2.start()

    def sendErrorResponse(self, seqid, errorMessage, con):
        self.dict = JsonDict(seqid)
        self.dict["message"] = errorMessage
        jsonPart = json.dumps(self.dict)
        message = 'ERROR  ' + jsonPart
        sendManager = ServerSendManager(con, message)
        threads.append(sendManager)
        sendManager.start()



class ServerReceiveManager(threading.Thread):
    def __init__(self, con, address):
        threading.Thread.__init__(self)
        self.c = con
        self.address = address
    def run(self):
        print "Starting ServerReceiveManager"
        while running:
            req = self.c.recv(1024)
            serverCommandHandler = ServerCommandHandler()
            serverCommandHandler.handleCommand(req, self.c, self.address)
        print "Exiting ServerReceiveManager"

class ServerSendManager(threading.Thread):
    def __init__(self, con, message):
        threading.Thread.__init__(self)
        self.c = con
        self.message = message
    def run(self):
        threadLock.acquire
        print "Starting ServerSendManager"
        threadLock.release
        self.c.sendall(self.message)
        threadLock.acquire
        print "Exiting ServerSendManager"
        threadLock.release
        threads.remove(self)


threads = []
running = True
users = Users()

waitingRoom = WaitingRoom()
threads.append(waitingRoom)
waitingRoom.start()

s = socket.socket()
host = socket.gethostname()
port = 7500
s.bind((host, port))

s.listen(100)

while running:
    c, address = s.accept()
    print ("Got connection from" + str(address))
    receiveManager = ServerReceiveManager(c, address)
    threads.append(receiveManager)
    receiveManager.start()

# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
running = False
s.close()
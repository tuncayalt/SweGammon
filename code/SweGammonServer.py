import threading
import time
import socket
import json
import re
import Queue
from random import randint
import copy

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
                          [5,0],[0,0],[0,0],[0,0],[0,0],[0,2],
                          [0,0]]
        self.gatheringZone = [0,0]
        self.brokenZone = [0,0]

    def buttonsAfterSendMove(self, color):
        if color == 'W':
            self.buttons[0][0] = 0
            self.buttons[0][1] = 0
            self.buttons[0][2] = 0
            self.buttons[1][0] = 1
            self.buttons[1][1] = 0
            self.buttons[1][2] = 1
        else:
            self.buttons[0][0] = 1
            self.buttons[0][1] = 0
            self.buttons[0][2] = 1
            self.buttons[1][0] = 0
            self.buttons[1][1] = 0
            self.buttons[1][2] = 0

    def parse(self, bgNotationString):
        #sample backgammon notation: 2-2: 22/20* bar/22 1/off 2/off
        bgNotationString = bgNotationString.strip()
        returnList = re.split('\* |-|: | |/', bgNotationString)
        return returnList

    def checkWinning(self):
        if self.gatheringZone[0] >= 15:
            self.buttons[0][0] = 0
            self.buttons[1][0] = 0
            return [True, False]
        elif self.gatheringZone[1] >= 15:
            self.buttons[0][0] = 0
            self.buttons[1][0] = 0
            return [False, True]
        return [False, False]

    def checkAfterMove(self):
        totalPieces = 0
        for position in self.positions:
            if position[0] < 0 or position[1] < 0:
                return True
            totalPieces += position[0] + position[1]
        if self.gatheringZone[0] < 0 or self.brokenZone[0] < 0:
            return True
        if self.gatheringZone[1] < 0 or self.brokenZone[1] < 0:
            return True
        totalPieces += self.gatheringZone[0] + self.brokenZone[0]
        totalPieces += self.gatheringZone[1] + self.brokenZone[1]
        if totalPieces != 30:
            return True
        return False


    def movePieces(self, color, bgNotationString):
        #sample move = ['4', '2', '22', '18', '6', '2']
        move = self.parse(bgNotationString)

        #moving white color
        if color == 'W':
            threadLock.acquire
            print('white plays')
            threadLock.release
            for piece in range(2,len(move),2):
                if move[piece] == 'bar':
                    #from the broken zone
                    if self.brokenZone[0] > 0:
                        self.brokenZone[0] -= 1
                        self.positions[25 - int(move[piece + 1])][0] += 1
                elif move[piece + 1] == 'off':
                    self.positions[25 - int(move[piece])][0] -= 1
                    self.gatheringZone[0] += 1
                else:
                    self.positions[25 - int(move[piece])][0] -= 1
                    self.positions[25 - int(move[piece + 1])][0] += 1
            #breaking the black piece
            for position in self.positions:
                if position[0] > 0 and position[1] == 1:
                    position[1] = 0
                    self.brokenZone[1] += 1
        #moving black color
        else:
            threadLock.acquire
            print('black plays')
            threadLock.release
            for piece in range(2,len(move),2):
                if move[piece] == 'bar':
                    #from the broken zone
                    if self.brokenZone[1] > 0:
                        self.brokenZone[1] -= 1
                        self.positions[int(move[piece + 1])][1] += 1
                elif move[piece + 1] == 'off':
                    self.positions[int(move[piece])][1] -= 1
                    self.gatheringZone[1] += 1
                else:
                    self.positions[int(move[piece])][1] -= 1
                    self.positions[int(move[piece + 1])][1] += 1
            #breaking the white piece
            for position in self.positions:
                if position[1] > 0 and position[0] == 1:
                    position[0] = 0
                    self.brokenZone[0] += 1
        return self.checkAfterMove()

class Games(object):
    def __init__(self):
        self.games = []

    def addGame(self, game):
        self.games.append(game)

    def findGameFromPlayer(self, user):
        for game in self.games:
            if game.whitePlayer == user or game.blackPlayer == user:
                return game
        return None

    def findGameFromWatcher(self, user):
        for game in self.games:
            if len(game.watchers) != 0:
                for watcher in game.watchers:
                    if watcher == user:
                        return game
        return None

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
            time.sleep(1)
            if self.players.qsize() > 1:
                game = Game()
                whitePlayer = self.players.get()
                whitePlayer.color = 'W'
                blackPlayer = self.players.get()
                blackPlayer.color = 'B'
                game.setPlayers(whitePlayer, blackPlayer)
                games.addGame(game)
                ServerCommandHandler.sendChoosePlayResponse(game, whitePlayer, blackPlayer)

            if self.watchers.qsize() > 0 and len(games.games) > 0:
                randGameNumber = randint(0,len(games.games) - 1)
                watcher = self.watchers.get()
                games.games[randGameNumber].addWatcher(watcher)
                ServerCommandHandler.sendChooseWatchResponse(game, watcher)

class JsonDict(dict):
    def __init__(self, seqid):
        dict.__init__(self)
        self["seqid"] = seqid

class ServerCommandHandler(object):
    def requestParser(self,req):
        reqList = re.split('  ',req)
        return reqList[0], reqList[1]

    def checkInput(self, con, decoded):
        seqid = decoded['seqid']
        user = users.findUserFromConnection(con)
        if user == None:
            self.sendErrorResponse(seqid, 'Technical error. User not connected', con)
        else:
            user.seqid = seqid
        return seqid, user

    def handleCommand(self, req, con, address):
        try:
            command, jsonString = self.requestParser(req)
            # threadLock.acquire
            # print command + ' ' + jsonString
            # threadLock.release
            decoded = json.loads(jsonString)
            if command == 'LOGIN':
                self.receiveLoginCommand(decoded, con, address)
            elif command == 'SPLAY':
                self.receiveChoosePlayCommand(decoded, con, address)
            elif command == 'SWATC':
                self.receiveChooseWatchCommand(decoded, con, address)
            elif command == 'DROLL':
                self.receiveRollDiceCommand(decoded, con, address)
            elif command == 'SMOVE':
                self.receiveSendMoveCommand(decoded, con, address)
            elif command == 'WMOVE':
                self.receiveWrongMoveAlertCommand(decoded, con, address)
            elif command == 'HBESC':
                self.receiveHeartbeatResponse(decoded, con, address)

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
        seqid, user = self.checkInput(con, decoded)
        if user != None:
            user.userType = 'P'
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

    def receiveChooseWatchCommand(self, decoded, con, address):
        seqid, user = self.checkInput(con, decoded)
        if user != None:
            user.userType = 'W'
            waitingRoom.addToQueue(user)

    @staticmethod
    def sendChooseWatchResponse(game, user):
        dict1 = JsonDict(user.seqid)
        dict1["player1"] = game.whitePlayer.userName
        dict1["player2"] = game.blackPlayer.userName
        dict1["gamestate"] = game.gameState.__dict__
        jsonPart = json.dumps(dict1)
        message = 'SWASC  ' + jsonPart
        sendManager1 = ServerSendManager(user.con, message)
        threads.append(sendManager1)
        sendManager1.start()

    def receiveRollDiceCommand(self, decoded, con, address):
        seqid, user = self.checkInput(con, decoded)
        if user == None:
            return
        game = games.findGameFromPlayer(user)
        if game == None:
            self.sendErrorResponse(seqid, 'Technical error. Game not found', con)
            return
        elif game.gameState.buttons[0][0] != 1 and user.color == 'W':
            self.sendErrorResponse(seqid, 'Technical error. dice button does not match1', con)
            return
        elif game.gameState.buttons[1][0] != 1 and user.color == 'B':
            self.sendErrorResponse(seqid, 'Technical error. dice button does not match2', con)
            return

        randDice1 = randint(1,6)
        randDice2 = randint(1,6)
        game.gameState.dice = [randDice1, randDice2]
        if user.color == 'W':
            game.gameState.buttons[0][0] = 0
            game.gameState.buttons[0][1] = 1
            game.gameState.buttons[0][2] = 0
            game.gameState.buttons[1][0] = 0
            game.gameState.buttons[1][1] = 0
            game.gameState.buttons[1][2] = 0
        else:
            game.gameState.buttons[0][0] = 0
            game.gameState.buttons[0][1] = 0
            game.gameState.buttons[0][2] = 0
            game.gameState.buttons[1][0] = 0
            game.gameState.buttons[1][1] = 1
            game.gameState.buttons[1][2] = 0

        self.sendRollDiceResponse(user, game)

    def sendRollDiceResponse(self, user, game):
        dict = JsonDict(user.seqid)
        dict["gamestate"] = game.gameState.__dict__
        jsonPart = json.dumps(dict)
        message = 'DROSC  ' + jsonPart
        sendManager1 = ServerSendManager(game.whitePlayer.con, message)
        threads.append(sendManager1)
        sendManager1.start()
        sendManager2 = ServerSendManager(game.blackPlayer.con, message)
        threads.append(sendManager2)
        sendManager2.start()
        for watcher in game.watchers:
            sendManager = ServerSendManager(watcher.con, message)
            threads.append(sendManager)
            sendManager.start()

    def receiveSendMoveCommand(self, decoded, con, address):
        seqid, user = self.checkInput(con, decoded)
        moveString = decoded["move"]
        if user == None:
            return
        game = games.findGameFromPlayer(user)
        if game == None:
            self.sendErrorResponse(seqid, 'Technical error. Game not found', con)
            return
        elif game.gameState.buttons[0][1] != 1 and user.color == 'W':
            self.sendErrorResponse(seqid, 'Technical error. send move button does not match1', con)
            return
        elif game.gameState.buttons[1][1] != 1 and user.color == 'B':
            self.sendErrorResponse(seqid, 'Technical error. send move button does not match2', con)
            return
        elif not moveString:
            self.sendErrorResponse(seqid, 'Technical error. move is invalid1', con)
            return

        tempGameState = copy.deepcopy(game.gameState)
        game.gameState.buttonsAfterSendMove(user.color)
        error = game.gameState.movePieces(user.color, moveString)
        if error:
            self.sendErrorResponse(seqid, 'Technical error. move is invalid2', con)
            game.gameState = copy.deepcopy(tempGameState)
            threadLock.acquire
            print game.gameState
            threadLock.release
            return
        wingame = game.gameState.checkWinning()
        if wingame == None:
            self.sendErrorResponse(seqid, 'Technical error. move is invalid3', con)
            game.gameState = copy.deepcopy(tempGameState)
            threadLock.acquire
            print game.gameState
            threadLock.release
        else:
            self.sendSendMoveResponse(user, game, wingame)
            game.previousGameState = copy.deepcopy(tempGameState)

    def sendSendMoveResponse(self, user, game, wingame):
        dict = JsonDict(user.seqid)
        dict["wingame"] = wingame
        dict["gamestate"] = game.gameState.__dict__
        jsonPart = json.dumps(dict)
        message = 'SMOSC  ' + jsonPart
        sendManager1 = ServerSendManager(game.whitePlayer.con, message)
        threads.append(sendManager1)
        sendManager1.start()
        sendManager2 = ServerSendManager(game.blackPlayer.con, message)
        threads.append(sendManager2)
        sendManager2.start()
        for watcher in game.watchers:
            sendManager = ServerSendManager(watcher.con, message)
            threads.append(sendManager)
            sendManager.start()

    def receiveWrongMoveAlertCommand(self, decoded, con, address):
        seqid, user = self.checkInput(con, decoded)
        if user == None:
            return
        game = games.findGameFromPlayer(user)
        if game == None:
            self.sendErrorResponse(seqid, 'Technical error. Game not found', con)
            return
        elif game.gameState.buttons[0][2] != 1 and user.color == 'W':
            self.sendErrorResponse(seqid, 'Technical error. wrongmove button does not match1', con)
            return
        elif game.gameState.buttons[1][2] != 1 and user.color == 'B':
            self.sendErrorResponse(seqid, 'Technical error. wrongmove button does not match2', con)
            return

        game.gameState = copy.deepcopy(game.previousGameState)

        self.sendWrongMoveAlertResponse(user, game)

    def sendWrongMoveAlertResponse(self, user, game):
        dict = JsonDict(user.seqid)
        dict["gamestate"] = game.gameState.__dict__
        jsonPart = json.dumps(dict)
        message = 'WMOSC  ' + jsonPart
        sendManager1 = ServerSendManager(game.whitePlayer.con, message)
        threads.append(sendManager1)
        sendManager1.start()
        sendManager2 = ServerSendManager(game.blackPlayer.con, message)
        threads.append(sendManager2)
        sendManager2.start()
        for watcher in game.watchers:
            sendManager = ServerSendManager(watcher.con, message)
            threads.append(sendManager)
            sendManager.start()

    @staticmethod
    def sendHeartbeatCommand(seqid, con):
        dict = JsonDict(seqid)
        jsonPart = json.dumps(dict)
        message = 'HBEAT  ' + jsonPart
        sendManager = ServerSendManager(con, message)
        threads.append(sendManager)
        sendManager.start()

    def receiveHeartbeatResponse(self, decoded, con, address):
        seqid = decoded['seqid']
        for thread in threads:
            if type(thread) is HeartbeatSendManager:
                if thread.c == con:
                    thread.resetHeartbeatFails()
        user = users.findUserFromConnection(con)
        if user != None:
            user.heartBeatFails = -1

    def sendErrorResponse(self, seqid, errorMessage, con):
        self.dict = JsonDict(seqid)
        self.dict["message"] = errorMessage
        jsonPart = json.dumps(self.dict)
        message = 'ERROR  ' + jsonPart
        sendManager = ServerSendManager(con, message)
        threads.append(sendManager)
        sendManager.start()

class HeartbeatSendManager(threading.Thread):
    def __init__(self, con, address):
        threading.Thread.__init__(self)
        self.c = con
        self.address = address
        self.seqid = 0
        self.heartbeatFails = -1
        self.running = True

    def prepHeartbeatMessage(self, seqid):
        dict = JsonDict(seqid)
        jsonPart = json.dumps(dict)
        message = 'HBEAT  ' + jsonPart
        return message

    def resetHeartbeatFails(self):
        self.heartbeatFails = -1

    def disconnectUser(self):
        print 'disconnect01'
        self.running = False;
        for thread in threads:
            if type(thread) is ServerReceiveManager:
                if thread.c == self.c:
                    thread.running = False
                    thread.join()
        user = users.findUserFromConnection(self.c)
        if user == None:
            c.close()
            print 'disconnect02'
            return
        user.heartbeatFails = 6
        game = games.findGameFromWatcher(user)
        if game != None:
            game.watchers.remove(user)
            users.users.remove(user)
            c.close()
            print 'disconnect03'
            return
        game = games.findGameFromPlayer(user)
        if game == None:
            users.users.remove(user)
            c.close()
            print 'disconnect04'
            return

        games.games.remove(game)
        if user.color == 'W':
            waitingRoom.addToQueue(game.blackPlayer)
        elif user.color == 'B':
            waitingRoom.addToQueue(game.whitePlayer)
        for watcher in game.watchers:
            waitingRoom.addToQueue(watcher)
        users.users.remove(user)
        print 'disconnect05'
        c.close()

    def run(self):
        print "Starting HeartbeatManager"
        while self.running:
            time.sleep(5)
            self.seqid += 1
            self.heartbeatFails += 1
            if self.heartbeatFails > 6:
                self.disconnectUser()
            else:
                ServerCommandHandler.sendHeartbeatCommand(self.seqid, self.c)
        print "Exiting HeartbeatManager"

class ServerReceiveManager(threading.Thread):
    def __init__(self, con, address):
        threading.Thread.__init__(self)
        self.c = con
        self.address = address
        self.running = True
    def run(self):
        print "Starting ServerReceiveManager"
        while self.running:
            req = self.c.recv(1024)
            threadLock.acquire
            print 'Receiving: ' + req
            threadLock.release
            serverCommandHandler = ServerCommandHandler()
            serverCommandHandler.handleCommand(req, self.c, self.address)
        self.c.close()
        threads.remove(self)
        self.join()
        print "Exiting ServerReceiveManager"

class ServerSendManager(threading.Thread):
    def __init__(self, con, message):
        threading.Thread.__init__(self)
        self.c = con
        self.message = message
    def run(self):
        threadLock.acquire
        print "Sending  : " + self.message
        threadLock.release
        self.c.sendall(self.message)
        threads.remove(self)


threads = []
running = True
users = Users()
games = Games()

waitingRoom = WaitingRoom()
threads.append(waitingRoom)
waitingRoom.start()

s = socket.socket()
host = socket.gethostname()
port = 7500
s.bind((host, port))

s.listen(200)

while running:
    c, address = s.accept()
    print ("Got connection from" + str(address))
    receiveManager = ServerReceiveManager(c, address)
    threads.append(receiveManager)
    receiveManager.start()
    heartbeatSendManager = HeartbeatSendManager(c, address)
    threads.append(heartbeatSendManager)
    heartbeatSendManager.start()

# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
running = False
s.close()
from Tkinter import *
import tkMessageBox
import threading
import socket
import json
import time

threadLock = threading.Lock()

class GameState(object):
    def __init__(self):
        self.dice = [0,0]
        self.buttons = [[1,0,0],[0,0,0]]
        #[white,black] pieces
        #first and last tuples are not used. it is for index usability.
        self.positions = [[0,0],
                          [2,0],[0,0],[0,0],[0,0],[0,0],[0,5],
                          [0,0],[0,3],[0,0],[0,0],[0,0],[5,0],
                          [0,5],[0,0],[0,0],[0,0],[3,0],[0,0],
                          [5,0],[0,0],[0,0],[0,0],[0,0],[0,2],
                          [0,0]]
        self.gatheringZone = [0,0]
        self.brokenZone = [0,0]

class SendManager(threading.Thread):
    def __init__(self, message):
        threading.Thread.__init__(self)
        self.message = message
    def run(self):
        threadLock.acquire
        print "Sending  : " + self.message
        threadLock.release
        s.send(self.message)

class ReceiveManager(threading.Thread):
    def run(self):
        while True:
            incoming = s.recv(1024)
            threadLock.acquire
            print 'Receiving: ' + incoming
            threadLock.release
            commandHandler = CommandHandler(incoming)
            threads.append(commandHandler)
            commandHandler.start()

class Session(object):
    def __init__(self):
        self.seqid = 0
        self.userType = ''
        self.userName = ''
        self.color = ''
        self.serverIp = ''
        self.serverPort = ''
        self.gameState = GameState()

    def initGameState(self):
        self.gameState = None
        self.gameState = GameState()

class JsonDict(dict):
    def __init__(self):
        dict.__init__(self)
        session.seqid += 1
        self["seqid"] = session.seqid

class CommandHandler(threading.Thread):
    def __init__(self, message):
        threading.Thread.__init__(self)
        self.message = message

    def requestParser(self,message):
        reqList = re.split('  ', message)
        return reqList[0], reqList[1]

    def run(self):
        self.handleCommand(self.message)

    def handleCommand(self, message):
        try:
            command, jsonString = self.requestParser(message)
            decoded = json.loads(jsonString)
            #session.initGameState()
            if command == 'LOGSC':
                self.receiveLoginResponse(decoded)
            elif command == 'SPLSC':
                self.receiveChoosePlayResponse(decoded)
            elif command == 'SWASC':
                self.receiveChooseWatchResponse(decoded)
            elif command == 'DROSC':
                self.receiveRollDiceResponse(decoded)
            elif command == 'SMOSC':
                self.receiveSendMoveResponse(decoded)
            elif command == 'WMOSC':
                self.receiveWrongMoveAlertResponse(decoded)
            elif command == 'HBEAT':
                self.receiveHeartbeatResponse(decoded)

        except ValueError, e:
            print 'valueerror:' +  e.message
        except KeyError, e:
            print 'keyerror:' +  e.message
        except TypeError, e:
            print 'typeerror:' +  e.message

    @staticmethod
    def sendMessage(command, jsonPart):
        message = command + '  ' + jsonPart
        sendManager = SendManager(message)
        threads.append(sendManager)
        sendManager.start()

    @staticmethod
    def sendLoginCommand():
        dict = JsonDict()
        dict["username"] = session.userName
        jsonPart = json.dumps(dict)
        CommandHandler.sendMessage('LOGIN', jsonPart)

    @staticmethod
    def sendChoosePlayCommand():
        dict = JsonDict()
        jsonPart = json.dumps(dict)
        CommandHandler.sendMessage('SPLAY', jsonPart)

    @staticmethod
    def sendChooseWatchCommand():
        dict = JsonDict()
        jsonPart = json.dumps(dict)
        CommandHandler.sendMessage('SWATC', jsonPart)

    @staticmethod
    def sendRollDiceCommand():
        dict = JsonDict()
        jsonPart = json.dumps(dict)
        CommandHandler.sendMessage('DROLL', jsonPart)
    @staticmethod
    def sendSendMoveCommand(bgNotationString):
        dict = JsonDict()
        dict["move"] = bgNotationString
        jsonPart = json.dumps(dict)
        CommandHandler.sendMessage('SMOVE', jsonPart)
    @staticmethod
    def sendWrongMoveAlertCommand():
        dict = JsonDict()
        jsonPart = json.dumps(dict)
        CommandHandler.sendMessage('WMOVE', jsonPart)

    def sendHeartbeatResponse(self, serverSeqId):
        dict1 = dict()
        dict1["seqid"] = serverSeqId
        jsonPart = json.dumps(dict1)
        CommandHandler.sendMessage('HBESC', jsonPart)

    def receiveLoginResponse(self, decoded):
        seqid = decoded['seqid']
        try:
            message = decoded['message']
        except:
            message = None
        if message == None:
            sweGammonGui.showConnectedScreen()
        else:
            sweGammonGui.showLoginScreen(seqid, message)

    def getGameStateFromResponse(self, decoded):
        session.gameState.dice[0] = decoded['gamestate']['dice'][0]
        session.gameState.dice[1] = decoded['gamestate']['dice'][1]
        for i in range(0, len(session.gameState.buttons)):
            session.gameState.buttons[i][0] = decoded['gamestate']['buttons'][i][0]
            session.gameState.buttons[i][1] = decoded['gamestate']['buttons'][i][1]
            session.gameState.buttons[i][2] = decoded['gamestate']['buttons'][i][2]
        for i in range(0, len(session.gameState.positions)):
            session.gameState.positions[i][0] = decoded['gamestate']['positions'][i][0]
            session.gameState.positions[i][1] = decoded['gamestate']['positions'][i][1]
        session.gameState.brokenZone[0] = decoded['gamestate']['brokenZone'][0]
        session.gameState.brokenZone[1] = decoded['gamestate']['brokenZone'][1]
        session.gameState.gatheringZone[0] = decoded['gamestate']['gatheringZone'][0]
        session.gameState.gatheringZone[1] = decoded['gamestate']['gatheringZone'][1]

    def receiveChoosePlayResponse(self, decoded):
        seqid = decoded['seqid']
        session.userType = 'P'
        session.color = decoded['color']
        session.opponent = decoded['opponent']
        self.getGameStateFromResponse(decoded)
        sweGammonGui.showPlayerGameScreen()

    def receiveChooseWatchResponse(self, decoded):
        seqid = decoded['seqid']
        session.userType = 'W'
        session.color = 'W'
        session.userName = decoded['player1']
        session.opponent = decoded['player2']
        self.getGameStateFromResponse(decoded)
        sweGammonGui.showWatcherGameScreen()
    #
    def receiveRollDiceResponse(self, decoded):
        seqid = decoded['seqid']
        self.getGameStateFromResponse(decoded)
        if session.userType == 'W':
            sweGammonGui.showWatcherGameScreen()
        else:
            sweGammonGui.showPlayerGameScreen()
    #
    def receiveSendMoveResponse(self, decoded):
        seqid = decoded['seqid']
        winGame = [False, False]
        winGame[0] = decoded['wingame'][0]
        winGame[1] = decoded['wingame'][1]
        self.getGameStateFromResponse(decoded)
        if session.userType == 'W':
            sweGammonGui.showWatcherGameScreen()
        else:
            sweGammonGui.showPlayerGameScreen()
    #
    def receiveWrongMoveAlertResponse(self, decoded):
        seqid = decoded['seqid']
        self.getGameStateFromResponse(decoded)
        if session.userType == 'W':
            sweGammonGui.showWatcherGameScreen()
        else:
            sweGammonGui.showPlayerGameScreen()

    def receiveHeartbeatResponse(self, decoded):
        seqid = decoded['seqid']
        self.sendHeartbeatResponse(seqid)


class GUIManager(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, background = "white")
        self.master = master
        self.grid(column=0, row=0, sticky=(N, W, E, S))

    def initialize(self):
        self.showLoginScreen(None)

    def showLoginScreen(self, alreadyExistMessage):
        threadLock.acquire
        for widget in widgets:
            widget.grid_forget

        self.lblGreetings = Label(self, text='Welcome to SweGammon!')
        self.lblGreetings.grid(column=1, row=1, sticky=(W, E))
        widgets.append(self.lblGreetings)
        self.lblError = Label(self, text=alreadyExistMessage)
        if alreadyExistMessage != None:
            self.lblError.grid(column=1, row=2, sticky=(W, E))
        widgets.append(self.lblError)
        self.lblUser = Label(self, text='Username ')
        self.lblUser.grid(column=1, row=3, sticky=(W))
        widgets.append(self.lblUser)
        self.txtUser = Entry(self)
        self.txtUser.grid(column=2, row=3, sticky=(W))
        widgets.append(self.txtUser)
        self.lblIp = Label(self, text='IP Address ')
        self.lblIp.grid(column=1, row=4, sticky=(W))
        widgets.append(self.lblIp)
        self.txtIp = Entry(self)
        self.txtIp.grid(column=2, row=4, sticky=(W))
        self.txtIp.insert(0, str(socket.gethostname()))
        widgets.append(self.txtIp)
        self.btnLogin = Button(self, text='Login', command=sendLogin)
        self.btnLogin.grid(column=2, row=5, sticky=(W, E))
        widgets.append(self.btnLogin)
        threadLock.release

    def showConnectedScreen(self):
        threadLock.acquire
        for widget in widgets:
            widget.grid_forget()
        self.lblLoggedIn = Label(self, text='You are logged in!')
        self.lblLoggedIn.grid(column=1, row=1, sticky=(W, E))
        widgets.append(self.lblLoggedIn)
        self.btnChoosePlay = Button(self, text='I want to play', command=sendChoosePlay)
        self.btnChoosePlay.grid(column=1, row=2, sticky=(W, E))
        widgets.append(self.btnChoosePlay)
        self.btnChooseWatch = Button(self, text='I want to watch', command=sendChooseWatch)
        self.btnChooseWatch.grid(column=1, row=3, sticky=(W, E))
        widgets.append(self.btnChooseWatch)
        threadLock.release

    def setPiecePositions(self, blackPositions, whitePositions):
        for i in range(1, 13):
            lblTopNumbers = Label(self, text=str(25 - i))
            lblTopNumbers.grid(column=2 + i, row=3, sticky=(W, E))
            widgets.append(lblTopNumbers)
            if whitePositions[i] == '0W' and blackPositions[i] == '0B':
                lblPosition = Label(self, text='  |')
                lblPosition.grid(column=2 + i, row=4, sticky=(E))
                widgets.append(lblPosition)
            elif blackPositions[i] == '0B':
                lblPosition = Label(self, text=whitePositions[i] + '|')
                lblPosition.grid(column=2 + i, row=4, sticky=(E))
                widgets.append(lblPosition)
            else:
                lblPosition = Label(self, text=blackPositions[i] + '|')
                lblPosition.grid(column=2 + i, row=4, sticky=(E))
                widgets.append(lblPosition)
        for i in range(13, 25):
            if whitePositions[i] == '0W' and blackPositions[i] == '0B':
                lblPosition = Label(self, text='  |')
                lblPosition.grid(column=27 - i, row=9, sticky=(E))
                widgets.append(lblPosition)
            elif blackPositions[i] == '0B':
                lblPosition = Label(self, text=whitePositions[i] + '|')
                lblPosition.grid(column=27 - i, row=9, sticky=(E))
                widgets.append(lblPosition)
            else:
                lblPosition = Label(self, text=blackPositions[i] + '|')
                lblPosition.grid(column=27 - i, row=9, sticky=(E))
                widgets.append(lblPosition)
            lblBottomNumbers = Label(self, text=str(25 - i))
            lblBottomNumbers.grid(column=27 - i, row=10, sticky=(W, E))
            widgets.append(lblBottomNumbers)
    #
    def showPlayerGameScreen(self):
        threadLock.acquire
        for widget in widgets:
            widget.grid_forget()
        self.lblHeader = Label(self, text='SweGammon Board')
        self.lblHeader.grid(column=1, row=1, sticky=(W, E))
        widgets.append(self.lblHeader)
        whitePositions = []
        whitePositions.append('0')
        blackPositions = []
        blackPositions.append('0')
        if session.color == 'W':
            opponentColor = 'Black'
            youColor = 'White'
            opponentGatheringZone = str(session.gameState.gatheringZone[1]) + 'B'
            opponentBrokenZone = str(session.gameState.brokenZone[1]) + 'B'
            youGatheringZone = str(session.gameState.gatheringZone[0]) + 'W'
            youBrokenZone = str(session.gameState.brokenZone[0]) + 'W'
            for i in range(1, len(session.gameState.positions)):
                whitePositions.append(str(session.gameState.positions[i][0]) + 'W')
                blackPositions.append(str(session.gameState.positions[i][1]) + 'B')
            if session.gameState.buttons[0][0] == 1:
                rollDiceButton = 'normal'
            else:
                rollDiceButton = 'disabled'
            if session.gameState.buttons[0][1] == 1:
                sendMoveButton = 'normal'
            else:
                sendMoveButton = 'disabled'
            if session.gameState.buttons[0][2] == 1:
                wrongMoveButton = 'normal'
            else:
                wrongMoveButton = 'disabled'

            print whitePositions
            print blackPositions
        else:
            opponentColor = 'White'
            youColor = 'Black'
            opponentGatheringZone = str(session.gameState.gatheringZone[0]) + 'W'
            opponentBrokenZone = str(session.gameState.brokenZone[0]) + 'W'
            youGatheringZone = str(session.gameState.gatheringZone[1]) + 'B'
            youBrokenZone = str(session.gameState.brokenZone[1]) + 'B'
            for i in range(1, len(session.gameState.positions)):
                whitePositions.append(str(session.gameState.positions[25 - i][0]) + 'W')
                blackPositions.append(str(session.gameState.positions[25 - i][1]) + 'B')
            if session.gameState.buttons[1][0] == 1:
                rollDiceButton = 'normal'
            else:
                rollDiceButton = 'disabled'
            if session.gameState.buttons[1][1] == 1:
                sendMoveButton = 'normal'
            else:
                sendMoveButton = 'disabled'
            if session.gameState.buttons[1][2] == 1:
                wrongMoveButton = 'normal'
            else:
                wrongMoveButton = 'disabled'
            print whitePositions
            print blackPositions

        self.lblOpponent = Label(self, text='Opponent ' + opponentColor + ': ')
        self.lblOpponent.grid(column=1, row=2, sticky=(W, E))
        widgets.append(self.lblOpponent)
        self.lblOpponentName = Label(self, text=session.opponent)
        self.lblOpponentName.grid(column=2, row=2, sticky=(W, E))
        widgets.append(self.lblOpponentName)
        self.lblOpponentGathering = Label(self, text=opponentColor + ' gathered: ' + opponentGatheringZone + '||')
        self.lblOpponentGathering.grid(column=1, row=5, sticky=(E))
        widgets.append(self.lblOpponentGathering)
        self.lblYouBroken = Label(self, text=youColor + ' broken: ' + youBrokenZone + '||')
        self.lblYouBroken.grid(column=1, row=6, sticky=(E))
        widgets.append(self.lblYouBroken)
        self.lblOpponentBroken = Label(self, text=opponentColor + ' broken: ' + opponentBrokenZone + '||')
        self.lblOpponentBroken.grid(column=1, row=7, sticky=(E))
        widgets.append(self.lblOpponentBroken)
        self.lblYouGathering = Label(self, text=youColor + ' gathered: ' + youGatheringZone + '||')
        self.lblYouGathering.grid(column=1, row=8, sticky=(E))
        widgets.append(self.lblYouGathering)

        self.setPiecePositions(blackPositions, whitePositions)

        self.lblYou = Label(self, text='You ' + youColor + ': ')
        self.lblYou.grid(column=1, row=11, sticky=(W, E))
        widgets.append(self.lblYou)
        self.lblYourName = Label(self, text=session.userName)
        self.lblYourName.grid(column=2, row=11, sticky=(W, E))
        widgets.append(self.lblYourName)
        self.lblDice = Label(self, text='Dice: ' + str(session.gameState.dice[0]) + '-' + str(session.gameState.dice[1]))
        self.lblDice.grid(column=2, row=12, sticky=(E))
        widgets.append(self.lblDice)
        self.btnRollDice = Button(self, text='Roll Dice', command=sendRollDice)
        self.btnRollDice.grid(column=2, row=13, sticky=(E))
        self.btnRollDice.config(state=rollDiceButton)
        widgets.append(self.btnRollDice)
        self.txtMove = Entry(self)
        self.txtMove.grid(column=2, row=14, sticky=(E))
        self.txtMove.insert(0, str(session.gameState.dice[0]) + '-' + str(session.gameState.dice[1]) + ': ')
        widgets.append(self.txtMove)
        self.btnSendMove = Button(self, text='Send Move', command=sendSendMove)
        self.btnSendMove.grid(column=2, row=15, sticky=(E))
        self.btnSendMove.config(state=sendMoveButton)
        widgets.append(self.btnSendMove)
        self.btnWrongMoveAlert = Button(self, text='Wrong Move Alert', command=sendWrongMoveAlert)
        self.btnWrongMoveAlert.grid(column=2, row=16, sticky=(E))
        self.btnWrongMoveAlert.config(state=wrongMoveButton)
        widgets.append(self.btnWrongMoveAlert)
        threadLock.release
    #


    def showWatcherGameScreen(self):
        threadLock.acquire
        for widget in widgets:
            widget.grid_forget()
        self.lblHeader = Label(self, text='SweGammon Board')
        self.lblHeader.grid(column=1, row=1, sticky=(W, E))
        widgets.append(self.lblHeader)
        whitePositions = []
        whitePositions.append('0')
        blackPositions = []
        blackPositions.append('0')

        opponentColor = 'Black'
        youColor = 'White'
        opponentGatheringZone = str(session.gameState.gatheringZone[1]) + 'B'
        opponentBrokenZone = str(session.gameState.brokenZone[1]) + 'B'
        youGatheringZone = str(session.gameState.gatheringZone[0]) + 'W'
        youBrokenZone = str(session.gameState.brokenZone[0]) + 'W'
        for i in range(1, len(session.gameState.positions)):
            whitePositions.append(str(session.gameState.positions[i][0]) + 'W')
            blackPositions.append(str(session.gameState.positions[i][1]) + 'B')
        rollDiceButton = 'disabled'
        sendMoveButton = 'disabled'
        wrongMoveButton = 'disabled'
        print whitePositions
        print blackPositions
        self.lblOpponent = Label(self, text='Player1 ' + opponentColor + ': ')
        self.lblOpponent.grid(column=1, row=2, sticky=(W, E))
        widgets.append(self.lblOpponent)
        self.lblOpponentName = Label(self, text=session.opponent)
        self.lblOpponentName.grid(column=2, row=2, sticky=(W, E))
        widgets.append(self.lblOpponentName)
        self.lblOpponentGathering = Label(self, text=opponentColor + ' gathered: ' + opponentGatheringZone + '||')
        self.lblOpponentGathering.grid(column=1, row=5, sticky=(E))
        widgets.append(self.lblOpponentGathering)
        self.lblYouBroken = Label(self, text=youColor + ' broken: ' + youBrokenZone + '||')
        self.lblYouBroken.grid(column=1, row=6, sticky=(E))
        widgets.append(self.lblYouBroken)
        self.lblOpponentBroken = Label(self, text=opponentColor + ' broken: ' + opponentBrokenZone + '||')
        self.lblOpponentBroken.grid(column=1, row=7, sticky=(E))
        widgets.append(self.lblOpponentBroken)
        self.lblYouGathering = Label(self, text=youColor + ' gathered: ' + youGatheringZone + '||')
        self.lblYouGathering.grid(column=1, row=8, sticky=(E))
        widgets.append(self.lblYouGathering)
        self.setPiecePositions(blackPositions, whitePositions)
        self.lblYou = Label(self, text='Player2 ' + youColor + ': ')
        self.lblYou.grid(column=1, row=11, sticky=(W, E))
        widgets.append(self.lblYou)
        self.lblYourName = Label(self, text=session.userName)
        self.lblYourName.grid(column=2, row=11, sticky=(W, E))
        widgets.append(self.lblYourName)
        self.lblDice = Label(self, text='Dice: ' + str(session.gameState.dice[0]) + '-' + str(session.gameState.dice[1]))
        self.lblDice.grid(column=2, row=12, sticky=(E))
        widgets.append(self.lblDice)
        self.btnRollDice = Button(self, text='Roll Dice', command=sendRollDice)
        self.btnRollDice.grid(column=2, row=13, sticky=(E))
        self.btnRollDice.config(state=rollDiceButton)
        widgets.append(self.btnRollDice)
        self.txtMove = Entry(self)
        self.txtMove.grid(column=2, row=14, sticky=(E))
        widgets.append(self.txtMove)
        self.btnSendMove = Button(self, text='Send Move', command=sendSendMove)
        self.btnSendMove.grid(column=2, row=15, sticky=(E))
        self.btnSendMove.config(state=sendMoveButton)
        widgets.append(self.btnSendMove)
        self.btnWrongMoveAlert = Button(self, text='Wrong Move Alert', command=sendWrongMoveAlert)
        self.btnWrongMoveAlert.grid(column=2, row=16, sticky=(E))
        self.btnWrongMoveAlert.config(state=wrongMoveButton)
        widgets.append(self.btnWrongMoveAlert)
        threadLock.release

#button commands
def sendLogin(*args):
    #host = socket.gethostname() # Get local machine name
    #print str(host)
    host = sweGammonGui.txtIp.get()
    s.connect((host, port))
    time.sleep(2)
    receiveManager.start()
    session.userName = sweGammonGui.txtUser.get()
    CommandHandler.sendLoginCommand()
def sendChoosePlay(*args):
    session.userName = sweGammonGui.txtUser.get()
    CommandHandler.sendChoosePlayCommand()
def sendChooseWatch(*args):
    session.userName = sweGammonGui.txtUser.get()
    CommandHandler.sendChooseWatchCommand()
def sendRollDice(*args):
    CommandHandler.sendRollDiceCommand()
def sendSendMove(*args):
    move = sweGammonGui.txtMove.get()
    CommandHandler.sendSendMoveCommand(move)
def sendWrongMoveAlert(*args):
    CommandHandler.sendWrongMoveAlertCommand()

threads = []
widgets = []

s = socket.socket() # Create a socket object
host = '' # Get local machine name
port = 7500 # Reserve a port for our service.
# s.connect((host, port))

session = Session()

receiveManager = ReceiveManager()
threads.append(receiveManager)
#receiveManager.start()

root = Tk()
root.title("SweGammon")
root.geometry("700x500+300+300")
sweGammonGui = GUIManager(root)
sweGammonGui.initialize()
root.mainloop()


# Wait for all threads to complete
for t in threads:
    t.join()

s.close # Close the socket when done
print "Exiting Main Thread"



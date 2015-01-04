from Tkinter import *
import tkMessageBox
import threading
import socket
import json

threadLock = threading.Lock()

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
            commandHandler = CommandHandler()
            commandHandler.handleCommand(incoming)

class Session(object):
    def __init__(self):
        self.seqid = 0
        self.userName = ''
        self.color = ''
        self.serverIp = ''
        self.serverPort = ''
        self.gameState = GameState()

class JsonDict(dict):
    def __init__(self):
        dict.__init__(self)
        session.seqid += 1
        self["seqid"] = session.seqid

class CommandHandler(object):
    def requestParser(self,message):
        reqList = re.split('  ', message)
        return reqList[0], reqList[1]

    def handleCommand(self, message):
        try:
            command, jsonString = self.requestParser(message)
            # threadLock.acquire
            # print command + ' ' + jsonString
            # threadLock.release
            decoded = json.loads(jsonString)
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

    def sendRollDiceCommand(self):
        dict = JsonDict()
        jsonPart = json.dumps(dict)
        CommandHandler.sendMessage('DROLL', jsonPart)

    def sendSendMoveCommand(self, bgNotationString):
        dict = JsonDict()
        dict["move"] = bgNotationString
        jsonPart = json.dumps(dict)
        CommandHandler.sendMessage('SMOVE', jsonPart)

    def sendWrongMoveAlertCommand(self):
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

    def receiveChoosePlayResponse(self, decoded):
        seqid = decoded['seqid']
        session.color = decoded['color']
        session.opponent = decoded['opponent']
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
        sweGammonGui.showGameScreen()

    # def receiveIWantToWatchResponse(self, decoded):
    #
    # def receiveRollDiceResponse(self, decoded):
    #
    # def receiveSendMoveResponse(self, decoded):
    #
    # def receiveWrongMoveAlertResponse(self, decoded):

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


        # session.gameState = GameState()
        # self.stringToButtons(session.gameState)


    def stringToButtons(self, state):
        for i in range(0, 25):
            for j in range(0, 1):

                self.button = Button()
                self.button.grid()
                self.button.configure(bg = "#000000")
                #self.button.place(x = i * 30, y = (j+1) * 30, width = 30, height = 30)



    def showLoginScreen(self, alreadyExistMessage):
        threadLock.acquire
        self.lblGreetings = Label(self, text='Welcome to SweGammon!')
        self.lblGreetings.grid(column=1, row=1, sticky=(W, E))
        self.lblError = Label(self, text=alreadyExistMessage)
        if alreadyExistMessage != None:
            self.lblError.grid(column=1, row=2, sticky=(W, E))
        self.lblUser = Label(self, text='Username ')
        self.lblUser.grid(column=1, row=3, sticky=(W))
        self.txtUser = Entry(self)
        self.txtUser.grid(column=2, row=3, sticky=(W))
        self.lblIp = Label(self, text='IP Address ')
        self.lblIp.grid(column=1, row=4, sticky=(W))
        self.txtIp = Entry(self)
        self.txtIp.grid(column=2, row=4, sticky=(W))
        self.btnLogin = Button(self, text='Login', command=sendLogin)
        self.btnLogin.grid(column=2, row=5, sticky=(W, E))
        threadLock.release

    def showConnectedScreen(self):
        threadLock.acquire
        self.lblGreetings.grid_forget()
        self.lblError.grid_forget()
        self.lblUser.grid_forget()
        self.txtUser.grid_forget()
        self.lblIp.grid_forget()
        self.txtIp.grid_forget()
        self.btnLogin.grid_forget()
        self.lblLoggedIn = Label(self, text='You are logged in!')
        self.lblLoggedIn.grid(column=1, row=1, sticky=(W, E))
        self.btnChoosePlay = Button(self, text='I want to play', command=sendChoosePlay)
        self.btnChoosePlay.grid(column=1, row=2, sticky=(W, E))
        self.btnChooseWatch = Button(self, text='I want to watch', command=sendChooseWatch)
        self.btnChooseWatch.grid(column=1, row=3, sticky=(W, E))
        threadLock.release

    # def iWantToPlayOrWatch(self, choice):
    #
    # #def showNoActiveUsers(self):
    #
    # #def showNoActiveGames(self):
    #
    def showGameScreen(self):
        threadLock.acquire
        self.lblLoggedIn.grid_forget()
        self.btnChoosePlay.grid_forget()
        self.btnChooseWatch.grid_forget()
        self.lblHeader = Label(self, text='SweGammon')
        self.lblHeader.grid(column=1, row=1, sticky=(W, E))
        if session.color == 'W':
            opponentColor = 'Black'
        else:
            opponentColor = 'White'
        self.lblOpponent = Label(self, text=opponentColor + ' Opponent: ')
        self.lblOpponent.grid(column=1, row=2, sticky=(W, E))
        self.lblOpponentName = Label(self, text=session.opponent)
        self.lblOpponentName.grid(column=2, row=2, sticky=(W, E))
        for i in range(1,14):
            Button(self).pack()
        threadLock.release
    #
    # def throwDice(self):
    #
    # def sendMove(self):
    #
    # def wrongMoveAlert(self):

def sendLogin(*args):
    session.userName = sweGammonGui.txtUser.get()
    CommandHandler.sendLoginCommand()
def sendChoosePlay(*args):
    session.userName = sweGammonGui.txtUser.get()
    CommandHandler.sendChoosePlayCommand()
def sendChooseWatch(*args):
    session.userName = sweGammonGui.txtUser.get()
    CommandHandler.sendChooseWatchCommand()

threads = []

s = socket.socket() # Create a socket object
host = socket.gethostname() # Get local machine name
port = 7500 # Reserve a port for your service.

s.connect((host, port))

session = Session()

receiveManager = ReceiveManager()
threads.append(receiveManager)
receiveManager.start()

root = Tk()
root.title("SweGammon")
root.geometry("500x500+300+300")
sweGammonGui = GUIManager(root)
sweGammonGui.initialize()
root.mainloop()


# Wait for all threads to complete
for t in threads:
    t.join()

s.close # Close the socket when done
print "Exiting Main Thread"



from Tkinter import *
import GameState
import threading


class SendManager(threading.Thread):
    def run(self):


class ReceiveManager(threading.Thread):
    def run(self):


class Session(object):
    def __init__(self, userName, serverIp, serverPort, gameState):
        self.userName = userName
        self.serverIp = serverIp
        self.serverPort = serverPort
        self.gameState = gameState


class CommandHandler(object):
    def __init__(self, session):
        self.session = session

    def sendLoginCommand(self, userName, serverIp, serverPort):

    def sendChoosePlayCommand(self):

    def sendChooseWatchCommand(self):

    def sendRollDiceCommand(self):

    def sendSendMoveCommand(self):

    def sendWrongMoveAlertCommand(self):

    def sendHeartbeatResponseCommand(self):

    def receiveLoginResponse(self, response):

    def receiveIWantToPlayResponse(self, response):

    def receiveIWantToWatchResponse(self, response):

    def receiveRollDiceResponse(self, response):

    def receiveSendMoveResponse(self, response):

    def receiveWrongMoveAlertResponse(self, response):




class GUIManager(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.initialize()

    def initialize(self):
        gameState = GameState.GameState()
        self.stringToButtons(gameState)


    def stringToButtons(self, state):
        for i in range(0, 25):
            for j in range(0, 1):

                self.button = Button()
                self.button.grid()
                self.button.configure(bg = "#000000")
                #self.button.place(x = i * 30, y = (j+1) * 30, width = 30, height = 30)



    def showLoginScreen(self, alreadyExistMessage):


    def login(self, userName, serverIp, serverPort):


    #def showAlreadyExistScreen(self, userName):


    def showConnectedScreen(self, noActiveMessage):
        #uses session

    def iWantToPlayOrWatch(self, choice):

    #def showNoActiveUsers(self):

    #def showNoActiveGames(self):

    def showGameScreen(self):

    def throwDice(self):

    def sendMove(self):

    def wrongMoveAlert(self):







root = Tk()
root.title("SweGammon")
root.geometry("500x500")

sweGammon = SweGammonClient(root)

root.mainloop()

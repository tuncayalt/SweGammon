import threading
import time
import socket
import json
import re

threadLock = threading.Lock()

class Users(object):
    def __init__(self):
        self.users = []
    def userNameExist(self, userName):
        if self.users is None or self.users.count() == 0:
            return False
        for user in self.users:
            if user.userName == userName:
                return True
        return False

    def addUser(self, user):
        self.users += user

class User(object):
    def __init__(self, userName, address):
        self.userType = ''
        self.userName = userName
        self.userIpAddress = address[0]
        self.userPort = address[1]
        self.userHeartbeatFails = 0



class ServerCommandHandler(object):
    def requestParser(self,req):
        reqList = re.split(' ',req)
        threadLock.acquire
        print reqList
        threadLock.release
        return reqList[0], reqList[1]

    def handleCommand(self, req, address):
        command, jsonString = self.requestParser(req)
        try:
            decoded = json.loads(jsonString)
        except (ValueError, KeyError, TypeError):
            threadLock.acquire
            print "JSON format error"
            threadLock.release
        if (command == 'LOGIN'):
            self.receiveLoginCommand(decoded, address)

    def receiveLoginCommand(self, decoded, address):
            seqid = decoded['seqid']
            userName = decoded['username']
            if users.userNameExist(userName):
                self.sendLoginResponse(False, seqid, userName)
            else:
                user = User(userName, address)
                users.addUser(user)
                self.sendLoginResponse(True, seqid, userName)





class ServerReceiveManager(threading.Thread):
    def __init__(self, con, address):
        threading.Thread.__init__(self)
        self.c = con
        self.address = address
    def run(self):
        print "Starting ServerReceiveManager"
        while True:
            req = self.c.recv(1024)
            serverCommandHandler = ServerCommandHandler()
            serverCommandHandler.handleCommand(req, self.address)
        print "Exiting ServerReceiveManager"

class ServerSendManager(threading.Thread):
    def __init__(self, con, address):
        threading.Thread.__init__(self)
        self.c = con
        self.address = address
    def run(self):
        threadLock.acquire
        print "Starting ServerSendManager"
        threadLock.release
        while True:
            time.sleep(10)
            mes = 'time: ' + str(time.time()) + '\n'
            threadLock.acquire()
            print (mes)
            threadLock.release()
            #self.c.sendall(mes)
        threadLock.acquire
        print "Exiting ServerSendManager"
        threadLock.release


threads = []
users = Users()

s = socket.socket()
host = socket.gethostname()
port = 7500
s.bind((host, port))

s.listen(100)

while True:
    c, address = s.accept()
    print ("Got connection from" + str(address))
    receiveManager = ServerReceiveManager(c, address)
    sendManager = ServerSendManager(c, address)
    threads.append(receiveManager)
    threads.append(sendManager)
    receiveManager.start()
    sendManager.start()

# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
s.close()
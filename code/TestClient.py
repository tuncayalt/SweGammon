import socket # Import socket module
import threading

threadLock = threading.Lock()

class ThreadRead(threading.Thread):
    def run(self):
        print "Starting ThreadRead"
        while True:
            threadLock.acquire()
            print s.recv(1024)
            threadLock.release()

        print "Exiting ThreadRead"


class ThreadWrite(threading.Thread):
    def run(self):
        print "Starting ThreadWrite"
        while True:
            s.send(raw_input())


        print "Exiting ThreadWrite"


threads = []

s = socket.socket() # Create a socket object
host = socket.gethostname() # Get local machine name
port = 7500 # Reserve a port for your service.

s.connect((host, port))

threadRead = ThreadRead()
threadWrite = ThreadWrite()
threads.append(threadRead)
threads.append(threadWrite)
threadRead.start()
threadWrite.start()

# Wait for all threads to complete
for t in threads:
    t.join()

s.close # Close the socket when done
print "Exiting Main Thread"

import random
import os
from _thread import *
from threading import Thread
import socket
import time
import queue

class Machine:

    def __init__(self, config):

        config.append(os.getpid()) # get current process id

        self.rate = float(1/random.randInt(1,6))
        self.host = str(config[0])
        self.port = int(config[1])
        self.config = config
        self.clock = 0

        self.queue = queue.SimpleQueue # network queue

        # init listening thread on home port
        init_thread = Thread(target=self.init_machine)
        init_thread.start()

        #add delay to initialize the server-side logic on all processes
        time.sleep(5)

        # producers "receive" messages by connecting sockets to other ports
        self.prod1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.port1 = int(config[2])
        try:
            self.prod1.connect(self.host, self.port1)
            print("Client-side connection success to port val:" + str(self.port1) + "\n")
        except socket.error as e:
            print ("Error connecting producer: %s" % e)

        self.prod2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.port2 = int(config[3])
        try:
            self.prod2.connect(self.host, self.port2)
            print("Client-side connection success to port val:" + str(self.port2) + "\n")
        except socket.error as e:
            print ("Error connecting producer: %s" % e)



    def init_machine(self): # receive function, essentially
        HOST = self.host
        PORT = self.port
        print("starting server| port val:", PORT)

        # create socket, bind to host and port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, _ = s.accept() # all must connect first, then start receiving
            start_new_thread(self.consumer, (conn,)) # consumer reads, decodes msgs and add to queue
    
    def consumer(self, conn): # called when starting new thread
        # conn is client connection received after s.accept(); can use conn.send()
        print("consumer accepted connection" + str(conn)+"\n")

        while True: # receiving messages to queue NOT constrained to rate

            data = conn.recv(1024) # blocks until connection from client
            print("msg received\n")

            # decode 
            dataVal = data.decode('ascii')
            print("msg received:", dataVal)

            # network queue
            self.queue.append(dataVal)


    def start(self):
        
        if self.queue.empty():
            rng = random.randInt(1,10)
            time.sleep(self.rate)
            if rng == 1: 
                # send to one of other machines
                msg = str(self.clock)
                s.send(msg.encode('ascii'))
                print("msg sent", msg)

                # update own logical clock
                self.clock += 1

                # update log with send, system time, logical clock time
                # TODO 
            elif rng == 2:

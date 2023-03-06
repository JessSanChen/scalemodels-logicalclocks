
import random
import os
from _thread import *
from threading import Thread
import socket
import time
import queue
from multiprocessing import Process

class Machine:

    def __init__(self, config):

        config.append(os.getpid()) # get current process id

        self.rate = float(1/random.randint(1,6))
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
            self.queue.put(dataVal)


    def start(self):
        while True:
            time.sleep(self.rate)
            if not self.queue.empty():
                msg = self.queue.get()
                self.clock += 1
                # write to log: received, global time, length of queue, logical clock time
            else:
                rng = random.randint(1,10)
                time.sleep(self.rate)
                if rng == 1: # send to one of other machines
                    msg = str(self.clock)
                    self.prod1.send(msg.encode('ascii'))
                    print("msg sent", msg)
                    self.clock += 1

                    # write log with send, system time, logical clock time
                elif rng == 2: # send to other machine
                    # send to one of other machines
                    msg = str(self.clock)
                    self.prod2.send(msg.encode('ascii'))
                    print("msg sent", msg)
                    self.clock += 1

                    # write log with send, system time, logical clock time
                elif rng == 3: # send to both other machines
                    # send to one of other machines
                    msg = str(self.clock)
                    self.prod1.send(msg.encode('ascii'))
                    self.prod2.send(msg.encode('ascii'))
                    print("msg sent", msg)
                    self.clock += 1

                    # write log with send, system time, logical clock time
                else: # internal event
                    self.clock += 1
                    # log internal event, system time, logical clock value
                


if __name__ == '__main__':
    localHost= "127.0.0.1"

    port1 = 2056
    port2 = 3056
    port3 = 4056

    config1=[localHost, port1, port2, port3]
    m1 = Machine(config1)
    config2=[localHost, port2, port1, port3]
    m2 = Machine(config2)
    config3=[localHost, port3, port1, port2]
    m3 = Machine(config3)    
    
    p1 = Process(target=m1.start)
    p2 = Process(target=m2.start)
    p3 = Process(target=m3.start)

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
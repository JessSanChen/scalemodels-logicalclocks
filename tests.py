import random
import os
from _thread import *
from threading import Thread
import socket
import time
import queue
from multiprocessing import Process
import matplotlib.pyplot as plt
import multiprocessing

global machines
machines = [[[],[],[],[]],[[],[],[],[]],[[],[],[],[]]]

class Machine:

    def __init__(self, config, number, rate, roll,filename):

        config.append(os.getpid()) # get current process id

        self.roll = roll
        self.rate = float(1/rate)

        self.host = str(config[0])
        self.port = int(config[1])
        self.config = config
        self.clock = [0,0,0]
        self.number = number # id for the machine
        self.queue = [] # network queue
        self.file = filename+"m"+str(self.number)+".txt"
        self.lock = multiprocessing.Lock()


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
            start_new_thread(self.consumer, (conn,))
    
    def consumer(self, conn): # called when starting new thread
        # conn is client connection received after s.accept(); can use conn.send()
        print("consumer accepted connection" + str(conn)+"\n")

        while True: # receiving messages to queue NOT constrained to rate
            data = conn.recv(1024).decode('ascii')
            print(self.number, " queue appended with: ", data)
            self.queue.append(data) # network queue

    def producer(self):
        # producers "receive" messages by connecting sockets to other ports
        self.prod1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.port1 = int(self.config[2])

        try:
            self.prod1.connect((self.host, self.port1))
            print("Client-side connection success to port val:" + str(self.port1) + "\n")
        except socket.error as e:
            print ("Error connecting producer: %s" % e)

        self.prod2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.port2 = int(self.config[3])

        try:
            self.prod2.connect((self.host, self.port2))
            print("Client-side connection success to port val:" + str(self.port2) + "\n")
        except socket.error as e:
            print ("Error connecting producer: %s" % e)

        with open(self.file, "w") as f:
            self.opened_file = f
            start = time.time()
            while time.time() - start < 5:
                time.sleep(self.rate)
                timestr = str(round(time.time()-start,3))
                if len(self.queue) > 0:
                    msg = self.queue.pop()
                    data_list = msg.split("|")
                    for i in range(0,3):
                        self.clock[i] = max(int(data_list[i]), self.clock[i]) + 1
                    print(self.number, " received: ", self.clock)

                    clockstr = ''.join(str(n)+"|" for n in self.clock)
                    f.write("Received "+ msg+ ","+timestr+","+str(len(self.queue))+","+clockstr+"\n")
                else:
                    status = ''.join(str(n)+"|" for n in self.clock)
                    # rng = random.randint(1,10)
                    rng = self.roll
                    self.clock[self.number] += 1
                    if rng == 1: # send to one of other machines
                        self.prod1.send(status.encode('ascii'))
                        print("status sent", status)
                        action = "Sent"
                    elif rng == 2: # send to other machine
                        # send to one of other machines
                        self.prod2.send(status.encode('ascii'))
                        print("status sent", status)
                        action = "Sent"
                        # write log with send, system time, logical clock time
                    elif rng == 3: # send to both other machines
                        self.prod1.send(status.encode('ascii'))
                        self.prod2.send(status.encode('ascii'))
                        print("status sent", status)
                        action = "Sent"
                    else:
                        print(str(self.number) + " resting")
                        action = "Internal"
                    clockstr = ''.join(str(n)+"|" for n in self.clock)
                    f.write(action+","+timestr+","+"0,"+clockstr+"\n")
                machines[self.number][3].append(float(timestr))
                machines[self.number][0].append(self.clock[0])
                machines[self.number][1].append(self.clock[1])
                machines[self.number][2].append(self.clock[2])
            f.close()
        return

            
    def start(self):
        # init listening thread on home port
        init_thread = Thread(target=self.init_machine)
        init_thread.start()

        #add delay to initialize the server-side logic on all processes
        time.sleep(5)

        prod_thread = Thread(target=self.producer)
        prod_thread.start()

        # time.sleep(70)
        # self.plot()

    def plot(self):
        plt.plot(machines[self.number][3], machines[self.number][0], label="Machine 0")
        plt.plot(machines[self.number][3], machines[self.number][1], label="Machine 1")
        plt.plot(machines[self.number][3], machines[self.number][2], label="Machine 2")
        plt.title("Machine " + str(self.number) + f" POV at {round(1/self.rate,3)} ops/sec")
        plt.xlabel("Time")
        plt.ylabel("Logical Clock Values") 
        plt.legend()
        plt.show()
        time.sleep(20)

    def close_file(self):
        self.opened_file.close()


class Test:

    def __init__(self, config1,config2,config3):
        self.config1 = config1
        self.config2 = config2
        self.config3 = config3


    def test_synch_rate(self):
        # all machines synchronized at 1 op/sec
        # m0 sends to m1, m1 sends to both m0 and m2, m2 internal only
        # m0 starts first

        m0 = Machine(config1, 0,1,1,"sync0first")
        m1 = Machine(config2, 1,1,3,"sync0first")
        m2 = Machine(config3, 2,1,5,"sync0first") 
        
        try:
            p1 = Process(target=m0.start)
            p2 = Process(target=m1.start)
            p3 = Process(target=m2.start)

            p1.start()
            time.sleep(0.2)
            p2.start()
            time.sleep(0.2)
            p3.start()

            p1.join(timeout=duration)
            p2.join(timeout=duration)
            p3.join(timeout=duration)

            p1.terminate()
            p2.terminate()
            p3.terminate()


        except KeyboardInterrupt:
            p1.terminate()
            p2.terminate()
            p3.terminate()

        success = True
        m0expected = [[1, 0, 0],[2, 0, 0],[3, 0, 0],[4, 0, 0],[5, 0, 0]]
        m1expected = [[1, 1, 1],[2, 2, 2],[3, 3, 3],[4, 4, 4],[5, 5, 5]]
        m2expected = [[0, 0, 1],[0, 0, 2],[0, 0, 3],[0, 0, 4],[0, 0, 5]]

        with open("syncm0.txt","r") as f0:
            clock = []
            for line in f0:
                linelist = line.split(",")
                lineclock = list(map(int,linelist[3].split("|")[:3]))
                clock.append(lineclock)
            print(clock)
            if clock != m0expected:
                success = False
                self.test_synch_rate_error = "m0 does not match expected"
        with open("syncm1.txt","r") as f1:
            clock = []
            for line in f1:
                linelist = line.split(",")
                lineclock = list(map(int,linelist[3].split("|")[:3]))
                clock.append(lineclock)
            print(clock)
            if clock != m1expected:
                success = False
                self.test_synch_rate_error = "m1 does not match expected"
        with open("syncm2.txt","r") as f2:
            clock = []
            for line in f2:
                linelist = line.split(",")
                lineclock = list(map(int,linelist[3].split("|")[:3]))
                clock.append(lineclock)
            print(clock)
            if clock != m2expected:
                success = False
                self.test_synch_rate_error = "m2 does not match expected"

        return success
    

if __name__ == '__main__':

    duration = 6
    
    localHost= "127.0.0.1"

    port1 = 2056
    port2 = 3056
    port3 = 4056

    config1=[localHost, port1, port2, port3]
    config2=[localHost, port2, port1, port3]
    config3=[localHost, port3, port2, port1]

    tester = Test(config1,config2,config3)

    if tester.test_synch_rate():
        print("synchronized machines with rolls 1, 3, 5 PASS")
    else: 
        print("synchronized machines with rolls 1, 3, 5 FAIL")
        print(tester.test_synch_rate_error)

    

    # m0 = Machine(config1, 0,1,1)
    # m1 = Machine(config2, 1,1,3)
    # m2 = Machine(config3, 2,1,5)    
    
    # try:
    #     p1 = Process(target=m0.start)
    #     p2 = Process(target=m1.start)
    #     p3 = Process(target=m2.start)

    #     p1.start()
    #     p2.start()
    #     p3.start()

    #     p1.join(timeout=duration)
    #     p2.join(timeout=duration)
    #     p3.join(timeout=duration)

    #     p1.terminate()
    #     p2.terminate()
    #     p3.terminate()


    # except KeyboardInterrupt:
    #     p1.terminate()
    #     p2.terminate()
    #     p3.terminate()
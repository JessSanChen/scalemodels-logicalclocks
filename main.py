from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import time
from threading import Thread
import random
 

def consumer(conn, rate): # called when starting new thread
    # conn is client connection received after s.accept(); can use conn.send()
    print("consumer accepted connection" + str(conn)+"\n")

    # network queue
    msg_queue=[]

    # sleep val; to be randomized?
    sleepVal = rate

    while True:
        time.sleep(sleepVal)

        # read at most 1024 bytes, blocking if no data is waiting to be read
        data = conn.recv(1024) 
        print("msg received\n")

        # decode 
        dataVal = data.decode('ascii')
        print("msg received:", dataVal)

        # network queue
        msg_queue.append(dataVal)
 

def producer(portVal):
    host= "127.0.0.1" # still just localhost
    port = int(portVal) # last arg in configs
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sleepVal = 0.500
    #sema acquire
    try:
        s.connect((host,port))
        print("Client-side connection success to port val:" + str(portVal) + "\n")

        # send message
        while True:
            codeVal = str(code) # global code variable, randInt(1,3) in machine
            time.sleep(sleepVal)
            s.send(codeVal.encode('ascii'))
            print("msg sent", codeVal)
    
    except socket.error as e:
        print ("Error connecting producer: %s" % e)
 

def init_machine(config): # receive function, essentially
    HOST = str(config[0])
    PORT = int(config[1])
    print("starting server| port val:", PORT)

    rate = random.randint(1,6)

    # create socket, bind to host and port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        # (clientConnection, clientAddress) = serverSocket.accept();
        conn, _ = s.accept()
        start_new_thread(consumer, (conn,rate)) # consumer reads, decodes msgs and add to queue
        

def machine(config):
    config.append(os.getpid()) # get current process id
    global code
    #print(config)

    # threads, init_machine just does basic socket binding/listening
    init_thread = Thread(target=init_machine, args=(config,))
    init_thread.start()

    #add delay to initialize the server-side logic on all processes
    time.sleep(5)

    # extensible to multiple producers
    prod_thread = Thread(target=producer, args=(config[2],)) #why only 1 other producer?
    prod_thread.start()
 

    while True:
        code = random.randint(1,3)

localHost= "127.0.0.1"
    

if __name__ == '__main__':
    port1 = 2056
    port2 = 3056
    port3 = 4056
    

    config1=[localHost, port1, port2, port3]
    p1 = Process(target=machine, args=(config1,))
    config2=[localHost, port2, port1, port3]
    p2 = Process(target=machine, args=(config2,))
    config3=[localHost, port3, port1, port2]
    p3 = Process(target=machine, args=(config3,))
    

    p1.start()
    p2.start()
    p3.start()
    

    p1.join()
    p2.join()
    p3.join()
import threading
from multiprocessing import Process, Queue
import multiprocessing

# from here each process will random number generate and send a message

class Client:
    # initialization
    def __init__(self, name):
        self.name = name
        self.messages = []

    # Receiving messages from server

    def receive(self, queue, lock):
        while len(queue) > 0:
            with lock:
                try:
                    for msg in queue:
                        message_data = msg.split('|'); recipient = message_data[0]
                        if self.name == recipient:
                            print(message_data[1])
                            msg.get()
                            return(message_data[1])
                except:
                    break
                    
    def start(self):
        self.receive()




c1 = Client("c1"); c2 = Client("c2"); c3 = Client("c3")

if __name__ == "__main__":
    lock = multiprocessing.Lock(); q = Queue()
    p1 = Process(target=c1.receive, args=(q,lock))
    p2 = Process(target=c2.start())
    p3 = Process(target=c3.start())

    p1.start()
    p2.start()
    p3.start()

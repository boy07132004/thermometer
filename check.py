import csv
import time
import numpy as np
import tkinter as tk
from PIL import Image,ImageTk
from opcua import ua,Client
state = 'Running'

class App:      
    def detect(self):
        try:
            self.ary = np.array(temp.get_value(),dtype=np.uint8)
            self.img = ImageTk.PhotoImage(Image.fromarray(self.ary))
            self.lb.image = self.img
            self.lb.configure(image=self.img)
        except Exception as e:
            print(e)
        self.master.after(100,self.detect)
        

    def __init__(self,master):
        self.master = master
        self.img = ImageTk.PhotoImage(Image.fromarray(np.ones((200,200))*150))
        self.lb = tk.Label(image=self.img)
        self.lb.pack()
        #print(self.img)
        self.master.after(100,self.detect)


# Separate images when data change
class SubHandler(object):
    def datachange_notification(self, node, val, data):
        try:
            if val == -1:
                state = "Done"
        except Exception as e:
            print(e)

def main():
    root = tk.Tk()
    app  = App(root)
    while True:
        if count.get_value() == -99:
            print('Waiting...')
            time.sleep(1)
        else:
            break
    count.set_value(-66)
    root.mainloop()
    print('end')

        

if __name__ == "__main__":
    print('='*18)
    print('Made in AUO_ML6A01')
    print('='*18)
    client = Client("opc.tcp://192.168.0.101:4840/")
    #client = Client("opc.tcp://172.20.10.7:4840/")
    client.connect()
    print('Connected')
    temp = client.get_node("ns=2;i=2")
    count = client.get_node("ns=2;i=3")
    handler = SubHandler()
    sub = client.create_subscription(500, handler)
    handle = sub.subscribe_data_change(count)
    main()
    client.disconnect()
    print('End')
    
    
    
            

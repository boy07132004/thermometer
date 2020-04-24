import cv2
import csv
import time
import tkinter as tk
from opcua import ua,Client


class App:
    def show_id_temper(self):
        while True:
            if state == 'Running':
                time.sleep(0.2)
            elif state == 'Done' :
                if len(temp_list)>1:
                    for i in range(len(temp_list)):
                        self.value = temp_list[(-1)*(i+1)]
                        if (self.value>31) and (self.value<37.3) :
                            self.Status['text'] = f'Welcome!!\n{self.ID_now} -- {self.value}℃\n下一位請刷卡'
                            with open('output.csv','a',newline='\n') as csv_file:
                                csv.writer(csv_file).writerow([self.ID_now,self.value])
                            break
                        elif (self.value>37.4) and (self.value<43):
                            self.Status['text'] = '體溫過高'
                            break
                        else:
                            pass
                else:
                    self.Status['text'] = '請重新刷卡量測'   
                break
        self.ID['state']='normal'
        self.ID.delete(0,'end')
                

    def detect(self,event=None):
        temp_list = []
        state = "Running"
        count.set_value(11)
        self.ID_now = self.ID.get()
        self.master.after(1300,self.show_id_temper)
        self.Status['text'] = '量測中請稍後'
        self.ID['state'] = 'disabled'
        

    def __init__(self,master):
        global count
        global state
        global temp_list
        self.value = 0
        self.master = master
        self.master.geometry("500x500")
        self.Frame = tk.Frame(self.master)
        self.Label = tk.Label(self.Frame,text='Made in ML6A01',font = ("Verdana",15))
        self.Label.pack()
        self.ID = tk.Entry(self.Frame)
        self.ID.bind('<Return>',self.detect)
        self.ID.pack()
        self.Status = tk.Label(
            self.Frame,
            text = '',
            font = ("Verdana",40))
        self.Status.pack()
        self.Frame.pack()

# Separate images when data change
class SubHandler(object):
    def datachange_notification(self, node, val, data):
        try:
            global temp_list
            temp_list = val
            global state
            state = "Done"
        except Exception as e:
            print(e)


def announcement(word):
    print('='*10,time.ctime(),'='*10)
    print(word)
    print('-'*10)



def main():
    root = tk.Tk()
    app  = App(root)
    root.mainloop()
    print('end')

        

if __name__ == "__main__":
    print('='*18)
    print('Made in AUO_ML6A01')
    print('='*18)
    client = Client("opc.tcp://192.168.0.101:4840/")
    client.connect()
    announcement('Connected')
    temp = client.get_node("ns=2;i=2")
    count = client.get_node("ns=2;i=3")
    handler = SubHandler()
    sub = client.create_subscription(500, handler)
    handle = sub.subscribe_data_change(temp)
    main()
    client.disconnect()
    announcement('End')
    
    
    
            

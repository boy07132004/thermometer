import cv2
import csv
import time
import tkinter as tk
from opcua import ua,Client
state = 'Running'

class App:
    def show_id_temper(self):
        if self.times >0 and state == 'Done':
            temp_list = temp.get_value()

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
                    elif i==(len(temp_list)-1):
                        self.Status['text'] = '請重新刷卡量測'
            else:
                self.master.after(100,self.show_id_temper)
                self.times-=1
                return
            self.ID['state']='normal'
            self.ID.delete(0,'end')
        elif self.times>0 and state == 'Running':
            self.times-=1
            self.master.after(100,self.show_id_temper)
            self.Status['text'] = '2'
        else:
            self.Status['text'] = '請重新刷卡量測'
            self.ID['state']='normal'
            self.ID.delete(0,'end')
                

    def detect(self,event=None):
        self.times = 100
        state = "Running"
        count.set_value(11)
        temp.set_value([0])
        self.ID_now = self.ID.get()
        self.master.after(1000,self.show_id_temper)
        self.Status['text'] = '量測中請稍候'
        self.ID['state'] = 'disabled'
        

    def __init__(self,master):
        global count
        global state
        global temp
        self.value = 0
        self.master = master
        self.master.geometry("1800x900")
        self.Frame = tk.Frame(self.master)
        self.Label = tk.Label(self.Frame,text='Made in ML6A01',font = ("Calibri",12))
        #self.Label.pack()
        self.ID = tk.Entry(self.Frame,font="Calibri 60",justify="center")
        self.ID.bind('<Return>',self.detect)
        self.ID.pack()
        self.Status = tk.Label(
            self.Frame,
            text = 'Welcome!!\n請刷卡',
            font = ("Calibri",100))
        self.Status.pack()
        self.Frame.pack()

# Separate images when data change
class SubHandler(object):
    def datachange_notification(self, node, val, data):
        global state
        global temp
        try:
            if val == -1:
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
    #client = Client("opc.tcp://192.168.0.101:4840/")
    client = Client("opc.tcp://172.20.10.7:4840/")
    client.connect()
    announcement('Connected')
    temp = client.get_node("ns=2;i=2")
    count = client.get_node("ns=2;i=3")
    handler = SubHandler()
    sub = client.create_subscription(500, handler)
    handle = sub.subscribe_data_change(count)
    main()
    client.disconnect()
    announcement('End')
    
    
    
            

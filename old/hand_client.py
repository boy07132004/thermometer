import cv2
import time
import numpy as np
import tkinter as tk
from opcua import ua,Client
from argparse import ArgumentParser
from keras.models import load_model
my_model = load_model(r'model_CNN_32x32.h5')

parser = ArgumentParser()
parser.add_argument("-g","--gpu",type=bool,nargs='?',const=True,default=False,dest='gpu')
args = parser.parse_args()
value = 0

class App:
    def show_id_temper(self,event = None):
        self.start = time.time()
        self.imgs = Separate(img)
        self.predict_list = my_model.predict(self.imgs)
        self.predict_ans = self.predict_list.argmax(axis=1)
        self.value = int("".join(str(x) for x in self.predict_ans))/10
        print(f'ans ------- {self.predict_ans}')
        print(f'value ------- {self.value}')
        if (self.value>31) and (self.value<37.3):
            self.Status['text'] = f'Welcome!!\n{self.ID.get()} -- {self.predict_ans}℃\n下一位請刷卡'
        else:
            self.Status['text'] = f'Wait!!\nTemperature -- {self.value}℃'
        print(f'cost time {time.time()-self.start}s')
        self.ID.delete(0,'end')
    
    def save_img(self):
        cv2.imwrite(f"{time.time()//100000}.png",img)
    
    def __init__(self,master):
        global img
        self.value = 0
        master.geometry("500x500")
        self.Frame = tk.Frame(master)
        self.ID = tk.Entry(self.Frame)
        self.ID.bind('<Return>',self.show_id_temper)
        self.ID.pack()
        self.Status = tk.Label(
            self.Frame,
            text = '',
            font = ("Verdana",30))
        self.Status.pack()
        self.Saveimg = tk.Button(self.Frame,text='Save this img',command=self.save_img)
        self.Saveimg.pack()
        self.Frame.pack()

# Separate images when data change
class SubHandler(object):
    def datachange_notification(self, node, val, data):
        try:
            global img
            #announcement("New data change")
            img = np.array(val,dtype='uint8')             
        except Exception as e:
            print(e)


def announcement(word):
    print('='*10,time.ctime(),'='*10)
    print(word)
    print('-'*10)

def Separate(img_g):
    img_list = []
    try:
        #img_g[img_g[:,:] < 230] = 0 
        #_, binary = cv2.threshold(img_g, 110, 255, cv2.THRESH_BINARY)
        binary = img_g
        rawimg = binary - binary[0,1]
        row_nz = []
        for row in rawimg.tolist():
            row_nz.append(len(row) - row.count(0))
        idx=np.array(row_nz)>(max(row_nz)/4) 
        np.where(idx==1)[0][0],np.where(idx==1)[0][-1]
        up_y=np.where(idx==1)[0][-1] 
        down_y=np.where(idx==1)[0][0] 
        rawimg1=rawimg[down_y:up_y,]
        col_nz = []
        for col in rawimg1.T.tolist():
            col_nz.append(len(col) - col.count(0))

        idy=np.not_equal(col_nz,0)
        record_y=[]
        for i in range(0,(len(np.where(idy==1)[0])-1)):
            if(np.where(idy==1)[0][i+1]-np.where(idy==1)[0][i]==1):
                pass
            else:
                record_y.append(np.where(idy==1)[0][i])

        record_y.insert(0,np.where(idy==1)[0][0])
        record_y.append(np.where(idy==1)[0][-1])

        rm_id=[]
        if len(record_y)>9:
            for j in range(0,len(record_y)-1):
                temp=np.array(col_nz[record_y[j]:record_y[j+1]])
                if sum(temp>(max(col_nz)/4))==0:
                    rm_id.append(record_y[j+1])
		
        for x in rm_id:
            record_y.remove(x)
		
        for i in range(0,len(record_y)-1):
            a = binary[down_y:up_y,record_y[i]:record_y[i+1]]
            if min(a.shape)<10:continue
            a = cv2.resize(a, (32,32), interpolation=cv2.INTER_CUBIC)
            a = np.reshape(a,(32,32,1))
			#a = cv2.cvtColor(a,cv2.COLOR_GRAY2BGR) 
            img_list.append(a)
    except Exception as e:
        print(e)
    return np.array(img_list).astype('float32')/255.


def main():
    root = tk.Tk()
    app  = App(root)
    root.mainloop()
    print('end')

        

if __name__ == "__main__":
    if args.gpu:
        import os
        os.environ["CUDA_VISIBLE_DEVICES"]="0"
        from tensorflow import Session
        from tensorflow import ConfigProto
        import keras.backend.tensorflow_backend as KTF
        cfg = ConfigProto()
        cfg.gpu_options.allow_growth = True
        sess = Session(config=cfg)
        KTF.set_session(sess)
    print('='*18)
    print('Made in AUO_ML6A01')
    print('='*18)
    client = Client("opc.tcp://192.168.0.101:4840/")
    client.connect()
    announcement('Connected')
    temp = client.get_node("ns=2;i=2")
    handler = SubHandler()
    sub = client.create_subscription(500, handler)
    handle = sub.subscribe_data_change(temp)
    main()
    client.disconnect()
    announcement('End')
    
    
    
            

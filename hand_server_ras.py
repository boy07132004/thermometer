import cv2
cap = cv2.VideoCapture(0)

import time
import numpy as np
from os import environ
from opcua import ua,Server
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-s","--show",type=bool,nargs='?',const="True",dest="show_mode",default=False)
args = parser.parse_args()
count = 2
if args.show_mode==False:
    from keras.models import load_model
    my_model = load_model(r'/home/pi/Desktop/thermometer/model_CNN_32x32.h5')

def Separate(img_g):
    img_list = []
    try:        
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
            img_list.append(a)
    except Exception as e:
        print(e)
    return np.array(img_list).astype('float32')/255.

def Get_Frame(cap):
    frame = cap.read()[1]
    frame = frame[:,190:450]
    frame = cv2.resize(frame,(33*2,43*2))
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    #gray = cv2.GaussianBlur(gray,(5,5),0)
    thresh = cv2.threshold(gray,35,255,cv2.THRESH_BINARY_INV)[1]
    thresh = np.rot90(thresh,3)
    #thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU )[1]
    return (frame,thresh)
    
    

def main():
    global count
    value_list = [0]
    if args.show_mode:
        while 1:
            frame,thresh = Get_Frame(cap)
            cv2.imshow('frame',frame)
            cv2.imshow('thr',thresh)
            if cv2.waitKey(1) and 0xFF == ord('q'):
                break
    else:
        while 1:
            # When client send (count = 11)
            # 1.Sleep 1.2 sec and initiate value_list
            # 2.Recognize frame 10 times by CNN
            frame,thresh = Get_Frame(cap)
            if count >= 0:
                if count > 10:
                    value_list = [0]
                    time.sleep(1.2)
                elif count>0:
                    if np.mean(thresh)<=30:
                        time.sleep(0.35)
                        value_list.append(0)
                    else:
                        #start = time.time()
                        imgs = Separate(thresh)
                        predict_list = my_model.predict(imgs)
                        predict_ans = predict_list.argmax(axis=1)
                        value = int("".join(str(x) for x in predict_ans))/10
                        value_list.append(value)
                        #print(f'cost time {time.time()-start}s')
                elif count == 0:
                    print('set',value_list)
                    Temp.set_value(value_list)
                print(f'{count}')
                count-=1
                Count.set_value(count)
            else:
                time.sleep(0.5)
            count = Count.get_value()

if __name__ == '__main__':
    if args.show_mode == False:
        server = Server()
        #server.set_endpoint("opc.tcp://192.168.0.101:4840")
        server.set_endpoint("opc.tcp://172.20.10.7:4840")
        obj    = server.get_objects_node()
        uri    = server.register_namespace("ML6A01")
        Thermo = obj.add_object(uri,"Thermometer")
        Temp   = Thermo.add_variable(uri,"Temperature",[''])
        Count  = Thermo.add_variable(uri,"Count",count)
        Count.set_writable()
        Temp.set_writable()
        server.start()
    
    main()
    if args.show_mode == False:
        server.stop()
    cap.release()
    cv2.destroyAllWindows()

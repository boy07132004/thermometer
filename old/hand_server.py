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

def main():
    global count
    while 1:
        if count>=0:
            frame = cap.read()[1]
            frame = frame[:,120:450]
            frame = cv2.resize(frame,(33*2,43*2))#,interpolation=cv2.INTER_NEAREST)
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            #gray = cv2.GaussianBlur(gray,(5,5),0)
            thresh = cv2.threshold(gray,35,255,cv2.THRESH_BINARY_INV)[1]
            thresh = np.rot90(thresh,3)
            #thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU )[1]

            if args.show_mode:
                cv2.imshow('gray',gray)
                cv2.imshow('thr',thresh)
                if cv2.waitKey(1) and 0xFF == ord('q'):break
                continue
            else:
                if np.mean(thresh)<=30:
                    time.sleep(0.2)
                else:
                    Temp.set_value(thresh.tolist())
                    count-=1
                    Count.set_value(count)
                    time.sleep(0.1)
                    print('set',count)
        else:
            time.sleep(0.05)
        count = Count.get_value()

if __name__ == '__main__':
    if args.show_mode == False:
        server = Server()
        server.set_endpoint("opc.tcp://192.168.0.101:4840")
        #server.set_endpoint("opc.tcp://172.20.10.7:4840")
        obj    = server.get_objects_node()
        uri    = server.register_namespace("ML6A01")
        Thermo = obj.add_object(uri,"Thermometer")
        Temp   = Thermo.add_variable(uri,"Temperature",[''])
        Count  = Thermo.add_variable(uri,"Count",count)
        Count.set_writable()
        server.start()
    
    main()
    if args.show_mode == False:
        server.stop()
    cap.release()
    cv2.destroyAllWindows()

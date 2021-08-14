
#-----------------------------CREATED BY GROUP NO – 79 (CSE-CORE , Batch:- 2019-23)--------------------------------------------------------


import os
import csv
import cv2
import numpy as np
import face_recognition
import os
from datetime import  datetime #library for time and date
import time
import pyttsx3
import pandas as pd

import pyrebase
from firebase import firebase
from google.cloud import storage
from google.cloud.storage.blob import Blob
#-----------------------for voice----------------------------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)
#---------------------for voice-------------------------------------

#-------------------------------------fore firebase configeration-------------------------------------------------------
config = {
    "apiKey": "",       #--> Enter Api key
    "authDomain": "",       #--> Enter authDomain
    "databaseURL": "",          #--> Enter databaseURL
    "projectId": "",            #--> Enter projectId
    "storageBucket": "",           #--> Enter storageBucket        
    "messagingSenderId": "",                               #--> Enter messagingSenderId
    "appId": ""               #--> Enter appId
}
firebase = firebase.FirebaseApplication("firebase url of ur project", None)
blob = Blob.from_string("firestore url")
#-----------------------------------------for firebase configeration-------------------------------------------------


path = 'ImagesAttendance'
images = []
classNames = []
mylist = os.listdir(path)
print(mylist)

for cls in mylist:
    cuImg = cv2.imread(f'{path}/{cls}')
    images.append(cuImg)
    classNames.append(os.path.splitext(cls)[0])

print(classNames) #it will print the file names with out the extensions like "jpg"
print(images)

classFile = 'coco.names'
with open(classFile,'rt') as f:
    classNames2 = f.read().rstrip('\n').split('\n')

#print(classNames)

#next we are going to start with encoding process

'''
we know that once we import the images then we need to find the encodings of each 
image
So , to we will create a simple function that will do this job for us
let's name as findEncodings() and it's parameter will be list of  images
then inside the function we will have the empty list that will have all the encodings
'''

#----------------------function to find the known face encodings----------------------------------------------------------------

def findEncodings(images):
    encodeList = []
    #now we will iterate over the list
    for img in images:
        #so first we find to convet image to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #now we will find the encodings
        encode = face_recognition.face_encodings(img)[0]
        print(encode)
        encodeList.append(encode)

    return encodeList
#----------------------function to find the known face encodings------------------------------------------------------------------


#--------------------defining the classs class path and initializing the model for object dection-----------------------------------------------------
configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

net = cv2.dnn_DetectionModel(weightsPath,configPath)

net.setInputSize(320,320) #height and width
net.setInputScale(1.0/127.5) #sacling the image of different size
net.setInputMean((127.5,127.5,127.5))
net.setInputSwapRB(True)  #by default opencv consider BGR so we need to convert it to rbg by swapping the position of r and g

#---------------------defining the classs class path and initializing the model for object dection------------------------------------------------------



#here we will write a function to mark the attendance
def markAttendance(name1,date1):  # so we need to call this function whenever we find the name and then we need to pass the name as the function parameter
    #here we will open Attendance.csv file and now we will proform both do read and write operation over this file

    with open('Attendance.csv','r+')as f:
        myDataList = f.readlines()
        print(myDataList)
        namelist = []
        datelist = []
        for line in myDataList:
            #conn = pymysql.connect(host="localhost", user="root", password="", db="facedetect")
            #mycursor = conn.cursor()

            entry = line.split(',')
            namelist.append(entry[0]) #so only all the names will get appended to the list which named as "namelist"
            datelist.append(entry[2])
        if name1 not in namelist or date1 not in datelist: #now we are gpoing to check wheater the current name is present in the list or not
            na_me = name1
            present = "present"
            #mycursor.execute("INSERT INTO USERS(regno , status) VALUES (%s,%s)", (na_me, present))
            #conn.commit()

            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')

            #ddString = now.strftime('%b/%d/%Y')

            f.writelines(f'\n{name1},{dtString},{date1}')
            talk(name1+" Marked Present")

        #else:
            #talk(name1+" Already Marked Present")



def detect_cellphone(s,img1):
    classIds, confs, bbox = net.detect(img1, confThreshold=0.4)

    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            if classId - 1 == 76:
                a=76 #cell phone
            elif classId-1 ==0:
                a = 0 #person
            else:
                a = classId-1
            return a

            #cv2.rectangle(img, box, color=(0, 255, 0), thickness=3)
            #cv2.putText(img, classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 255, 0), 2)

def givingproxy(namep,datep):
    with open('proxylist.csv', 'r+')as f:
        myDataListp = f.readlines()
        print(myDataListp)
        namelistp = []
        datelistp = []
        for line in myDataListp:
            entry = line.split(',')
            namelistp.append(entry[0])  # so only all the names will get appended to the list which named as "namelist"
            datelistp.append(entry[2])
        if namep not in namelistp or datep not in datelistp:  # now we are gpoing to check wheater the current name is present in the list or not
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')

            # ddString = now.strftime('%b/%d/%Y')

            f.writelines(f'\n{namep},{dtString},{datep}')





def talk(text):
    engine.say(text)
    engine.runAndWait()



def csvfile_to_xlsx(date):

    #for main Attendance file
    read_file = pd.read_csv(r'MainAttendance.csv')
    fileNameM = "AllmainAttandance\MainAttendance_" + date
    read_file.to_excel(fileNameM + '.xlsx', index=None, header=True)
    fileto_uploadM = fileNameM + '.xlsx'
    print(fileto_uploadM, '\n')

    #for porxylist
    read_fileP = pd.read_csv(r'proxylist.csv')
    fileNameP = "Allproxylist\Proxylist_" + date
    read_fileP.to_excel(fileNameP + '.xlsx', index=None, header=True)
    fileto_uploadP = fileNameP + '.xlsx'
    print(fileto_uploadP, '\n')

    uploadM_to_firebase(fileto_uploadM, date)
    uploadP_to_firebase(fileto_uploadP,date)


def uploadM_to_firebase(MainA,date):
    Firebase = pyrebase.initialize_app(config)
    storage = Firebase.storage()
    blob = storage.child('uploads/' + MainA).put(MainA)
    edia&token=" + blob['downloadTokens']}
    data = {'name': "Date_" + date,
            'url': "https://firebasestorage.googleapis.com/v0/b/firebase_project_name.appspot.com/o/uploads%2FAllmainAttandance%5CMainAttendance_" + date + ".xlsx?alt=media&token=" +
                   blob['downloadTokens']}
    result = firebase.post('/uploads', data)
    print(result)


def uploadP_to_firebase(MainP,date):
    Firebase = pyrebase.initialize_app(config)
    storage = Firebase.storage()
    blob = storage.child('uploads/' + MainP).put(MainP)
    data = {'name': "Date_" + date,
            'url': "https://firebasestorage.googleapis.com/v0/b/firebase_project_name.appspot.com/o/uploads%2FAllproxylist%5CProxylist_" + date + ".xlsx?alt=media&token=" +
                   blob['downloadTokens']}
    result = firebase.post('/proxy', data)
    print(result)


#------------------------------------------------------------functions are given above-----------------------------------------------------------------------

#removing data from Attendance csv file if the date is not today's date
now = datetime.now()
da_te = now.strftime('%b/%d/%Y')
with open('Attendance.csv','r+')as f:
    Alldata = f.readlines()
    date_list = []

    for line in Alldata:
        entry = line.split(',')
        date_list.append(entry[2])
    if da_te not in date_list:
        fl = open('Attendance.csv', 'r+')
        fl.truncate(0)
        #with open('Attendance.csv', 'r+')as f:
        fl.writelines(f'Name,   Time,       Day')
        fl.close()


#removing data from proxy list csv file if the date is not today's date
with open('proxylist.csv','r+')as f:
    Alldatap = f.readlines()
    date_listp = []
    for line in Alldatap:
        entry = line.split(',')
        date_listp.append(entry[2])
    if da_te not in date_listp:
        fl = open('proxylist.csv', 'r+')
        fl.truncate(0)
        #with open('Attendance.csv', 'r+')as f:
        fl.writelines(f'Name,   Time,       Day')
        fl.close()





ts = time.time()
timeStamp = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
Hour, Minute, Second = timeStamp.split(":")
startmin = int(Minute)
timeofupload = startmin+2
maxtimeofupload = startmin+2
print(timeofupload)
print(maxtimeofupload)
talk(Minute+" time of start")

#now we will just need to call this function to encode any input iamge

encodeListKnown = findEncodings(images) #all the images that are present in the folder named as "ImageAttendance" will get encoded and that will be stored in the list named as "encodeListKnown"
#print(len(encodeListKnown)) #It will print 8 as the no of images present in that folder is = 8
print('Encoding Complete......')

#now we need to find the matches between our encodings, so the inages with which we are matching
#we will come from webcam

#so now we will initialise the webcam
cap = cv2.VideoCapture(0)
while True:  #this loop is used to get each frame one by one
    success, img = cap.read()

    #so in real time to speed we the process we need to reduced the size of the image
    # to do this we will use
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #now we need to find the encoding of our web cam
    # so in the webcam we might have multiple images , so for that we are going to find the
    # location of our faces then we are going to send this location to our encoding function

    facesCurFrame = face_recognition.face_locations(imgS) #so here we are finding all locations of our small image in the current frame i.e webcam
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame) #facesCurFrame is passed to metion that where we gonna do our encodings..


    #now we will find the matches between the encodings. So for that we will iterate between the images that we find
    #in our current frame with all the encodings that we previously found and all that are present in   "encodeListKnown"

    for encodeFace , faceLoc in zip(encodesCurFrame,facesCurFrame):
        #now we will do matching
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        print("Printing matches")
        print(matches)
        #now we will find the distances
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)  #since we are sending the  lists to our face_distance function it will also return a list
        # and it will return 3 values since 3 faces are present there. And also
        #it will return the respective distances so , the lowest distance will be our best match
        print("face Distance")
        print(faceDis)

        #so in the list returened by face_distance() function the smallest vlaue / lowest element  will represent the best match
        matchIndex = np.argmin(faceDis)
        #since we have the index so we can talk say that which person we are talking about.


        #function called to check that it's a real person or not
        proxy_val = detect_cellphone(success,img)
        print(proxy_val)


        if matches[matchIndex] and proxy_val==76:
            name = classNames[matchIndex].upper()
            txt = name+" is Giving Proxy"
            y1, x2, y2, x1 = faceLoc
            # y1, x2, y2, x1  = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4)
            cv2.rectangle(img, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, txt, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2)
            givingproxy(name,da_te)
            talk("Attention " + name + " Giving Proxy")

        elif matches[matchIndex] and proxy_val == 0:  #if matches we will display a bounding box around them and we can write their name as well
            name = classNames[matchIndex].upper()
            print(name)
            y1,x2,y2,x1 = faceLoc
            #y1, x2, y2, x1  = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),4)
            cv2.rectangle(img,(x1,y2-20),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,255,255),2)
            #now = datetime.now()
            #ddString = now.strftime('%b/%d/%Y')
            #print(ddString)
            markAttendance(name,da_te)

        elif matches[matchIndex] and (proxy_val!=76 or proxy_val!=0):
            print("Not a person")
            txt = "unknown"+str(proxy_val)
            y1, x2, y2, x1 = faceLoc
            # y1, x2, y2, x1  = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4)
            cv2.rectangle(img, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, txt, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2)
            talk("Unknown Person")

        else:
            txt = "unknown"
            y1, x2, y2, x1 = faceLoc
            # y1, x2, y2, x1  = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4)
            cv2.rectangle(img, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, txt, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2)
            talk("Unknown Person")

    cv2.imshow('ATTENDANCE SYSTEM BY GROUP-79',img)  # and also we will have to show the image in full size (here imshow() is the inbuilt function)
    cv2.waitKey(1)

    ts = time.time()
    timeStamp = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Currentmin, Second = timeStamp.split(":")
    current_min = int(Currentmin)

    if (current_min >= timeofupload):
        talk("Time Over No More Attendance")
        break
    else:
        continue
    break
cap.release()
cv2.destroyAllWindows()

date1 = now.strftime('%b/%d/%Y')
with open('proxylist.csv', 'r+')as fp:
    myDataListp = fp.readlines()
    namelist_p = []

    for line in myDataListp:
        entry = line.split(',')
        namelist_p.append(entry[0])  # so only all the names will get appended to the list which named as "namelist"
    namelist_p.pop(0)
fp.close()

with open('Attendance.csv', 'r+')as f:
    myDataList = f.readlines()
    print(myDataList)
    namelist = []
    datelist = []
    timelist = []
    for line in myDataList:
        entry = line.split(',')
        namelist.append(entry[0])  # so only all the names will get appended to the list which named as "namelist"
        datelist.append(entry[2])
        timelist.append(entry[1])

    namelist.pop(0)
    datelist.pop(0)
    timelist.pop(0)
f.close()

now = datetime.now()
dtString = now.strftime('%H:%M:%S')
a_file = open("MainAttendance.csv", "a")
#a_file.write("\nDATE = %s\n" % (da_te))

a_file.writelines(f'Day,        Name,       Time\n')
#a_file.write("\n")
for nameG,timeA,dateA in zip(namelist,timelist,datelist):
    if (nameG not in namelist_p):
        a_file.writelines("%s,%s,%s\n" % (da_te,nameG,timeA))
    else:
        continue
a_file.close()



#here we will convert the MainAttendanceFile and Proxyfile to XlSX file
ts = time.time()
date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
csvfile_to_xlsx(date) #function is called to for converting the csv file to xlsx files and they in turn called the function which uload this files to firebase storage

#uploadM_to_firebase(MainAttendance_to_upload,da_te)
#uploadP_to_firebase(Proxylist_to_upload,da_te)


#databaseupload()
talk("")
talk("File Uploaded Please Check Attendance")



#------------------------------------------------------------------THANK YOU---------------------------------------------------------------------------------------------------------------






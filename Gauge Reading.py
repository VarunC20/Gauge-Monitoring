import cv2
import sys
import numpy as np
import matplotlib.pyplot as mat
import math
import os
import socket
import time

#Creating function to get square root to obtain distance between line
def dist_2_pts(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

img = cv2.imread("image.png", cv2.IMREAD_GRAYSCALE) #reading image on disk (for grayscale replace cv2.IMREAD_COLOR with 0) 

print(type(img))
print(img.shape)

#crop = img[30:500, 100:550] #crop resolution

ret, thresh = cv2.threshold(img, 70, 255,cv2.THRESH_BINARY)

edges = cv2.Canny(img, 150, 200,apertureSize=3) #edge detection 2nd parameter is lower threshold and 3rd is upper threshold

gray = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

cgray = np.copy(gray)

#1st parameter = output of edge detection
#2nd parameter = rho
#3rd = Theta
#4th = threshold (min no. of interactions to detect line)
#5th = minLineLength (min no. of points that can form line)
#6th = MaxLineGap (Max gap between 2 points tp be considered same line)
linesP = cv2.HoughLinesP(edges,1,np.pi/180, 75,None, 50, 10) 
if linesP is not None:
    for i in range(0, len(linesP)):
        l=linesP[i][0]
        cv2.line(cgray,(l[0], l[1]),(l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)

#cv2.imshow("HP", cgray)

#1st parameter = image name
#2nd = detection method
#3rd = inverse ration of resolution
#4th = min. distance between detected centers
#5th = upper threshold for canny
#6th = threshold for center detection
#7th = min radius to be detected
#8th = max radius to be detected
circles = cv2.HoughCircles(edges,cv2.HOUGH_GRADIENT,1,500,param1=300,param2=30,minRadius=50,maxRadius=0)

circles = np.uint16(np.around(circles))
for j in circles[0,:]:
    cv2.circle(cgray,(j[0],j[1]),j[2],(0,255,0),2) #draws circle

    cv2.circle(cgray,(j[0],j[1]),2,(0,0,255),3) #draws centerpoint

cv2.imshow('detected circles', cgray)

#Dividing Circle in interval of 10 degrees
separation = 10
interval = int(360/separation)
p1 = np.zeros((interval, 2))
p2 = np.zeros((interval, 2))
p_text = np.zeros((interval, 2))

for k in range (0, interval):
    for m in range(0,2):
        if (m%2==0):
            p1[k][m] = (j[0] + 1.2 * j[2] * np.cos(separation * (k) * 3.142/180)) #points for lines
        else:
            p1[k][m] = (j[1] + 1.2 * j[2] * np.sin(separation * (k) * 3.142/180))

text_offset_x = 10
text_offset_y = 5

for k in range(0, interval):
    for m in range(0, 2):
        if (m % 2 == 0):
            p2[k][m] = j[0] + j[2] * np.cos(separation * k * 3.142/180) 
            p_text[k][m] = j[0] - text_offset_x + 1.2 * j[2] * np.cos((separation) * (k+9) * 3.142/180) #points for text
        else:
            p2[k][m] = j[1] + j[2] * np.sin(separation * k * 3.142/180) 
            p_text[k][m] = j[1] - text_offset_x + 1.2 * j[2] * np.sin((separation) * (k+9) * 3.142/180)

for i in range(0, interval):
    cv2.line(cgray, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])), (0, 255, 0), 2)
    cv2.putText(cgray, '%s' %(int(i*separation)), (int(p_text[i][0]), int(p_text[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 1, cv2.LINE_AA)

#cv2.putText(cgray, "Gauge Okay!", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA)
x = j[0]
y = j[1]
r = j[2]

min_angle = 36
max_angle = 324

min_value = 0
max_value = 6

list = []

diff1LB = 0.15
diff1UB = 0.25
diff2LB = 0.5
diff2UB = 1.0

for i in range(0, len(linesP)):
    for x1, y1, x2, y2 in linesP[i]:
        diff1 = dist_2_pts(x, y, x1, y1)
        diff2 = dist_2_pts(x, y, x2, y2)

        if (diff1>diff2):
            temp = diff1
            diff1 = diff2
            diff2 = temp
        if (((diff1<diff1UB*r) and (diff1>diff1LB*r) and (diff2<diff2UB*r)) and (diff2>diff2LB*r)):
            line_length = dist_2_pts(x1, y1, x2, y2)
        list.append([x1, y1, x2, y2])

x1 = list[0][0]
y1 = list[0][1]
x2 = list[0][2]
y2 = list[0][3]

cv2.line(cgray, (x1, y1), (x2, y2), (0, 255, 0), 2)

dist_pt_0 = dist_2_pts(x, y, x1, y1)
dist_pt_1 = dist_2_pts(x, y, x2, y2)

if (dist_pt_0 > dist_pt_1):
    x_angle = x1 - x
    y_angle = y - y1
else:
    x_angle = x2 - x
    y_angle = y - y2

res = np.arctan(np.divide(float(y_angle), float(x_angle)))

res = np.rad2deg(res)
if x_angle > 0 and y_angle > 0:  #in quadrant I
    final_angle = 270 - res
if x_angle < 0 and y_angle > 0:  #in quadrant II
    final_angle = 90 - res
if x_angle < 0 and y_angle < 0:  #in quadrant III
    final_angle = 90 - res
if x_angle > 0 and y_angle < 0:  #in quadrant IV
    final_angle = 270 - res

old_min = float(min_angle)
old_max = float(max_angle)

new_min = float(min_value)
new_max = float(max_value)

old_value = final_angle

old_range = (old_max - old_min)
new_range = (new_max - new_min)
new_value = (((old_value - old_min) * new_range) / old_range) + new_min

print('final value is: ', new_value)

cv2.imshow('detected circles', cgray)

cv2.waitKey(0) #this command holds the screen. As 0 is passed on in the parameters, it will hold the screen uptill user closes the window

cv2.destroyAllWindows()

import email
from email.message import EmailMessage
import ssl
import smtplib
email_sender = 'raspberrypi201998@gmail.com'
email_password = 'jnrjelcqbzsqjwvk'

email_receiver = 'varuntravels20@gmail.com'
v =str(3)
subject = 'Gauge value'
body = "Hi"+ new_value

em = EmailMessage()
em['From']='raspberrypi201998@gmail.com'
em['To']='varuntravels20@gmail.com'
em['subject']=subject
em.set_content(body)

context = ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:

    smtp.login(email_sender,email_password)
    smtp.sendmail(email_sender,email_receiver,em.as_string())



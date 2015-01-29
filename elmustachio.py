import sys
import os
import math
from operator import itemgetter
import numpy as np
import cv2
from PIL import Image

def init():
    global face_cascade
    global eye_cascade
    global mustache
    global sombrero
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    mustache = Image.open('mustache.png').convert('RGBA')
    sombrero = Image.open('sombrero.png')

def goMoustachioGo(filename):
    cvimg = cv2.imread(filename)
    image = Image.open(filename)
    gray = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    threshold = cvimg.shape[0]*cvimg.shape[1]*0.01

    score = 0
    for (x,y,w,h) in faces:
        if w*h > threshold:
            score += w*h/threshold

    if score < 2:
        return None
    else:
        worked = False
        for (x,y,w,h) in faces:
            if w*h > threshold:
                roi_gray = gray[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray)
                candidates = []
                for (ex, ey, ew, eh) in eyes:
                    score = (ew*eh - (w*h*0.058))**2
                    candidates.append((score, x+ex+ew/2, y+ey+eh/2))
                candidates = sorted(candidates, key=itemgetter(0))
                if len(candidates) >= 2:
                    p1 = (candidates[0][1], candidates[0][2])
                    p2 = (candidates[1][1], candidates[1][2])
                    p3 = (x + w/2, y + h/2)
                    scale = (h*w)**0.5
                    angle = math.atan(float(p2[1] - p1[1])/float(p2[0] - p1[0]))
                    sm = scale/2/mustache.size[0]
                    m = mustache.resize((int(mustache.size[0]*sm), int(mustache.size[1]*sm)), Image.BICUBIC).rotate(-angle*360/(2*math.pi), Image.BICUBIC, 1)
                    pm = (int(p3[0] - scale/4*math.sin(angle) - m.size[0]/2), int(p3[1] + scale/4*math.cos(angle) - m.size[1]/2))
                    image.paste(m, box=pm, mask=m)
                    ss = scale*2/sombrero.size[0]
                    s = sombrero.resize((int(sombrero.size[0]*ss), int(sombrero.size[1]*ss)), Image.BICUBIC).rotate(-angle*360/(2*math.pi), Image.BICUBIC, 1)
                    ps = (int(p3[0] + scale/1.5*math.sin(angle) - s.size[0]/2), int(p3[1] - scale/1.5*math.cos(angle) - s.size[1]/2))
                    image.paste(s, box=ps, mask=s)
                    worked = True
        if worked:
            (head, tail) = os.path.split(filename)
            result = os.path.join(head, 'elmustachios-'+tail)
            image.save(result)
            return result
        else:
            return None

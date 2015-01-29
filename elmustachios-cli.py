import sys
import math
from operator import itemgetter
import numpy as np
import cv2
from PIL import Image

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

cvimg = cv2.imread(sys.argv[1])
image = Image.open(sys.argv[1])
mustache = Image.open('mustache.png').convert('RGBA')
sombrero = Image.open('sombrero.png')
gray = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, 1.1, 5)

threshold = cvimg.shape[0]*cvimg.shape[1]*0.01
print('threshold: ' + str(threshold))

score = 0
for (x,y,w,h) in faces:
    print('face surface: ' + str(w*h))
    if w*h > threshold:
        score += w*h/threshold

print('Final score: ' + str(score))
if score < 2:
    print('Not a selfie')
else:
    worked = False
    for (x,y,w,h) in faces:
        if w*h > threshold:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            candidates = []
            for (ex, ey, ew, eh) in eyes:
                score = (ew*eh - (w*h*0.05))**2
                print(str(ew*eh) + ' vs ' + str(w*h*0.05) + ': ' + str(score))
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
                cv2.line(cvimg, p1, p2, (255, 0, 0), 5)
                cv2.line(cvimg, p1, p3, (0, 255, 0), 5)
                cv2.line(cvimg, p3, p2, (0, 255, 0), 5)
    if worked:
        print('ElMustachios!')
        cv2.imwrite('debug-'+sys.argv[1], cvimg)
        image.save('elmustachios-'+sys.argv[1]);
    else:
        print('Too ugly')

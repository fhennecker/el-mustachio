import sys
import os
import math
from operator import itemgetter
import numpy as np
import cv2
from PIL import Image

def matchRect(r1, r2):
    if r2[2]*r2[3] < r1[2]*r1[3]:
        ms = r2[2]*r2[3]
    else:
        ms = r1[2]*r1[3]
    w = min(r1[0]+r1[2], r2[0]+r2[2]) - max(r1[0], r2[0])
    if w < 0:
        w = 0
    h = min(r1[1]+r1[3], r2[1]+r2[3]) - max(r1[1], r2[1])
    if h < 0:
        h = 0
    return w*h/float(ms)



face_cascades = [cv2.CascadeClassifier('haarcascade_frontalface_alt.xml'),
                 cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml'),
                 cv2.CascadeClassifier('haarcascade_frontalface_alt_tree.xml'),
                 cv2.CascadeClassifier('haarcascade_frontalface.xml')]
eye_cascades = [cv2.CascadeClassifier('haarcascade_eye.xml'), 
               cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml'),
               cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml'),
               cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')]

mustache = Image.open('mustache.png').convert('RGBA')
sombrero = Image.open('sombrero.png')

for filename in sys.argv[1:]:

    print(filename+':')

    image = Image.open(filename)
    cvimg = cv2.imread(filename)
    gray = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
    faces = []
    for cascade in face_cascades:
        new_faces = cascade.detectMultiScale(gray, 1.1, 5)
        for nf in new_faces:
            merged = False
            for f in faces:
                if matchRect(f, nf) > 0.8:
                    f[2] = max(f[0] + f[2], nf[0] + nf[2])
                    f[3] = max(f[1] + f[3], nf[1] + nf[3])
                    f[0] = min(f[0], nf[0])
                    f[2] -= f[0]
                    f[1] = min(f[1], nf[1])
                    f[3] -= f[1]
                    merged = True
                    break;
            if not merged:
                faces.append(nf)

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
                candidates = []
                for cascade in eye_cascades:
                    eyes = cascade.detectMultiScale(roi_gray)
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(cvimg, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 0, 0), 1)
                        score = min(1, 1/abs((ew*eh)**0.5 - (w*h*0.058)**0.5))
                        print(str(ew*eh) + ' vs ' + str(w*h*0.058) + ': ' + str(score))
                        merged = False
                        if score > 0.04:
                            for c in candidates:
                                if matchRect(c[1], [x+ex, y+ey, ew, eh]) > 0.8:
                                    c[1][2] = max(c[1][0] + c[1][2], x + ex + ew)
                                    c[1][3] = max(c[1][1] + c[1][3], y + ey + eh)
                                    c[1][0] = min(c[1][0], x + ex)
                                    c[1][2] -= c[1][0]
                                    c[1][1] = min(c[1][1], y + ey)
                                    c[1][3] -= c[1][1]
                                    c[0] += score
                                    merged = True
                                    break;
                            if not merged:
                                candidates.append([score, [x+ex, y+ey, ew, eh]])
                candidates = sorted(candidates, key=itemgetter(0), reverse=True)
                print candidates
                if len(candidates) >= 2:
                    p1 = (int(candidates[0][1][0]+candidates[0][1][2]/2), int(candidates[0][1][1]+candidates[0][1][3]/2))
                    p2 = (int(candidates[1][1][0]+candidates[1][1][2]/2), int(candidates[1][1][1]+candidates[1][1][3]/2))
                    p3 = (x + w/2, y + h/2)
                    scale = (h*w)**0.5
                    angle = math.atan(float(p2[1] - p1[1])/float(p2[0] - p1[0]))
                    if abs(angle) > math.pi/4:
                        break;
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
            (head, tail) = os.path.split(filename)
            cv2.imwrite(os.path.join(head, 'debug-'+tail), cvimg)
            image.save(os.path.join(head, 'elmustachios-'+tail));
        else:
            print('Too ugly')

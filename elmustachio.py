import sys
import os
import math
from operator import itemgetter
import numpy as np
import cv2
from PIL import Image

def init():
    global face_cascades
    global eye_cascades
    global mustache
    global sombrero
    face_cascades = [cv2.CascadeClassifier('haarcascade_frontalface_alt.xml'),
                cv2.CascadeClassifier('haarcascade_frontalface.xml')]
    eye_cascades = [cv2.CascadeClassifier('haarcascade_eye.xml'), 
               cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml'),
               cv2.CascadeClassifier('haarcascade_lefteye_2splits.xml'),
               cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')]

    mustache = Image.open('mustache.png').convert('RGBA')
    sombrero = Image.open('sombrero.png')

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

def mergeRect(r1, r2):
    r1[2] = max(r1[0] + r1[2], r2[0] + r2[2])
    r1[3] = max(r1[1] + r1[3], r2[1] + r2[3])
    r1[0] = min(r1[0], r2[0])
    r1[2] -= r1[0]
    r1[1] = min(r1[1], r2[1])
    r1[3] -= r1[1]
    return r1

def findFaces(gray_img):
    faces = []
    for cascade in face_cascades:
        new_faces = cascade.detectMultiScale(gray_img, 1.1, 5)
        for nf in new_faces:
            merged = False
            for f in faces:
                if matchRect(f, nf) > 0.8:
                    f = mergeRect(f, nf)
                    merged = True
                    break;
            if not merged:
                faces.append(nf)
    return faces

def findEyeCandidates(face_img, ideal_size):
    candidates = []
    for cascade in eye_cascades:
        eyes = cascade.detectMultiScale(face_img)
        for (ex, ey, ew, eh) in eyes:
            score = min(1, 1/abs((ew*eh)**0.5 - ideal_size**0.5))
            merged = False
            if score > 0.04:
                for c in candidates:
                    if matchRect(c[1], [ex, ey, ew, eh]) > 0.8:
                        c[1] = mergeRect(c[1], [ex, ey, ew, eh])
                        c[0] += score
                        merged = True
                        break;
                if not merged:
                    candidates.append([score, [ex, ey, ew, eh]])
    return candidates

def computeFaceGeometry(face, eye1, eye2):
    p_face = (int(face[0] + face[2]/2), int(face[1] + face[3]/2))
    p_eye1 = (int(face[0] + eye1[0] + eye1[2]/2), int(face[1] + eye1[1] + eye1[3]/2))
    p_eye2 = (int(face[0] + eye2[0] + eye2[2]/2), int(face[1] + eye2[1] + eye2[3]/2))
    scale = (face[2]*face[3])**0.5
    angle = math.atan(float(p_eye2[1] - p_eye1[1])/float(p_eye2[0] - p_eye1[0]))
    return (p_face, scale, angle)

def pasteScaledRotatedObject(image, obj, pos, scale, angle):
    transformed = obj.resize((int(obj.size[0]*scale), int(obj.size[1]*scale)), Image.BICUBIC).rotate(-angle*360/(2*math.pi), Image.BICUBIC, 1)
    pos = (pos[0] - transformed.size[0]/2, pos[1] - transformed.size[1]/2)
    image.paste(transformed, box=pos, mask=transformed)

def goMustachioGo(filename):
    cvimg = cv2.imread(filename)
    image = Image.open(filename)
    gray_img = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)

    faces = findFaces(gray_img)
    threshold = cvimg.shape[0]*cvimg.shape[1]*0.01
    faces = filter(lambda x: x[2]*x[3] > threshold, faces)

    score = 0
    for (x,y,w,h) in faces:
        score += w*h/threshold

    if score < 2:
        return None
    else:
        worked = False
        for (x,y,w,h) in faces:
            candidates = findEyeCandidates(gray_img[y:y+h, x:x+w], w*h*0.058)
            candidates = sorted(candidates, key=itemgetter(0), reverse=True)
            if len(candidates) >= 2:
                (p_face, scale, angle) = computeFaceGeometry((x, y, w, h), candidates[0][1], candidates[1][1])
                if abs(angle) > math.pi/4:
                    break;
                mustache_pos = (int(p_face[0] - scale/4*math.sin(angle)), int(p_face[1] + scale/4*math.cos(angle)))
                sombrero_pos = (int(p_face[0] + scale/1.5*math.sin(angle)), int(p_face[1] - scale/1.5*math.cos(angle)))
                pasteScaledRotatedObject(image, mustache, mustache_pos, scale, angle)
                pasteScaledRotatedObject(image, sombrero, sombrero_pos, scale, angle)
                worked = True
        if worked:
            (head, tail) = os.path.split(filename)
            result = os.path.join(head, 'elmustachios-'+tail)
            image.save(result)
            return result
        else:
            return None

                   

from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np                
import argparse
import imutils
import time
import dlib
import cv2
import math
import time
from threading import Thread

def eye_aspect_ratio(eye):
                  
    A = dist.euclidean(eye[1], eye[5])                 
    B = dist.euclidean(eye[2], eye[4])
                   
                  
    C = dist.euclidean(eye[0], eye[3])
              
    ear = (A + B) / (2.0 * C)
              
    return ear

def mouth_aspect_ratio(mouth):      
    A = np.linalg.norm(mouth[2] - mouth[10])          
    B = np.linalg.norm(mouth[4] - mouth[8])          
    C = np.linalg.norm(mouth[0] - mouth[6])          
    mar = (A + B) / (2.0 * C)
    return mar

                                
print("[INFO] loading facial landmark predictor...")
                                              
detector = dlib.get_frontal_face_detector()
                                   
predictor = dlib.shape_predictor('weights/shape_predictor_68_face_landmarks.dat')
                
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

         
def detfatigue(frame):
                                             
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                  
    rects = detector(gray, 0)
    eyear = 0.0
    mouthar = 0.0
                                                 
    for rect in rects:
        shape = predictor(gray, rect)

                              
        shape = face_utils.shape_to_np(shape)

                   
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
              
        mouth = shape[mStart:mEnd]

                                      
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        eyear = (leftEAR + rightEAR) / 2.0
             
        mouthar = mouth_aspect_ratio(mouth)

                
                                                           
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        mouthHull = cv2.convexHull(mouth)
        cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)

                    
        cv2.line(frame,tuple(shape[38]),tuple(shape[40]),(0, 255, 0), 1)
        cv2.line(frame,tuple(shape[43]),tuple(shape[47]),(0, 255, 0), 1)
        cv2.line(frame,tuple(shape[51]),tuple(shape[57]),(0, 255, 0), 1)
        cv2.line(frame,tuple(shape[48]),tuple(shape[54]),(0, 255, 0), 1)

          
                        
                  
                    
    return(frame,eyear,mouthar)
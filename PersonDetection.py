import cv2
import numpy as np

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detect_person(frame):

    boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))
    
    if len(boxes) > 0:
        return max(boxes, key=lambda box: box[2] * box[3])
    return None

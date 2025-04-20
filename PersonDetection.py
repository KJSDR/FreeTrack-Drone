import cv2
import numpy as np

# Init person detection w/ HOG descriptor
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detect_person(frame):
    # Detect people
    boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))
    
    # Return coordinates of biggrst box
    if len(boxes) > 0:
        return max(boxes, key=lambda box: box[2] * box[3])
    return None

# import matplotlib.pyplot as plt
import numpy as np
import cv2

def create_detector():
    params = cv2.SimpleBlobDetector_Params()
    # Set Area filtering parameters
    params.filterByArea = True
    # params.minArea = 500
    params.minArea = 300

    # Set Circularity filtering parameters
    params.filterByCircularity = True
    params.minCircularity = 0.2

    # Set Convexity filtering parameters
    params.filterByConvexity = True
    params.minConvexity = 0.70

    # Set inertia filtering parameters
    params.filterByInertia = False
    params.minInertiaRatio = 0.01

    # Create a detector with the parameters
    return cv2.SimpleBlobDetector_create(params)


def detect_blobs(path):
    img = cv2.imread(path,0)
    detector = create_detector()
    
    keypoints = detector.detect(img)

    # Draw blobs on our image as red circles
    blank = np.zeros((1, 1))
    img_blobs = cv2.drawKeypoints(img, keypoints, blank, (0, 0, 255),
                              cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    return keypoints, img_blobs

def detect_blobs_img(img):

    # img = cv2.imread(path,0)
    detector = create_detector()
    
    keypoints = detector.detect(img)

    # Draw blobs on our image as red circles
    blank = np.zeros((1, 1))
    img_blobs = cv2.drawKeypoints(img, keypoints, blank, (0, 0, 255),
                              cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    return keypoints, img_blobs

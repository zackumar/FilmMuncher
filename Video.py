from threading import Thread
import cv2
import numpy as np

import math
import time


class Video:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.values = {}

        self.cropped = None
        self.gray = None
        self.edges = None
        self.eDilate = None
        self.eErode = None
        self.cdst = None
        self.cropCopy = None

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        dKernel = np.ones((7, 7), np.uint8)
        eKernel = np.ones((5, 5), np.uint8)

        activeCount = 0
        isPicture = False
        takePicture = True

        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()
                if (self.values == {}):
                    continue

                values = self.values

                if (type(values['topCrop']) is not int or type(values['bottomCrop']) is not int or type(values['leftCrop']) is not int or type(values['rightCrop']) is not int or values['topCrop'] > values['bottomCrop'] or values['leftCrop'] > values['rightCrop']):
                    continue

                self.cropped = self.frame[values['topCrop']: values['bottomCrop'],
                                          values['leftCrop']: values['rightCrop']]

                self.cropCopy = 255 - self.cropped.copy()

                blur = cv2.GaussianBlur(self.cropped, (5, 5), 0)

                self.gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

                self.edges = cv2.Canny(self.gray, values['cannyMin'],
                                       values['cannyMax'], apertureSize=3)
                self.eDilate = cv2.dilate(self.edges, dKernel)
                self.eErode = cv2.erode(self.eDilate, eKernel)
                self.cdst = cv2.cvtColor(self.eErode, cv2.COLOR_GRAY2BGR)

                linesP = cv2.HoughLinesP(self.eErode, 1, np.pi / 180,
                                         int(values['houghThresh']), None, 50, int(values['houghGap']))

                possibleEdges = []
                leftActive = False
                rightActive = False

                color = (0, 255, 255)

                leftRect = ((0, 0), (int(values['leftTarget']),
                                     int(values['bottomCrop']) - int(values['topCrop'])))
                rightRect = ((int(values['rightCrop']) - int(values['leftCrop']), 0), (int(values['rightCrop']) -
                                                                                       int(values['leftCrop']) - int(values['rightTarget']), int(values['bottomCrop']) - int(values['topCrop'])))

                if linesP is not None:
                    for line in linesP:
                        (x1, y1, x2, y2) = line[0]
                        angle = math.atan2(y2 - y1, x2 - x1) * 180.0 / np.pi
                        lineLen = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                        if (abs(angle) > values['minAngle']):

                            if (lineLen >= values['lineLength']):
                                possibleEdges.append(line)
                                cv2.line(self.cdst, (x1, y1), (x2, y2),
                                         (0, 0, 255), 3, cv2.LINE_AA)
                                cv2.line(self.cropCopy, (x1, y1), (x2, y2),
                                         (0, 0, 255), 3, cv2.LINE_AA)

                                if x1 <= values['leftTarget'] and x2 <= values['leftTarget']:
                                    leftActive = True
                                elif x1 >= values['rightCrop'] - values['leftCrop'] - values['rightTarget'] and x2 >= values['rightCrop'] - values['leftCrop'] - values['rightTarget']:
                                    rightActive = True

                if (leftActive and rightActive):
                    color = (0, 255, 0)
                    activeCount += 1
                    if (activeCount >= values['activeForPicture']):
                        isPicture = True

                    if (isPicture and takePicture):
                        takePicture = False
                        print('Take Picture')

                else:
                    isPicture = False
                    takePicture = True
                    activeCount = 0

                # print(isPicture, takePicture)

                cv2.rectangle(self.cdst, leftRect[0],
                              leftRect[1], color, 5)
                cv2.rectangle(self.cdst, rightRect[0],
                              rightRect[1], color, 5)

                cv2.rectangle(self.cropCopy, leftRect[0],
                              leftRect[1], color, 5)
                cv2.rectangle(self.cropCopy, rightRect[0],
                              rightRect[1], color, 5)

    def stop(self):
        self.stopped = True

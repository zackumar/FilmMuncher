from threading import Thread
import cv2
import numpy as np

import math
import logging


class Extractor:
    """Extracting film frames from a video stream using edge detection

    :param src: Video source
    :param camera: Camera object
    """

    def __init__(self, src, camera, motor):
        self.src = src
        self.motor = motor
        self.camera = camera
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.values = {}

        # display copies (so main thread doesn't stutter when working copies are drawing)
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
        logging.debug("Extractor started")
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
                if self.values == {} or self.values == None:
                    continue

                if self.stream == None or not self.stream.isOpened():
                    logging.error("Video stream not opened")
                    break

                values = self.values

                if (
                    type(values["topCrop"]) is not int
                    or type(values["bottomCrop"]) is not int
                    or type(values["leftCrop"]) is not int
                    or type(values["rightCrop"]) is not int
                    or values["topCrop"] > values["bottomCrop"]
                    or values["leftCrop"] > values["rightCrop"]
                ):
                    continue

                cropped = self.frame[
                    values["topCrop"]: values["bottomCrop"],
                    values["leftCrop"]: values["rightCrop"],
                ]

                cropCopy = 255 - cropped.copy()

                blur = cv2.GaussianBlur(cropped, (5, 5), 0)

                gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

                edges = cv2.Canny(
                    gray, values["cannyMin"], values["cannyMax"], apertureSize=3
                )
                eDilate = cv2.dilate(edges, dKernel)
                eErode = cv2.erode(eDilate, eKernel)
                cdst = cv2.cvtColor(eErode, cv2.COLOR_GRAY2BGR)

                linesP = cv2.HoughLinesP(
                    eErode,
                    1,
                    np.pi / 180,
                    int(values["houghThresh"]),
                    None,
                    50,
                    int(values["houghGap"]),
                )

                possibleEdges = []
                leftActive = False
                rightActive = False

                color = (0, 255, 255)

                leftRect = (
                    (0, 0),
                    (
                        int(values["leftTarget"]),
                        int(values["bottomCrop"]) - int(values["topCrop"]),
                    ),
                )
                rightRect = (
                    (int(values["rightCrop"]) - int(values["leftCrop"]), 0),
                    (
                        int(values["rightCrop"])
                        - int(values["leftCrop"])
                        - int(values["rightTarget"]),
                        int(values["bottomCrop"]) - int(values["topCrop"]),
                    ),
                )

                if linesP is not None:
                    for line in linesP:
                        (x1, y1, x2, y2) = line[0]
                        angle = math.atan2(y2 - y1, x2 - x1) * 180.0 / np.pi
                        lineLen = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                        if abs(angle) > values["minAngle"]:

                            if lineLen >= values["lineLength"]:
                                possibleEdges.append(line)
                                cv2.line(
                                    cdst,
                                    (x1, y1),
                                    (x2, y2),
                                    (0, 0, 255),
                                    3,
                                    cv2.LINE_AA,
                                )
                                cv2.line(
                                    cropCopy,
                                    (x1, y1),
                                    (x2, y2),
                                    (0, 0, 255),
                                    3,
                                    cv2.LINE_AA,
                                )

                                if (
                                    x1 <= values["leftTarget"]
                                    and x2 <= values["leftTarget"]
                                ):
                                    leftActive = True
                                elif (
                                    x1
                                    >= values["rightCrop"]
                                    - values["leftCrop"]
                                    - values["rightTarget"]
                                    and x2
                                    >= values["rightCrop"]
                                    - values["leftCrop"]
                                    - values["rightTarget"]
                                ):
                                    rightActive = True

                if leftActive and rightActive:
                    color = (0, 255, 0)
                    activeCount += 1
                    logging.debug(activeCount)
                    if activeCount >= values["activeForPicture"]:
                        isPicture = True

                    if isPicture and takePicture and values["takePictures"]:
                        self.motor.queue.put((0, 0))
                        takePicture = False
                        logging.debug("Take Picture")

                        self.stream.release()
                        self.camera.takePicture()
                        self.stream = cv2.VideoCapture(self.src)

                        self.motor.queue.put((1, 100))

                else:
                    isPicture = False
                    takePicture = True
                    activeCount = 0

                cv2.rectangle(cdst, leftRect[0], leftRect[1], color, 5)
                cv2.rectangle(cdst, rightRect[0], rightRect[1], color, 5)

                cv2.rectangle(cropCopy, leftRect[0], leftRect[1], color, 5)
                cv2.rectangle(cropCopy, rightRect[0], rightRect[1], color, 5)

                self.cropped = cropped
                self.gray = gray
                self.edges = edges
                self.eDilate = eDilate
                self.eErode = eErode
                self.cdst = cdst
                self.cropCopy = cropCopy

    def stop(self):
        self.stopped = True
        logging.debug("Releasing video")
        # self.stream.release()
        logging.debug("Video released")

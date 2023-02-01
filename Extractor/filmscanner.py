import pickle
import logging
import time
import signal
import sys

import cv2
import numpy as np

import PySimpleGUI as sg
from extractor import Extractor
from camera import Camera
from motor import MotorController

from utils import *


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s:  %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("debug.log", mode="w")],
)


def close():
    logging.debug("Closing")

    if video:
        video.stop()
        time.sleep(0.5)
    if motor:
        motor.stop()
    if camera:
        camera.stopVideo()
    window.close()


signal.signal(signal.SIGINT, close)

DEFAULT_WIDTH = 960
DEFAULT_HEIGHT = 640

blank = np.zeros((640, 960, 3), np.uint8)
cv2.putText(
    blank,
    "Waiting for video stream...",
    (100, 100),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255, 255, 255),
    2,
    cv2.LINE_AA,
)

defaults = {
    "topCrop": 0,
    "bottomCrop": DEFAULT_HEIGHT,
    "leftCrop": 0,
    "rightCrop": DEFAULT_WIDTH,
    "view": 0,
    "cannyMin": 45,
    "cannyMax": 160.0,
    "houghThresh": 130.0,
    "houghGap": 12.0,
    "lineLength": 50.0,
    "minAngle": 87.0,
    "leftTarget": 50.0,
    "rightTarget": 50.0,
    "activeForPicture": 20.0,
    "inactiveForPicture": 200.0,
    "motorSpeed": 200,
    "motorCCW": False,
}

try:
    logging.info("Loading settings...")
    defaults = pickle.load(open("./settings.pickle", "rb"))
    logging.info("Loaded settings: ", defaults)
except:
    logging.info("No settings found, using defaults.")
    pass

sg.theme("DarkGray13")

frame1 = [
    [sg.Text("Video:", font=("Helvetica", 14))],
    [sg.Text("Crop:", font=("Helvetica", 14))],
    [
        sg.Text("Top:"),
        sg.Spin(
            [i for i in range(0, DEFAULT_HEIGHT)],
            initial_value=defaults["topCrop"],
            size=(5, 1),
            key="topCrop",
        ),
    ],
    [
        sg.Text("Bottom:"),
        sg.Spin(
            [i for i in range(1, DEFAULT_HEIGHT + 1)],
            initial_value=defaults["bottomCrop"],
            size=(5, 1),
            key="bottomCrop",
        ),
    ],
    [
        sg.Text("Left:"),
        sg.Spin(
            [i for i in range(0, DEFAULT_WIDTH)],
            initial_value=defaults["leftCrop"],
            size=(5, 1),
            key="leftCrop",
        ),
    ],
    [
        sg.Text("Right:"),
        sg.Spin(
            [i for i in range(1, DEFAULT_WIDTH + 1)],
            initial_value=defaults["rightCrop"],
            size=(5, 1),
            key="rightCrop",
        ),
    ],
    [sg.Text("_" * 35)],
    [sg.Text("CV:", font=("Helvetica", 14))],
    [
        sg.Text("View:"),
        sg.Spin(
            [i for i in range(0, 7)],
            initial_value=defaults["view"],
            size=(5, 1),
            key="view",
        ),
    ],
    [
        sg.Text("Canny Min:"),
        sg.Slider(
            range=(0, 255),
            orientation="h",
            size=(15, 15),
            default_value=defaults["cannyMin"],
            key="cannyMin",
        ),
    ],
    [
        sg.Text("Canny Max:"),
        sg.Slider(
            range=(0, 255),
            orientation="h",
            size=(15, 15),
            default_value=defaults["cannyMax"],
            key="cannyMax",
        ),
    ],
    [
        sg.Text("Hough Thresh:"),
        sg.Slider(
            range=(0, 255),
            orientation="h",
            size=(15, 15),
            default_value=defaults["houghThresh"],
            key="houghThresh",
        ),
    ],
    [
        sg.Text("Hough Gap:"),
        sg.Slider(
            range=(0, 255),
            orientation="h",
            size=(15, 15),
            default_value=defaults["houghGap"],
            key="houghGap",
        ),
    ],
    [
        sg.Text("Line Length"),
        sg.Slider(
            range=(0, 255),
            orientation="h",
            size=(15, 15),
            default_value=defaults["lineLength"],
            key="lineLength",
        ),
    ],
    [
        sg.Text("Min Angle"),
        sg.Slider(
            range=(0, 91),
            orientation="h",
            size=(15, 15),
            default_value=defaults["minAngle"],
            key="minAngle",
        ),
    ],
    [
        sg.Text("Left Target"),
        sg.Slider(
            range=(0, 255),
            orientation="h",
            size=(15, 15),
            default_value=defaults["leftTarget"],
            key="leftTarget",
        ),
    ],
    [
        sg.Text("Right Target"),
        sg.Slider(
            range=(0, 255),
            orientation="h",
            size=(15, 15),
            default_value=defaults["rightTarget"],
            key="rightTarget",
        ),
    ],
    [sg.Text("_" * 35)],
    [sg.Text("Picture:", font=("Helvetica", 14))],
    [
        sg.Text("Active for picture"),
        sg.Slider(
            range=(0, 255),
            orientation="h",
            size=(15, 15),
            default_value=defaults["activeForPicture"],
            key="activeForPicture",
        ),
    ],
    [
        sg.Text("Inactive before picture"),
        sg.Slider(
            range=(0, 1000),
            orientation="h",
            size=(15, 15),
            default_value=defaults["inactiveForPicture"],
            key="inactiveForPicture",
        ),
    ],
    [sg.Checkbox("Take Pictures", default=False, key="takePictures")],
    [sg.Button("Capture", size=(10, 1))],
    [
        sg.Text("Motor Speed"),
        sg.Slider(
            range=(0, 1000),
            orientation="h",
            size=(15, 15),
            default_value=defaults["motorSpeed"],
            key="motorSpeed",
        ),
    ],
    [sg.Checkbox("Motor CCW", default=defaults["motorCCW"], key="motorCCW")],
    [
        sg.Button("<", key="motorLeft"),
        sg.Button("Stop", key="motorStop"),
        sg.Button(">", key="motorRight"),
    ],
    [
        sg.Button("Save", size=(10, 1), pad=(5, 20)),
        sg.Button("Default", size=(10, 1), pad=(5, 20)),
        sg.Button("Close"),
    ],
]

frame2 = [
    [
        sg.Image(
            key="image",
            data=(cv2.imencode(".png", cv2.resize(blank, (960, 640)))[1].tobytes()),
            size=(DEFAULT_WIDTH, DEFAULT_HEIGHT),
        )
    ]
]

# Define the window's contents
layout = [
    [
        sg.Frame(
            "Controls",
            [
                [
                    sg.Column(
                        frame1,
                        scrollable=True,
                        vertical_scroll_only=True,
                        size=(None, DEFAULT_HEIGHT),
                    )
                ]
            ],
            font=("Helvetica", 16),
        ),
        sg.Frame("Video", frame2, font=("Helvetica", 16)),
    ],
]

isMock = len(sys.argv) > 1 and sys.argv[1] == "mock"
if isMock:
    logging.info("Using mock camera")

window = sg.Window(
    "Film Scanner",
    layout,
    icon=ICON,
    finalize=True,
)

camera = Camera(scalingFactor=0.5, mock=isMock)

if not camera.startVideo():
    createErrorAndClose(
        "No camera detected by gphoto2. Make sure your camera is supported by libghoto and try again.\nIt may help to power cycle your camera.",
        "No Camera",
        camera.stopVideo,
        [sg.Text('You can also use a mock camera by passing "mock" as an argument')],
    )

motor = MotorController()
ports = motor.getPorts()
port = None
for p in ports:
    if "Pico" in p.description:
        port = p.device
        break
if port is None:
    logging.error("No serial device found")
    port = createError(
        "No serial device found. Please connect a serial device and try again.\nOtherwise you can continue without a motor controller and manually push film",
        "No Serial Device Found",
        func=camera.stopVideo,
        layout=[sg.Text("If using a mock port, enter here:"), sg.Input(key="port")],
    )["port"]

logging.debug(port)
motor.start(port)

video = Extractor(
    "udp://127.0.0.1:8080/feed.mjpg?fifo_size=10000000", camera, motor
).start()

while True:
    event, values = window.read(timeout=10)
    video.values = values

    if values:
        if type(values["bottomCrop"]) is int and values["bottomCrop"] > camera.height:
            window["bottomCrop"].update(camera.height)
        elif type(values["rightCrop"]) is int and values["rightCrop"] > camera.width:
            window["rightCrop"].update(camera.width)

    if event == sg.WINDOW_CLOSED or event == "Close":
        close()
        break

    elif event == "Save":
        logging.debug("Saving settings")
        pickle.dump(
            values, open("./settings.pickle", "wb+"), protocol=pickle.HIGHEST_PROTOCOL
        )

    elif event == "Default":
        for key in defaults:
            window[key].update(defaults[key])

    elif event == "Capture":
        camera.takePicture()
    elif event == "motorLeft":
        motor.queue.put((1, 300))
    elif event == "motorRight":
        motor.queue.put((-1, 300))
    elif event == "motorStop":
        motor.queue.put((0, 0))

    viewNum = values["view"]
    imgbytes = None

    if (
        video.frame is not None
        and video.cropped is not None
        and video.gray is not None
        and video.edges is not None
        and video.eDilate is not None
        and video.eErode is not None
        and video.cdst is not None
        and video.cropCopy is not None
    ):
        if viewNum == 0:
            imgbytes = cv2.imencode(".png", cv2.resize(video.cropped, (960, 640)))[
                1
            ].tobytes()
        if viewNum == 1:
            imgbytes = cv2.imencode(".png", cv2.resize(video.gray, (960, 640)))[
                1
            ].tobytes()
        elif viewNum == 2:
            imgbytes = cv2.imencode(".png", cv2.resize(video.edges, (960, 640)))[
                1
            ].tobytes()
        elif viewNum == 3:
            imgbytes = cv2.imencode(".png", cv2.resize(video.eDilate, (960, 640)))[
                1
            ].tobytes()
        elif viewNum == 4:
            imgbytes = cv2.imencode(".png", cv2.resize(video.eErode, (960, 640)))[
                1
            ].tobytes()
        elif viewNum == 5:
            imgbytes = cv2.imencode(".png", cv2.resize(video.cdst, (960, 640)))[
                1
            ].tobytes()
        elif viewNum == 6:
            imgbytes = cv2.imencode(".png", cv2.resize(video.cropCopy, (960, 640)))[
                1
            ].tobytes()

    window["image"].update(data=imgbytes)

window.close()
sys.exit(0)

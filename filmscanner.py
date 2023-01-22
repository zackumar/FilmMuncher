import pickle
import logging
import time
import signal

import cv2

import PySimpleGUI as sg
from Video import Video
from camera import Camera


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(thread)s:  %(message)s',
                    handlers=[logging.StreamHandler()])


def close(signal=None, frame=None):
    print('Close')
    video.stop()
    time.sleep(0.1)
    camera.stopVideo()
    window.close()
    exit(0)


signal.signal(signal.SIGINT, close)

DEFAULT_WIDTH = 960
DEFAULT_HEIGHT = 640

defaults = {'topCrop': 0, 'bottomCrop': DEFAULT_HEIGHT, 'leftCrop': 0, 'rightCrop': DEFAULT_WIDTH, 'view': 0, 'cannyMin': 30.0, 'cannyMax': 60.0,
            'houghThresh': 130.0, 'houghGap': 12.0, 'lineLength': 50.0, 'minAngle': 87.0, 'leftTarget': 45.0, 'rightTarget': 45.0, 'activeForPicture': 20.0}

try:
    logging.info("Loading settings...")
    defaults = pickle.load(open("./settings.pickle", "rb"))
except:
    logging.info("No settings found, using defaults.")
    pass

sg.theme('Black')


frame1 = [
    [sg.Text("Video:", font=("Helvetica", 14))],
    [sg.Text("Crop:", font=("Helvetica", 14))],
    [sg.Text("Top:"), sg.Spin([i for i in range(0, DEFAULT_HEIGHT)],
                              initial_value=defaults['topCrop'], size=(5, 1), key="topCrop")],
    [sg.Text("Bottom:"), sg.Spin([i for i in range(1, DEFAULT_HEIGHT + 1)],
                                 initial_value=defaults['bottomCrop'], size=(5, 1), key="bottomCrop")],
    [sg.Text("Left:"), sg.Spin([i for i in range(0, DEFAULT_WIDTH)],
                               initial_value=defaults['leftCrop'], size=(5, 1), key="leftCrop")],
    [sg.Text("Right:"), sg.Spin([i for i in range(1, DEFAULT_WIDTH+1)],
                                initial_value=defaults['rightCrop'], size=(5, 1), key="rightCrop")],
    [sg.Text('_'*35)],
    [sg.Text("CV:", font=("Helvetica", 14))],
    [sg.Text("View:"), sg.Spin([i for i in range(0, 7)],
                               initial_value=defaults['view'], size=(5, 1), key="view")],
    [sg.Text("Canny Min:"), sg.Slider(range=(0, 255),
                                      orientation='h', size=(15, 15), default_value=defaults['cannyMin'], key="cannyMin")],
    [sg.Text("Canny Max:"), sg.Slider(range=(0, 255),
                                      orientation='h', size=(15, 15), default_value=defaults['cannyMax'], key="cannyMax")],
    [sg.Text("Hough Thresh:"), sg.Slider(range=(0, 255),
                                         orientation='h', size=(15, 15), default_value=defaults['houghThresh'], key="houghThresh")],
    [sg.Text("Hough Gap:"), sg.Slider(range=(0, 255),
                                      orientation='h', size=(15, 15), default_value=defaults['houghGap'], key="houghGap")],
    [sg.Text("Line Length"), sg.Slider(range=(0, 255),
                                       orientation='h', size=(15, 15), default_value=defaults['lineLength'], key="lineLength")],
    [sg.Text("Min Angle"), sg.Slider(range=(0, 91),
                                     orientation='h', size=(15, 15), default_value=defaults['minAngle'], key="minAngle")],
    [sg.Text("Left Target"), sg.Slider(range=(0, 255),
                                       orientation='h', size=(15, 15), default_value=defaults['leftTarget'], key="leftTarget")],
    [sg.Text("Right Target"), sg.Slider(range=(0, 255),
                                        orientation='h', size=(15, 15), default_value=defaults['rightTarget'], key="rightTarget")],
    [sg.Text('_'*35)],
    [sg.Text("Picture:", font=("Helvetica", 14))],
    [sg.Text("Active for picture"), sg.Slider(range=(0, 255),
                                              orientation='h', size=(15, 15), default_value=defaults['activeForPicture'], key="activeForPicture")],
    [sg.Button('Capture', size=(10, 1), pad=(5, 20))],
    [sg.Button('Save', size=(10, 1), pad=(5, 20)), sg.Button(
        'Default', size=(10, 1), pad=(5, 20)), sg.Button('Close')]]

frame2 = [
    [sg.Image(filename='', key='image', size=(DEFAULT_WIDTH, DEFAULT_HEIGHT))]]

# # Define the window's contents
layout = [[sg.Frame('Controls', frame1, font=("Helvetica", 16)),
           sg.Frame('Video', frame2, font=("Helvetica", 16))],
          ]


window = sg.Window('Film Scanner', layout, location=(0, 0),
                   finalize=True)

camera = Camera(scalingFactor=.3)
camera.startVideo()

video = Video('udp://127.0.0.1:8080/feed.mjpg?fifo_size=10000000').start()


while True:
    event, values = window.read(timeout=10)
    video.values = values

    if (values):
        if type(values['bottomCrop']) is int and values['bottomCrop'] > camera.height:
            window['bottomCrop'].update(camera.height)
        elif type(values['rightCrop']) is int and values['rightCrop'] > camera.width:
            window['rightCrop'].update(camera.width)

    if event == sg.WINDOW_CLOSED or event == 'Close':
        close()

    elif event == 'Save':
        logging.debug("Saving settings:", values)
        pickle.dump(values, open("./settings.pickle", "wb+"),
                    protocol=pickle.HIGHEST_PROTOCOL)

    elif event == 'Capture':
        camera.takePicture()

    viewNum = values['view']

    testFrame = cv2.resize(video.frame, (960, 640))

    imgbytes = cv2.imencode(".png", testFrame)[1].tobytes()
    if (viewNum == 1):
        imgbytes = cv2.imencode(".png", cv2.resize(
            video.gray, (960, 640)))[1].tobytes()
    elif (viewNum == 2):
        imgbytes = cv2.imencode(".png", cv2.resize(
            video.edges, (960, 640)))[1].tobytes()
    elif (viewNum == 3):
        imgbytes = cv2.imencode(".png", cv2.resize(
            video.eDilate, (960, 640)))[1].tobytes()
    elif (viewNum == 4):
        imgbytes = cv2.imencode(".png", cv2.resize(
            video.eErode, (960, 640)))[1].tobytes()
    elif (viewNum == 5):
        imgbytes = cv2.imencode(".png", cv2.resize(
            video.cdst, (960, 640)))[1].tobytes()
    elif (viewNum == 6):
        imgbytes = cv2.imencode(".png", cv2.resize(
            video.cropCopy, (960, 640)))[1].tobytes()

    window["image"].update(data=imgbytes)

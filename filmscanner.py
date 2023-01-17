import pickle
import math
import threading

import cv2
import numpy as np

import PySimpleGUI as sg
from Video import Video

sg.theme('Black')   # Add a touch of color

DEFAULT_WIDTH = 960
DEFAULT_HEIGHT = 640

defaults = {'topCrop': 0, 'bottomCrop': DEFAULT_HEIGHT, 'leftCrop': 0, 'rightCrop': DEFAULT_WIDTH, 'view': 0, 'cannyMin': 30.0, 'cannyMax': 60.0,
            'houghThresh': 130.0, 'houghGap': 12.0, 'lineLength': 50.0, 'minAngle': 87.0, 'leftTarget': 45.0, 'rightTarget': 45.0, 'activeForPicture': 20.0}

try:
    print("Loading settings...")
    defaults = pickle.load(open("./settings.pickle", "rb"))
except:
    print("No settings found, using defaults.")
    pass

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
    [sg.Button('Save', size=(10, 1), pad=(5, 20)), sg.Button(
        'Default', size=(10, 1), pad=(5, 20)), sg.Button('Close')]]

frame2 = [[sg.Image(filename='', key='image')]]

# # Define the window's contents
layout = [[sg.Frame('Controls', frame1, font=("Helvetica", 16)),
           sg.Frame('Video', frame2, font=("Helvetica", 16))],
          ]


window = sg.Window('Film Scanner', layout, location=(0, 0), finalize=True)

video = Video('udp://localhost:8080/feed.mjpg?fifo_size=10000000').start()

while True:
    event, values = window.read(timeout=10)
    video.values = values

    if event == sg.WINDOW_CLOSED or event == 'Close':
        video.stop()
        break

    elif event == 'Save':
        pickle.dump(values, open("./settings.pickle", "wb+"),
                    protocol=pickle.HIGHEST_PROTOCOL)

    viewNum = values['view']
    imgbytes = cv2.imencode(".png", video.frame)[1].tobytes()

    if (viewNum == 1):
        imgbytes = cv2.imencode(".png", video.gray)[1].tobytes()
    elif (viewNum == 2):
        imgbytes = cv2.imencode(".png", video.edges)[1].tobytes()
    elif (viewNum == 3):
        imgbytes = cv2.imencode(".png", video.eDilate)[1].tobytes()
    elif (viewNum == 4):
        imgbytes = cv2.imencode(".png", video.eErode)[1].tobytes()
    elif (viewNum == 5):
        imgbytes = cv2.imencode(".png", video.cdst)[1].tobytes()
    elif (viewNum == 6):
        imgbytes = cv2.imencode(".png", video.cropCopy)[1].tobytes()

    window["image"].update(data=imgbytes)

print(values)

# Finish up by removing from the screen
window.close()

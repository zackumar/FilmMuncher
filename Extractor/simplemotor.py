import PySimpleGUI as sg
from motor import MotorController

motor = MotorController().start()

layout = [[sg.Button("<", key="motorLeft"),
           sg.Button("Stop", key="motorStop"),
           sg.Button(">", key="motorRight"),],
          ]

window = sg.Window(
    "Simple Motor Controller",
    layout,
    finalize=True)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == "motorLeft":
        motor.queue.put((1, 200))
    if event == "motorStop":
        motor.queue.put((0, 0))
    if event == "motorRight":
        motor.queue.put((-1, 200))

window.close()

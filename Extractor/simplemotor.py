import PySimpleGUI as sg
from motor import MotorController

motor = MotorController()
ports = motor.getPorts()
for port in ports:
    print(port)

layout = [[sg.Text("Select port"), sg.Push(), sg.Text("Disconnected", key="status")],
          [sg.Combo([p.device for p in ports], key="port"),
           sg.Button("Start", key="start")],
          [sg.Button("<", key="motorLeft"),
           sg.Button("Stop", key="motorStop"),
           sg.Button(">", key="motorRight"), sg.Push(), sg.Button("Close")],
          ]

window = sg.Window(
    "Simple Motor Controller",
    layout,
    finalize=True)

connected = False

while True:
    if (connected == False):
        window['motorLeft'].update(disabled=True)
        window['motorStop'].update(disabled=True)
        window['motorRight'].update(disabled=True)

    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Close":
        motor.stop()
        break

    if event == "start" and values["port"]:
        window['status'].update("Connected")
        print(values["port"])
        motor.start(values["port"])
        connected = True
        window['motorLeft'].update(disabled=False)
        window['motorStop'].update(disabled=False)
        window['motorRight'].update(disabled=False)

    if event == "motorLeft":
        motor.queue.put((1, 400))
    if event == "motorStop":
        motor.queue.put((0, 0))
    if event == "motorRight":
        motor.queue.put((-1, 300))

window.close()

import PySimpleGUI as sg
from motor import MotorController

motor = MotorController()
ports = motor.getPorts()
for port in ports:
    print(port)

layout = [
    [sg.Text("Select port"), sg.Push(), sg.Text("Disconnected", key="status")],
    [sg.InputText(key="port"), sg.Button("Start")],
    [
        sg.Button("<", key="motorLeft"),
        sg.Button("Stop", key="motorStop"),
        sg.Button(">", key="motorRight"),
        sg.Push(),
        sg.Button("Close"),
    ],
]

window = sg.Window(
    "Simple Motor Controller",
    layout,
    icon=b"iVBORw0KGgoAAAANSUhEUgAAAEgAAABIBAMAAACnw650AAAAD1BMVEVHcEwjHyD1+Pq73fWIyfl/HgzbAAAAAXRSTlMAQObYZgAAADhJREFUeAFjGMJgFAgSBMQrUlLCh4ewIqqGkzEYCAq6GCMAqtiwVzSqaFTRqCK6l76jpe/QBaMAAFoG7Glx5CmLAAAAAElFTkSuQmCC",
    finalize=True,
)

connected = False

while True:
    if connected == False:
        window["motorLeft"].update(disabled=True)
        window["motorStop"].update(disabled=True)
        window["motorRight"].update(disabled=True)

    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Close":
        motor.stop()
        break

    if event == "Start" and values["port"]:
        window["status"].update("Connected")
        print(values["port"])
        # motor.start(values["port"])
        motor.start(values["port"])
        connected = True
        window["motorLeft"].update(disabled=False)
        window["motorStop"].update(disabled=False)
        window["motorRight"].update(disabled=False)

    if event == "motorLeft":
        motor.queue.put((1, 500))
    if event == "motorStop":
        motor.queue.put((0, 0))
        print("Motor Stop")
    if event == "motorRight":
        motor.queue.put((-1, 400))

window.close()

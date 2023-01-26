import PySimpleGUI as sg
import sys

ICON = b"iVBORw0KGgoAAAANSUhEUgAAAEgAAABIBAMAAACnw650AAAAD1BMVEVHcEwjHyD1+Pq73fWIyfl/HgzbAAAAAXRSTlMAQObYZgAAADhJREFUeAFjGMJgFAgSBMQrUlLCh4ewIqqGkzEYCAq6GCMAqtiwVzSqaFTRqCK6l76jpe/QBaMAAFoG7Glx5CmLAAAAAElFTkSuQmCC"


def createErrorAndClose(message, title=None, func=None, layout=None):
    """Create a window to display error messages."""

    window = sg.Window(
        f"Error: {title}" if title else "Error",
        [
            [sg.Text(message, font=("", 12))],
            layout if layout else [],
            [sg.VPush()],
            [sg.Push(), sg.Button("Quit Program")],
        ],
        finalize=True,
        icon=ICON,
        keep_on_top=True,
    )
    window.set_min_size((300, 100))
    window.read()

    # Used for graceful exit
    if func:
        func()

    window.close()
    sys.exit(1)


def createError(
    message,
    title=None,
    func=None,
    layout=None,
):
    """Create a window to display error messages."""

    window = sg.Window(
        f"Error: {title}" if title else "Error",
        [
            [sg.Text(message, font=("", 12))],
            layout if layout else [],
            [sg.VPush()],
            [
                sg.Push(),
                sg.Button("Ok", size=(5, 1)),
                sg.Button("Quit Program", key="quit"),
            ],
        ],
        finalize=True,
        icon=ICON,
        keep_on_top=True,
    )
    window.set_min_size((300, 100))
    event, values = window.read()

    if event == "quit":
        # Used for graceful exit
        if func:
            func()
        window.close()
        sys.exit(1)

    window.close()
    return values

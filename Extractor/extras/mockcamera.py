import os, pty
import threading

import numpy as np
import cv2
import sys
import struct

structFormat = "bh"

WIDTH = 960
HEIGHT = 640
PADDING_X = 50
PADDING_Y = 50

SPACING = 10


frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (66, 167, 245), -1)

cv2.rectangle(
    frame,
    (PADDING_X, PADDING_Y),
    (WIDTH - PADDING_X, HEIGHT - PADDING_Y),
    (66, 111, 245),
    -1,
)

SPROCKET_HEIGHT = 40
SPROCKET_WIDTH = 30
SPROCKET_INSET = 10
SPROCKET_SPACING = 100
SPROCKET_NUM = 8

for i in range(0, 10):
    cv2.rectangle(
        frame,
        (10 + i * SPROCKET_SPACING, SPROCKET_INSET),
        (
            10 + i * SPROCKET_SPACING + SPROCKET_WIDTH,
            SPROCKET_HEIGHT,
        ),
        (255, 255, 255),
        -1,
    )

    cv2.rectangle(
        frame,
        (10 + i * SPROCKET_SPACING, HEIGHT - SPROCKET_INSET),
        (
            10 + i * SPROCKET_SPACING + SPROCKET_WIDTH,
            HEIGHT - SPROCKET_HEIGHT,
        ),
        (255, 255, 255),
        -1,
    )


direction = (1, 0)


def listener(port):
    global direction
    # continuously listen to commands on the master device
    while True:

        res = b""
        while not sys.getsizeof(res) == 37:
            res += os.read(port, 1)

        direction = struct.unpack(structFormat, res)


def test_serial():
    master, slave = pty.openpty()  # open the pseudoterminal
    # sys.stdout.write(f"{s_name}\n")

    thread = threading.Thread(target=listener, args=[master])
    thread.start()

    global frame

    while True:
        frame = np.roll(frame, -direction[0], axis=1)
        sys.stdout.buffer.write(frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    test_serial()

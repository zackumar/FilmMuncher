import logging
from threading import Thread

import serial
import struct
import time
from queue import Queue


class MotorController:

    def __init__(self):

        self.pico = None

        self.prevData = None
        self.structFormat = "bh"

        self.queue = Queue()
        self.running = True

    def start(self):
        t = Thread(target=self.get, args=())
        t.start()
        return self

    def get(self):
        self.pico = serial.Serial(
            port='/dev/tty.usbmodem1201',
            timeout=0.1,
            baudrate=115200,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
        )
        logging.debug("Motor controller started")

        speed = 0
        direction = 0

        while (self.running):
            (direction, speed) = self.queue.get()
            self.pico.write(struct.pack(
                self.structFormat, direction, speed))

    def stop(self):
        self.running = False
        self.pico.write(struct.pack(
            self.structFormat, 0, 0))
        self.pico.close()

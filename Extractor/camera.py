import subprocess
import signal
import logging

DEFAULT_WIDTH = 960
DEFAULT_HEIGHT = 640


class Camera:
    """Camera class to handle gphoto2 and ffmpeg processes

    :param scalingFactor: Scaling factor for the video stream
    :type scalingFactor: float
    :param mock: Whether to use a mock camera, defaults to False
    :type mock: bool, optional
    """

    def __init__(self, scalingFactor=1, mock=False):

        self.mock = mock

        self.width = int(DEFAULT_WIDTH * scalingFactor)
        self.height = int(DEFAULT_HEIGHT * scalingFactor)

        self.dummyGphotoCommand = [
            "ffmpeg",
            "-f",
            "rawvideo",
            "-pixel_format",
            "bgr24",
            "-video_size",
            "960x640",
            "-framerate",
            "30",
            "-i",
            "-",
            "-vf",
            "format=yuv420p",
            "-f",
            "mjpeg",
            "pipe:1",
        ]

        self.gphotoCommand = [
            "gphoto2",
            "--capture-movie",
            "--stdout",
            "--set-config",
            "Camera Output=PC",
            "--set-config",
            "Live View Size=Large",
        ]

        self.ffmpegCommand = [
            "ffmpeg",
            "-i",
            "pipe:0",
            "-q:v",
            "2",
            "-vf",
            f"scale={self.width}:{self.height}",
            "-fflags",
            "nobuffer",
            "-tune",
            "zerolatency",
            "-f",
            "mjpeg",
            "udp://127.0.0.1:8080/feed.mjpg",
        ]

        self.dummyProcess = None
        self.gptotoProcess = None
        self.ffmpegProcess = None

        self.running = False

    def startVideo(self):
        logging.info("Starting ffmpeg...")

        if self.mock:
            self.dummyProcess = subprocess.Popen(
                [
                    "python",
                    "./extras/mockcamera.py",
                ],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

        self.gphotoProcess = subprocess.Popen(
            self.gphotoCommand if not self.mock else self.dummyGphotoCommand,
            universal_newlines=True,
            stdin=None if not self.mock else self.dummyProcess.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        self.ffmpegProcess = subprocess.Popen(
            self.ffmpegCommand,
            universal_newlines=True,
            stdin=self.gphotoProcess.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        for stdoutLine in self.ffmpegProcess.stdout:
            line = stdoutLine.strip()
            logging.debug(line)

            if line.startswith("frame="):
                logging.info("FFmpeg started.")
                return True
            elif "Invalid data found when processing input" in line:
                logging.error("Invalid data found in pipe: Check gphoto2")
                return False

    def stopVideo(self):
        logging.info("Killing video processes")

        if self.ffmpegProcess:
            logging.debug("Killing ffmpeg")
            self.ffmpegProcess.send_signal(signal.SIGINT)
            self.ffmpegProcess.wait()
            logging.debug("Killed ffmpeg")

        if self.gphotoProcess:
            logging.debug("Killing gphoto")
            self.gphotoProcess.kill()
            self.gphotoProcess.wait()
            logging.debug("Killed gphoto")

        if self.dummyProcess:
            logging.debug("Killing dummy")
            self.dummyProcess.kill()
            self.dummyProcess.wait()
            logging.debug("Killed dummy")

        logging.info("Killed video processes")

    def takePicture(self):
        self.stopVideo()
        logging.debug("Taking picture")
        subprocess.run(
            [
                "gphoto2",
                "--capture-image-and-download",
                "--filename=%H-%M-%S.%C",
                "--set-config",
                "Continuous AF=1",
            ]
        )
        logging.debug("Picture taken")
        self.startVideo()

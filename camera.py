import subprocess
import signal
import logging

#  gphoto2 --capture-movie --stdout --set-config "Camera Output"=PC --set-config "Live View Size"=Large | ffmpeg -i pipe:0 -q:v 2 -listen 1 -fflags nobuffer -f mjpeg udp://localhost:8080/feed.mjpg

# gphoto = ['gphoto2', '--capture-movie', '--stdout', '--set-config',
#           '"Camera Output"=PC', '--set-config', '"Live View Size"=Large']

DEFAULT_WIDTH = 960
DEFAULT_HEIGHT = 640


class Camera:
    def __init__(self, scalingFactor=1):

        self.width = int(DEFAULT_WIDTH * scalingFactor)
        self.height = int(DEFAULT_HEIGHT * scalingFactor)
        print(self.width, self.height)

        # self.gphotoCommand = ['ffmpeg', '-f', 'lavfi', '-i', 'testsrc=size=960x640:rate=30',
        #                       '-f', 'mjpeg', 'pipe:1']
        self.gphotoCommand = ['gphoto2', '--capture-movie', '--stdout', '--set-config',
                              'Camera Output=PC', '--set-config', 'Live View Size=Large']
        self.ffmpegCommand = ['ffmpeg', '-i', 'pipe:0', '-q:v', '2', '-vf', f'scale={self.width}:{self.height}',
                              '-fflags', 'nobuffer', '-f', 'mjpeg', 'udp://127.0.0.1:8080/feed.mjpg']

        self.gptotoProcess = None
        self.ffmpegProcess = None

        self.running = False

    def startVideo(self):
        logging.debug("Starting ffmpeg...")

        self.gphotoProcess = subprocess.Popen(
            self.gphotoCommand, universal_newlines=True, stdout=subprocess.PIPE, stderr=None)

        self.ffmpegProcess = subprocess.Popen(
            self.ffmpegCommand, universal_newlines=True, stdin=self.gphotoProcess.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for stdoutLine in self.ffmpegProcess.stdout:
            line = stdoutLine.strip()
            print(line)

            if (line.startswith("frame=")):
                self.running = True
                break

        logging.debug("FFmpeg started.")

    def stopVideo(self):
        logging.debug('Killing processes')
        if self.ffmpegProcess:
            logging.debug('Killing ffmpeg')
            self.ffmpegProcess.send_signal(signal.SIGINT)
            self.ffmpegProcess.wait()
            logging.debug('Killed ffmpeg')

        if self.gphotoProcess:
            logging.debug('Killing gphoto')
            # self.gphotoProcess.send_signal(signal.SIGINT)
            self.gphotoProcess.kill()
            self.gphotoProcess.wait()
            logging.debug('Killed gphoto')

    def takePicture(self):
        self.stopVideo()
        logging.debug('Taking picture')
        subprocess.run(
            ['gphoto2', '--capture-image-and-download', '--filename=%H-%M-%S %f.%C', '--set-config', 'Continuous AF=1'])
        logging.debug('Picture taken')
        self.startVideo()

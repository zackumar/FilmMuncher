import subprocess
import signal
import logging

#  gphoto2 --capture-movie --stdout --set-config "Camera Output"=PC --set-config "Live View Size"=Large | ffmpeg -i pipe:0 -q:v 2 -listen 1 -fflags nobuffer -f mjpeg udp://localhost:8080/feed.mjpg


# gphoto = ['gphoto2', '--capture-movie', '--stdout', '--set-config',
#           '"Camera Output"=PC', '--set-config', '"Live View Size"=Large']

gphoto = ['ffmpeg', '-f', 'lavfi', '-i', 'testsrc=size=960x640:rate=30',
          '-f', 'mjpeg', 'pipe:1']

ffmpeg = ['ffmpeg', '-i', 'pipe:0', '-q:v', '2', '-listen', '1',
          '-fflags', 'nobuffer', '-f', 'mjpeg', 'udp://localhost:8080/feed.mjpg']


class FFmpeg:
    def __init__(self):
        self.gptotoProcess = None
        self.ffmpegProcess = None
        self.running = False

    def start(self):
        self.gphotoProcess = subprocess.Popen(
            gphoto, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        self.ffmpegProcess = subprocess.Popen(
            ffmpeg, universal_newlines=True, stdin=self.gphotoProcess.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for stdoutLine in self.ffmpegProcess.stdout:
            line = stdoutLine.strip()

            if (line.startswith("frame=")):
                self.running = True
                logging.debug("Frame")
                break

    def stop(self):
        logging.debug('Killing processes')
        if self.ffmpegProcess:
            logging.debug('Killing ffmpeg')
            self.ffmpegProcess.send_signal(signal.SIGINT)
            self.ffmpegProcess.wait()
            logging.debug('Killed ffmpeg')

        if self.gphotoProcess:
            logging.debug('Killing gphoto')
            self.gphotoProcess.send_signal(signal.SIGINT)
            self.gphotoProcess.wait()
            logging.debug('Killed gphoto')

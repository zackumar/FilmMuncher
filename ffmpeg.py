import subprocess
import signal

#  gphoto2 --capture-movie --stdout --set-config "Camera Output"=PC --set-config "Live View Size"=Large | ffmpeg -i pipe:0 -q:v 2 -listen 1 -fflags nobuffer -f mjpeg udp://localhost:8080/feed.mjpg

gphotoProcess = None
ffmpegProcess = None


def kill():
    print('Killing processes')
    if ffmpegProcess:
        print('Killing ffmpeg')

        ffmpegProcess.send_signal(signal.SIGINT)
        ffmpegProcess.wait()
        print('Killed ffmpeg')

    if gphotoProcess:
        print('Killing gphoto')
        gphotoProcess.send_signal(signal.SIGINT)
        gphotoProcess.wait()
        print('killed gphoto')
    exit(0)


def run():
    gphoto = ['gphoto2', '--capture-movie', '--stdout', '--set-config',
              '"Camera Output"=PC', '--set-config', '"Live View Size"=Large']
    ffmpeg = ['ffmpeg', '-i', 'pipe:0', '-q:v', '2', '-listen', '1',
              '-fflags', 'nobuffer', '-f', 'mjpeg', 'udp://localhost:8080/feed.mjpg']

    gphotoProcess = subprocess.Popen(
        gphoto, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    ffmpegProcess = subprocess.Popen(
        ffmpeg, universal_newlines=True, stdin=gphotoProcess.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for stdout_line in ffmpegProcess.stdout:
        line = stdout_line.strip()
        print(line)
        if (line.startswith("frame=")):
            print('FRAME')


run()

# Film Muncher

<img src="https://raw.githubusercontent.com/zackumar/FilmMuncher/main/Extractor/images/logo.png" align="right"
     alt="Film Muncher by Zack Umar" width="144" height="144">

An automatic (35mm and possibly 120mm/APS) film holder + software for DSLR scanning for MacOS/Linux

## Features

- Use with 35mm film
- Frame Edge Detection
- Automatic picture taking and preview

## Installation

### Install using source

1. You need the following installed:

- [Python3](https://www.python.org/downloads/)
- [gphoto2](http://www.gphoto.org/) - Used to control and stream camera
- [FFmpeg](https://ffmpeg.org/) - Used to process camera stream

2. Next you can clone and setup the repo:

```bash
  # Clone this repo
  git clone https://github.com/zackumar/FilmMuncher.git
  cd FilmMuncher
```

There are two directories inside: Extractor and ExtractorPico.

4. Extractor (The Software):

```bash
  # Setup the Extractor
  cd Extractor

  # Create a virtual environment and install deps
  python3 -m venv ./.venv
  pip install -r requirements.txt

  # Run the extractor! (But set up the pico first)
  python ./filmscanner.py
```

3. ExtractorPico (The Hardware):

   i. I currently use PlatformIO + VSCode for the motor controller, but I plan to give just a straight .ino file soon. Flash the Arduino code onto your Arduino compatible devie (in my case a Raspberry Pi Pico).

   ii. I'm using a [28BYJ-48 Stepper Motor with ULN2003 Driver](https://www.amazon.com/ELEGOO-28BYJ-48-ULN2003-Stepper-Arduino/dp/B01CP18J4A). But most motors should work but you may need to update the hardware to support them.

   iii. Connect the motor to pins 8, 9, 10, and 11 on the Arduino compatible device (in this case a Raspberry Pi Pico) and connect it you your computer when running Film Muncher.

Enjoy!

## Roadmap

- Add fast fixed position mode

## Limitations

There are a currently a few known limitaions.

- Currently being developed on MacOS. I'm not sure how well this works on Linux at the moment. If you'd like to test that out, please give it a try.

- gphoto2
  - gphoto2 is only being developed for Unix based systems (though some are trying to port it to Windows). This means that Film Muncher will only work on MacOS/Linux/Unix
  - Not every camera is currently supported by gphoto2

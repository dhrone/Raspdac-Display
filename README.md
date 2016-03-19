# Raspdac-Display
An alternate display program for the Raspdac from Audiophonics which uses a Winstar OLED 16x2 display

The RaspDac is a Raspberry Pi audio player using a Sabre ES9023 DAC and running the excellent music distro from Volumio.  It uses a Winstar OLED WEH001602A as a display.   This python-based project is an alternate display program from what is provided by Audiophonics.

## Installation

These instructions assume a working version of the Volumio distribution (V1.55) and that the Winstar OLED display has been wired to the Raspberry Pi 2 according to the instructions provided by Audiophonics at http://forum.audiophonics.fr/viewtopic.php?f=4&t=1492.  If you have wired the display to different pins, please make sure to adjust the GPIO pin assignments accordingly.

Place RaspDacDisplay.py and WinstarOled.py in a directory of your choice (e.g. /home/pi).  Add RaspDacDisplay.py to /etc/rc.local to automate its startup on reboot.  It is a good idea to delay its start-up to allow the system to come up completely before it attempts to start.  The following examples uses a 20 second delay.

```
/etc/rc.local
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.
/var/www/command/player_wdog.sh startup & > /dev/null 2>&1

(sleep 20; python /home/pi/RaspDacDisplay.py) &
exit 0
```

* Additional instructions:
  * RaspDacDisplay.py currently is hardcoded to place it's log file in /var/log/RaspDacDisplay.log.
  * There are several adjusted variables at the beginning of RaspDacDisplay.py that you can modify for different behavior.  These are...
    * ARTIST_TIME - Sets the amount of time in seconds the artist's name will display before switching to the title
    * TITLE_TIME - Sets the amount of time in seconds the title will display before switching to the artist's name
    * HESITATION_TIME - Titles or artists which are wider than the display width get scrolled.  This variable sets how long the display should pause in seconds before the scrolling begins
    * TIMEZONE - Sets what timezone should be used when displaying the current system time.  Possible values can be found in the /usr/share/zoneinfo directory. Examples...
     ```
     New York City.  TIMEZONE="US/Eastern"
     San Francisco.  TIMEZONE="US/Pacific"
     Paris.  TIMEZONE = "Europe/Paris"
     ```
    
  * The program relies upon two python packages that are not installed by default on the Volumio 1.55 distribution.  These are moment and python-mpd2.  They are most easily installed using the Python Package Manager (PIP). If you do not have pip installed you can add it using the following command.
   ```
   apt-get install python-setuptools && easy_install pip
   ```
  * With PIP installed you can install moment and python-mpd with the following commands.
   ```
   pip install moment
   pip install python-mpd2
   ```
  
   
    
## Usage

./python RaspDacDisplay.py & 

Starts the RaspDacDisplay as a background process

## History

This is version 0.1 and should be considered ALPHA code.  It (hopefully) solves many of the initialization challenges associated with the Winstar OLED display and implements some nice display scrolling logic based upon the content of the artist and title data supplied by MPD and/or Spotify.

## Credits

The basis for most of this code comes from Lardconcepts (https://gist.github.com/lardconcepts/4947360)
A great overview of LCD/OLED logic is available on Wikipedia (https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller).  While that document is focused on the popular HD44870 LCDs, most of what is describe there applies to the Winstar OLED.  There are important differences though.  The OLED appears to be much more sensitive to timing issues and requires a different command sequence to reset it back to a known good state upon a warmstart.
Understanding the initialization behavior of the Winstar in 4 bit mode was greatly assisted by PicAxe who currently have a PDF posted which detailed a method to resync with the display.  This is described on the last page of  http://www.picaxe.com/docs/oled.pdf.

## License

The MIT License (MIT)

Copyright (c) [2015] [Dhrone]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

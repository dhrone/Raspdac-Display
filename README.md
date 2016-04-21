# Raspdac-Display
An alternate display program for the Raspdac from Audiophonics which uses a Winstar OLED 16x2 display

The RaspDac is a Raspberry Pi audio player using a Sabre ES9023 DAC and running the excellent music distro from Volumio.  It uses a Winstar OLED WEH001602A as a display.   This python-based project is an alternate display program from what is provided by Audiophonics.

## Installation

### For Volumio

   These instructions assume a working version of the Volumio distribution (V1.55) and that the Winstar OLED display has been wired to the Raspberry Pi 2 according to the instructions provided by Audiophonics at http://forum.audiophonics.fr/viewtopic.php?f=4&t=1492.  If you have wired the display to different pins, please make sure to adjust the GPIO pin assignments accordingly. Note: pin assignments for the V2 and V3 versions of the RaspDac are already encoded at the top of the Winstar_GraphicOLED.py file.
   
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
     
      
       
    ### Usage
   
   ./python RaspDacDisplay.py & 
   
   Starts the RaspDacDisplay as a background process

### For Runeaudio
These instructions assume you are using a newly created image of the Runeaudio distribution (V0.3-BETA) and that the Winstar OLED display has been wired to the Raspberry Pi 2 or Pi3 according to the instructions provided by Audiophonics at http://forum.audiophonics.fr/viewtopic.php?f=4&t=1492.  If you have wired the display to different pins, please make sure to adjust the GPIO pin assignments accordingly.  Note: pin assignments for the V2 and V3 versions of the RaspDac are already encoded at the top of the Winstar_GraphicOLED.py file.

There are several changes that need to be made to the Runeaudio distribution to get the RaspDac fully setup.  These directions will provide a step-by-step walkthrough of those changes.  Please note, they have only be tested on a Raspberry Pi 3 using the V0.3-BETA image with MD5 hash a072179a40613a5cbb277cc33d1ace9c.  There are some idiosyncrasies with this image that need to be addressed which may not be required in future versions.

* Step one.  Download and install the image on your SD card
Follow the instructions found at http://www.runeaudio.com/documentation/

The following steps require that your Raspdac be powered up, connected to the network and that you be logged into it as the root user.  Runeaudio allows login using the ssh protocol.  The username is root and the password is rune.  

* Step two.  Enable the ES9023 DAC
Edit /boot/config.txt and uncomment the line related to the hifiberry-dac.  You can use the editor of your choice here.  nano works fine, as does vi.
  ```
  nano /boot/config.txt
  ```
  
  Move the cursor down to the line that has #dtoverlay=hifiberry-dac, remove the # to uncomment that line, save the file and exit.
  
  ```
  # Uncomment one of these lines to enable an audio interface
  dtoverlay=hifiberry-dac
  #dtoverlay=hifiberry-dacplus
  #dtoverlay=hifiberry-digi
  #dtoverlay=hifiberry-amp
  #dtoverlay=iqaudio-dac
  #dtoverlay=iqaudio-dacplus
  ```

* Step three (optional).  Expand the disk to allow all of your SD card's space to be leveraged
Follow the instructions found at http://www.runeaudio.com/documentation/troubleshooting/extend-partition-sd/

   You will likely need to reboot in between making the changes to the partition with fdisk and issuing the resize2fs command

* Step four.  Update to the latest version of the Runeaudio UI
   ```
   cd /var/www
   git pull
   ```

* Step five.  Add the necessary packages to support the RaspDac_Display program
   * A.  Update the pacman package database.  This is needed to make sure that the correct version of files will be selected on any package update.
     ```
     pacman -Syu
     ```
     This will synchronize the package databases.
     ```
     :: Synchronizing package databases...
      core                                               209.7 KiB  1049K/s 00:00 [###########################################] 100%
      extra                                                2.3 MiB  1168K/s 00:02 [###########################################] 100%
      community                                            3.7 MiB  8.37M/s 00:00 [###########################################] 100%
      alarm is up to date
      aur is up to date
     :: Starting full system upgrade...
     resolving dependencies...
     looking for conflicting packages...
     
     Packages (80) adwaita-icon-theme-3.20-1  alsa-lib-1.1.1-1  alsa-utils-1.1.1-1  at-spi2-atk-2.20.1-1  at-spi2-core-2.20.1-1
                   atk-2.20.0-1  bluez-5.39-1  bluez-utils-5.39-1  boost-libs-1.60.0-4  ca-certificates-mozilla-3.23-3
                   cmake-3.5.1-1  colord-1.3.2-1  curl-7.48.0-1  dconf-0.26.0-1  device-mapper-2.02.149-1  dhcpcd-6.10.2-1
                   elfutils-0.166-1  expat-2.1.1-1  fontconfig-2.11.95-1  gcr-3.20.0-1  gdk-pixbuf2-2.34.0-1  git-2.8.0-1
                   glib-networking-2.48.0-1  glib2-2.48.0-1  gnutls-3.4.11-1  graphite-1:1.3.8-1  groff-1.22.3-6
                   gsettings-desktop-schemas-3.20.0-1  gst-plugins-base-libs-1.8.0-1  gstreamer-1.8.0-1
                   gtk-update-icon-cache-3.20.3-1  gtk3-3.20.3-1  harfbuzz-1.2.6-1  harfbuzz-icu-1.2.6-1  icu-57.1-1
                   inputproto-2.3.2-1  iproute2-4.4.0-1  iw-4.3-1  json-glib-1.2.0-1  jsoncpp-1.7.2-1  libdrm-2.4.67-2
                   libelf-0.166-1  libgusb-0.2.9-1  libmm-glib-1.4.14-1  libnl-3.2.27-1  libnm-glib-1.0.12-1  libpng-1.6.21-1.1
                   librsvg-2:2.40.15-1  libsecret-0.18.5-1  libsoup-2.54.0.1-1  libtasn1-4.8-1  libva-1.7.0-1  libwbclient-4.4.2-1
                   libxkbcommon-0.6.1-1  libxml2-2.9.3+14+gd5bd2a9-1  linux-raspberrypi-4.4.7-2  mesa-11.2.0-1.2
                   mesa-libgl-11.2.0-1.2  nss-3.23-3  ntfs-3g-2016.2.22-1  pacman-mirrorlist-20160319-1  pango-1.40.1-1
                   python2-2.7.11-3  raspberrypi-firmware-20160412-1  raspberrypi-firmware-bootloader-20160412-1
                   raspberrypi-firmware-bootloader-x-20160412-1  raspberrypi-firmware-examples-20160412-1
                   raspberrypi-firmware-tools-20160412-1  s-nail-14.8.8-1  shared-mime-info-1.6-1  smbclient-4.4.2-1
                   sqlite-3.12.1-1  sudo-1.8.16-1  tzdata-2016c-1  vala-0.32.0-1  wayland-protocols-1.3-1  webkitgtk-2.4.11-1
                   xorg-server-1.18.3-1  xorg-server-common-1.18.3-1  xorg-xinit-1.3.4-4
     
     Total Download Size:   151.36 MiB
     Total Installed Size:  571.61 MiB
     Net Upgrade Size:        3.50 MiB
     
     :: Proceed with installation? [Y/n] 
     ```
     I recommend that you NOT proceed with the installation as in my system, it seemed to destablize the system.  YMMV.

   * B.  Add WiringPi package.  This is needed to support the power management feature of the V3 DAC.  You can skip this for the RaspDac V2.
     ```
     pacman -Sy wiringpi
     ```
   * C. Retrive the python package manager for python2.
  ```
  pacman -Sy python2-pip
  ```
   * D. Add the moment and python-mpd2 packages.
  ```
  pip2 install moment
  pip2 install python-mpd2
  ```
  
    If you receive an error message when running the pip2 commands, you may need to repair the distutils installation.  This can be done by explicitly installing ez_setup.py.
  ```
  wget https://bootstrap.pypa.io/ez_setup.py -O - | python2
  ```
  
* Step six.  Retrieve the current version of the RaspDac_Display software from github
```
mkdir /home/raspdac
cd /home/raspdac
wget https://github.com/dhrone/Raspdac-Display/archive/master.tar.gz
tar xvf master.tar.gz
cd /home/raspdac/Raspdac-Display-master/
```
* Step seven.  Place files in their appropriate directories and register the service with systemctl to enable autostart.  All of these commands should be issued from within the Raspdac_Display directory that you retrieved from github.
   * A.  Files for the display
     ```
     cp oled.service /usr/lib/systemd/system/
     cp RaspDacDisplay.py /usr/local/bin/
     cp Winstar_GraphicOLD.py /usr/local/bin/
     systemctl enable oled.service
     ```
     Note: you will be overwriting the official version of the rune_shutdown command.  If you attempt to pull the latest RuneAudio UI from github, it will fail unless you stash the change first.
     
   * B.  Files for the power management function (RaspDac version V3 only)
     ```
     cp sds.service /usr/lib/systemd/system/
     cp sds.sh /usr/local/bin/
     cp rune_shutdown /var/www/command/
     chmod +x /usr/local/bin/sds.sh
     chmod +x /var/www/command/rune_shutdown  
     systemctl enable sds.service
     ```

 * Step eight.  Reboot (and enjoy) !!!
   ```
   reboot
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




## History

This is version 0.5 and should be considered BETA code.  It (hopefully) solves many of the initialization challenges associated with the Winstar OLED display and implements some nice display scrolling logic based upon the content of the artist and title data supplied by MPD and/or Spotify.

## Credits

The basis for most of this code comes from Lardconcepts (https://gist.github.com/lardconcepts/4947360)
A great overview of LCD/OLED logic is available on Wikipedia (https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller).  While that document is focused on the popular HD44870 LCDs, most of what is describe there applies to the Winstar OLED.  There are important differences though.  The OLED appears to be much more sensitive to timing issues and requires a different command sequence to reset it back to a known good state upon a warmstart.
Understanding the initialization behavior of the Winstar in 4 bit mode was greatly assisted by PicAxe who currently have a PDF posted which detailed a method to resync with the display.  This is described on the last page of  http://www.picaxe.com/docs/oled.pdf.
Most of the power management logic was pulled from discussions on the Runeaudio (http://www.runeaudio.com/forum/audiophonics-i-sabre-v3-dac-es9023-tcxo-t3377.html) and Audiophonics (http://forum.audiophonics.fr/viewtopic.php?f=4&t=1620) forums.  

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

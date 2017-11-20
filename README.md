# NO LONGER MAINTAINED
This project is no longer being maintained.  I will still try to respond to issue requests but will not commit signficant development effort to resolving them.  There is a new version of the project at http://github.com/dhrone/pydPiper that you may want to consider.  Unlike Raspdac-Display which is text-based, pydPiper is a graphical system and is able to handle a wider variety of display designs.

# Raspdac-Display
An alternate display program for the Raspdac from Audiophonics which uses a Winstar OLED 16x2 display

The RaspDac is a Raspberry Pi audio player using a Sabre ES9023 DAC and capable of running several excellent music distros such as Volumio, RuneAudio, and Max2Play.  It uses a Winstar OLED WEH001602A as a display.   This python-based project is an alternate display program from what is provided by Audiophonics.

## Installation

### For Volumio

   These instructions assume a working version of the Volumio distribution (V1.55) and that the Winstar OLED display has been wired to the Raspberry Pi according to the instructions provided by Audiophonics at http://forum.audiophonics.fr/viewtopic.php?f=4&t=1492.  If you have wired the display to different pins, please make sure to adjust the GPIO pin assignments accordingly. Note: pin assignments for the V2 and V3 versions of the RaspDac are already encoded at the top of the Winstar_GraphicOLED.py file.

  Retrieve the current version of the RaspDac_Display software from github

   ```
   git clone https://github.com/dhrone/Raspdac-Display
   cd Raspdac-Display
   ```

   Place RaspDacDisplay.py and WinstarOled.py in a directory of your choice (e.g. /usr/local/bin/.  Add RaspDacDisplay.py to /etc/rc.local to automate its startup on reboot.  It is a good idea to delay its start-up to allow the system to come up completely before it attempts to start.  The following examples uses a 20 second delay.

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

   (sleep 20; python /usr/local/bin/RaspDacDisplay.py) &
   exit 0
   ```

   * Additional instructions:
     * RaspDacDisplay.py uses the variable LOGFILE to determine where to place it's log file.  The default is /var/log/RaspDacDisplay.log.
     * There are several adjusted variables at the beginning of RaspDacDisplay.py that you can modify for different behavior.  These are...
       * HESITATION_TIME - Titles or artists which are wider than the display width get scrolled.  This variable sets how long the display should pause in seconds before the scrolling begins
       * ANIMATION_SMOOTHING - Sets the speed the upper speed for display update.  Values between .1 and .25 seem to work well.
       * TIMEZONE - Sets what timezone should be used when displaying the current system time.  Possible values can be found in the /usr/share/zoneinfo directory. Examples...
        ```
        New York City.  TIMEZONE="US/Eastern"
        San Francisco.  TIMEZONE="US/Pacific"
        Paris.  TIMEZONE = "Europe/Paris"
        ```
      * PAGES System:
        * There is now a more flexible system in place to configure what gets displayed on the screen.  It uses a metaphor of a collection of pages that are displayed for each of the major modes of the system (stop, play, alert).  A more complete description of how to modify and create pages is included in the "Page Format.txt" file.  
        * Note that ARTIST_TIME, and TITLE_TIME have been removed.  This functionality is now captured in the PAGES system


     * The program relies upon three python packages that are not installed by default on the Volumio 1.55 distribution.  These are moment, pylms and python-mpd2.  They are most easily installed using the Python Package Manager (PIP). If you do not have pip installed you can add it using the following command.
      ```
      apt-get install python-setuptools && easy_install pip
      ```
     * With PIP installed you can install moment and python-mpd with the following commands.
      ```
      pip install moment
      pip install pylms
      pip install python-mpd2
      ```

    ### Usage

   ./python RaspDacDisplay.py &

   Starts the RaspDacDisplay as a background process

### For Runeaudio
These instructions assume you are using a newly created image of the Runeaudio distribution (V0.3-BETA) and that the Winstar OLED display has been wired to the Raspberry Pi 2 or Pi 3 according to the instructions provided by Audiophonics at http://forum.audiophonics.fr/viewtopic.php?f=4&t=1492.  If you have wired the display to different pins, please make sure to adjust the GPIO pin assignments accordingly.  Note: pin assignments for the V2 and V3 versions of the RaspDac are already encoded at the top of the Winstar_GraphicOLED.py file.

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
   * A.  Update the pacman package database but do NOT update the system from that database.  Updating the database is needed to make sure that the correct version of files will be selected when you install some of the additional packages needed to make the display work but updating all of the currently installed packages is unnecessary, takes a long time, and can destablize the system.
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
     Reminder: Do NOT proceed with the installation as it appears to destablize the system!!!

   * B.  Add WiringPi package.  This is needed to support the power management feature of the V3 DAC.  You can skip this for the RaspDac V2.
     ```
     pacman -Sy wiringpi
     ```
   * C. Retrive the python package manager for python2.
  ```
  pacman -Sy python2-pip
  ```
   * D. Add the moment, pylms, python-mpd2 and redis packages.
  ```
  pip2 install moment
  pip2 install pylms
  pip2 install python-mpd2
  pip2 install redis
  ```

    If you receive an error message when running the pip2 commands, you may need to repair the distutils installation.  This can be done by explicitly installing ez_setup.py.
  ```
  wget https://bootstrap.pypa.io/ez_setup.py -O - | python2
  ```

* Step six.  Retrieve the current version of the RaspDac_Display software from github

```
git clone https://github.com/dhrone/Raspdac-Display
cd Raspdac-Display
```

* Step seven.  Place files in their appropriate directories and register the service with systemctl to enable autostart.  All of these commands should be issued from within the Raspdac_Display directory that you retrieved from github.
   * A.  Files for the display
     ```
     cp oled.service /usr/lib/systemd/system/
     cp RaspDacDisplay.py /usr/local/bin/
     cp Winstar_GraphicOLED.py /usr/local/bin/
     cp pages.py /usr/local/bin
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
   * RaspDacDisplay.py uses the variable LOGFILE to determine where to place it's log file.  The default is /var/log/RaspDacDisplay.log.
   * There are several variables you can adjust at the beginning of RaspDacDisplay.py to modify the software for different behavior.  These are...
     * HESITATION_TIME - Titles or artists which are wider than the display width get scrolled.  This variable sets how long the display should pause in seconds before the scrolling begins
     * ANIMATION_SMOOTHING - Sets the speed the upper speed for display update.  Values between .1 and .25 seem to work well.
     * TIMEZONE - Sets what timezone should be used when displaying the current system time.  Possible values can be found in the /usr/share/zoneinfo directory. Examples...
      ```
      New York City.  TIMEZONE="US/Eastern"
      San Francisco.  TIMEZONE="US/Pacific"
      Paris.  TIMEZONE = "Europe/Paris"
      ```
    * PAGES System:
      * There is now a more flexible system in place to configure what gets displayed on the screen.  It uses a metaphor of a collection of pages that are displayed for each of the major modes of the system (stop, play, alert).  A more complete description of how to modify and create pages is included in the "Page Format.txt" file.  
      * Note that ARTIST_TIME, and TITLE_TIME have been removed.  This functionality is now captured in the PAGES system

### For Max2Play
These instructions assume you are using a newly created image of the Max2Play distribution (v2.36) and that the Winstar OLED display has been wired to the Raspberry Pi 2 or Pi 3 according to the instructions provided by Audiophonics at http://forum.audiophonics.fr/viewtopic.php?f=4&t=1492.  If you have wired the display to different pins, please make sure to adjust the GPIO pin assignments accordingly.  Note: pin assignments for the V2 and V3 versions of the RaspDac are already encoded at the top of the Winstar_GraphicOLED.py file.

Note: Max2Play supports multiple playback systems.  Currently RaspdacDisplay is only tested to work with the Logitech Media Server method using the SqueezeLite Audioplayer.


* Step one.  Download and install the Max2Play HiFiBerry Image (Raspberry Pi) image on your SD card.  
Follow the instructions found at https://www.max2play.com/en/getting-started/

The following steps require that your Raspdac be powered up and connected to your network

   * Using a browser, navigate to http://max2play.local.  This should bring up the Max2Play interface on the HiFiBerry tab.  
   * Choose Hifi Berry DAC (Pi A/B) as your installed HiFiBerry Card and click save.
   * Click on the Settings/Reboot tab to switch to that page.
   * Click on Expand Filesystem to enable the full use of the storage on your SD card.  (You may need to reboot at this point).
   * Click on Update Max2Play to bring the software up to the current version.
   * Click on the Squeezebox Server tab to change to that page.
   * Click on Show available Versions to populate the list of available Squeezebox Server versions.
   * Choose the Nightly 7.9 build.  Make sure that the text in the Alternate source field references the 7.9 version.  If not, reselect 7.9 in the dropdown.
   * Click on Squeezebox Server start installation button
   When the installation is complete, you can click on Open Squeezebox Server Wedadministration to load the Logitech Media Server (LMS) interface. From there you can set up your music sources and play music.  Instructions for setting up Spotify are available at https://www.max2play.com/en/how-tos/howto-spotify/.  It is also possible to use Pandora, Tidal and other 3rd party music providers though this will require you to set up an account on mysqueezebox.com, link your LMS to mysqueezebox.com (settings->mysqueezebox.com) and add the apps of your choice on that site.  Once you have done this, the new services will be available under "My Apps" in the LMS web interface.

* Step two.  Log into the max2play console using ssh.  You can use whatever ssh client you are comfortable with.  The username is pi and the password is raspberry.  Unless you've changed it the URL should be max2play.local.  Ex: "ssh pi@max2play.local".

* Step three.  Download the latest Raspdac-Display software.

   ```
   git clone https://github.com/dhrone/Raspdac-Display
   cd Raspdac-Display
   ```


* Step four.  Add the necessary packages to support the RaspDac-Display program

  ```
  sudo apt-get install python-setuptools
  sudo pip install moment
  sudo pip install pylms
  sudo pip install python-mpd2
  ```

* Step five.  Edit the RaspdacDisplay.py to localize it for your system. You can use whatever editor you are comfortable with (e.g. vi, nano)

Find and change the following values to ones appropriate for your system.
```
TIMEZONE
MPD_ENABLED (should be false if using LMS)
SPOP_ENABLED (should be false if using LMS)
LMS_ENABLED (should be True if using LMS)
LMS_PLAYER (set this to the MAC address for your Max2Play system if using SqueezeLite).
```

To find the MAC address for your system, use the following command...

```
ifconfig -a | grep HWaddr
```

If you are using a wired network, choose the HWaddr from the eth0 interface.
If you are using a wireless network, choose the HWaddr from the wlan0 interface.

* Step six.  Edit the Winstar_GraphicOLED.py file and change the pin settings for the version of the Raspdac that you have.

```
# Pin Mappings V2
#OLED_DB4=25
#OLED_DB5=24
#OLED_DB6=23
#OLED_DB7=15
#OLED_RS=7
#OLED_E=8

# Pin Mappings V3
OLED_DB4=25
OLED_DB5=24
OLED_DB6=23
OLED_DB7=27
OLED_RS=7
OLED_E=8
```

This is important to get right as if the pins are wrong, the display will not work correctly.  The screen will likely remain blank or show random characters if you do not have the pins set correctly for the version of the Raspdac DAC you are using.

* Step seven.  Place files in their appropriate directories and register the service with systemctl to enable autostart.  All of these commands should be issued from within the Raspdac_Display directory that you retrieved from github.

  * A. Files for the display
  ```
  sudo cp oled.service /etc/systemd/system/
  sudo cp RaspdacDisplay.py /usr/local/bin/
  sudo cp Winstar_GraphicOLED.py /usr/local/bin/
  sudo systemctl enable oled.service
  ```

  * B. Files for the power management function (RaspDac version V3 only)

  ```
  sudo cp sds.service /etc/systemd/system/
  sudo cp sdsmax.sh /usr/local/bin/
  chmod +x /usr/local/bin/sdsmax.sh
  systemctl enable sds.service
  ```


 * Step eight.  Reboot (and enjoy) !!!
   ```
   reboot
   ```

 * Additional instructions:
   * RaspDacDisplay.py uses the variable LOGFILE to determine where to place it's log file.  The default is /var/log/RaspDacDisplay.log.
   * There are several variables you can adjust at the beginning of RaspDacDisplay.py to modify the software for different behavior.  These are...
     * HESITATION_TIME - Titles or artists which are wider than the display width get scrolled.  This variable sets how long the display should pause in seconds before the scrolling begins
     * ANIMATION_SMOOTHING - Sets the speed the upper speed for display update.  Values between .1 and .25 seem to work well.
     * TIMEZONE - Sets what timezone should be used when displaying the current system time.  Possible values can be found in the /usr/share/zoneinfo directory. Examples...
      ```
      New York City.  TIMEZONE="US/Eastern"
      San Francisco.  TIMEZONE="US/Pacific"
      Paris.  TIMEZONE = "Europe/Paris"
      ```
    * PAGES System:
      * There is now a more flexible system in place to configure what gets displayed on the screen.  It uses a metaphor of a collection of pages that are displayed for each of the major modes of the system (stop, play, alert).  A more complete description of how to modify and create pages is included in the "Page Format.txt" file.  
      * Note that ARTIST_TIME, and TITLE_TIME have been removed.  This functionality is now captured in the PAGES system

## History

Version 0.7 (Beta).  This version is a major re-write of the display logic.  It uses a pages metaphor to allow the user to more rapidly change the content of the display.  It also re-integrates customized versions to support RuneAudio, Volumio, and Max2play into a single version.

Version 0.5 (Beta).  This version (hopefully) solves many of the initialization challenges associated with the Winstar OLED display and implements some nice display scrolling logic based upon the content of the artist and title data supplied by MPD and/or Spotify.

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

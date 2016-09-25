import Winstar_GraphicOLED
import moment
import time
import json
import logging
import commands
import os
from mpd import MPDClient
import pylms
from pylms import server
from pylms import player
import telnetlib
from socket import error as socket_error

try:
	import RPi.GPIO as GPIO
	DISPLAY_INSTALLED = True
except:
	import curses
	DISPLAY_INSTALLED = False

import Queue
from threading import Thread
import signal
import sys

STARTUP_MSG = "Raspdac\nStarting"

HESITATION_TIME = 2.5 # Amount of time in seconds to hesistate before scrolling
ANIMATION_SMOOTHING = .15 # Amount of time in seconds before repainting display

COOLING_PERIOD = 15 # Default amount of time in seconds before an alert message can be redisplayed

# The Winstar display shipped with the RaspDac is capable of two lines of display
# when the 5x8 font is used.  This code assumes that is what you will be using.
# The display logic would need significant rework to support a different number
# of display lines!

DISPLAY_WIDTH = 16 # the character width of the display
DISPLAY_HEIGHT = 2 # the number of lines on the display

# This is where the log file will be written
LOGFILE='/var/log/RaspDacDisplay.log'
#LOGFILE='./log/RaspDacDisplay.log'

# Adjust this setting to localize the time display to your region
TIMEZONE="US/Eastern"
TIME24HOUR=False
#TIMEZONE="Europe/Paris"

# Logging level
#LOGLEVEL=logging.DEBUG
LOGLEVEL=logging.INFO
#LOGLEVEL=logging.WARNING
#LOGLEVEL=logging.CRITICAL


#Configure which music services to monitor
# For Volumio and RuneAudio MPD and SPOP should be enabled and LMS disabled
# for Max2Play if you are using the Logitech Music Service, then LMS should be enabled
MPD_ENABLED = True
MPD_SERVER = "localhost"
MPD_PORT = 6600

SPOP_ENABLED = True
SPOP_SERVER = "localhost"
SPOP_PORT = 6602

LMS_ENABLED = False
LMS_SERVER = "localhost"
LMS_PORT = 9090
LMS_USER = ""
LMS_PASSWORD = ""

# Set this to MAC address of the Player you want to monitor.
# THis should be the MAC of the RaspDac system if using Max2Play with SqueezePlayer
# Note: if you have another Logitech Media Server running in your network, it is entirely
#       possible that your player has decided to join it, instead of the LMS on Max2Play
#       To fix this, go to the SqueezeServer interface and change move the player to the
#       correct server.
LMS_PLAYER = "00:01:02:aa:bb:cc"


# Page Definitions
# See Page Format.txt for instructions and examples on how to modify your display settings
PAGES_Play = {
  'name':"Play",
  'pages':
    [
      {
        'name':"Album",
        'duration':10,
		'hidewhenempty':True,
        'hidewhenemptyvars': [ "album" ],
        'lines': [
          {
            'name':"top",
            'variables': [ "album" ],
            'format':"Album: {0}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "position" ],
            'format':"{0}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Blank",
        'duration':0.5,
        'lines': [
          {
            'name':"top",
            'format':"",
          },
          {
            'name':"bottom",
            'variables': [ "position" ],
            'format':"{0}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Artist",
        'duration':10,
		'hidewhenempty':True,
        'hidewhenemptyvars': [ "artist" ],
        'lines': [
          {
            'name':"top",
            'variables': [ "artist" ],
            'format':"Artist: {0}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "position" ],
            'format':"{0}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Blank",
        'duration':0.5,
        'lines': [
          {
            'name':"top",
            'format':"",
          },
          {
            'name':"bottom",
            'variables': [ "position" ],
            'format':"{0}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Title",
        'duration':10,
		'hidewhenempty':True,
        'hidewhenemptyvars': [ "title" ],
        'lines': [
          {
            'name':"top",
            'variables': [ "title" ],
            'format':"Title: {0}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "position" ],
            'format':"{0}",
            'justification':"left",
            'scroll':False
          }
        ]
      }
    ]
}

PAGES_Stop = {
  'name':"Stop",
  'pages':
    [
      {
        'name':"Ready",
        'duration':12,
        'lines': [
          {
            'name':"top",
            'variables': [ ],
            'format':"Ready",
            'justification':"center",
            'scroll':False
          },
          {
            'name':"bottom",
            'variables': [ "current_time" ],
            'format':"{0}",
            'justification':"center",
            'scroll':False
          }
        ]
      },
      {
        'name':"IPADDR",
        'duration':1.5,
        'lines': [
          {
            'name':"top",
            'variables': [ "current_ip" ],
            'format':"{0}",
            'justification':"center",
            'scroll':False
          },
          {
            'name':"bottom",
            'variables': [ "current_time" ],
            'format':"{0}",
            'justification':"center",
            'scroll':False
          }
        ]
      },
      {
        'name':"SYSTEMVARS",
        'duration':10,
        'lines': [
          {
            'name':"top",
            'variables': [ "current_tempc", "disk_availp" ],
            'format':"Temp: {0}c / Disk {1}% full",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "current_time" ],
            'format':"{0}",
            'justification':"center",
            'scroll':False
          }
        ]
      }
    ]
}

ALERT_Volume = {
 	'name':"Volume",
	'alert': {
  		'variable': "volume",
		'type': "change",
		'suppressonstatechange':True,
		'coolingperiod': 0
	},
	'interruptible':False,
	'pages': [
		{
			'name':"Volume",
        	'duration':2,
        	'lines': [
          		{
            		'name':"top",
            		'variables': [ ],
            		'format':"Volume",
            		'justification':"center",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
            		'variables': [ "volume" ],
            		'format':"{0}",
            		'justification':"center",
            		'scroll':False
          		}
        	]
      	}
    ]
}

ALERT_TempTooHigh = {
 	'name':"TempTooHigh",
	'alert': {
  		'variable': "current_tempc",
		'type': "above",
		'values': [ 85 ],
		'suppressonstatechange':False,
		'coolingperiod': 30
	},
	'interruptible':False,
	'pages': [
		{
			'name':"TempTooHigh",
        	'duration':8,
        	'lines': [
          		{
            		'name':"top",
            		'variables': [ ],
            		'format':"Temp Too High",
            		'justification':"center",
            		'scroll':False
          		},
          		{
            		'name':"bottom",
            		'variables': [ "current_tempc" ],
            		'format':"Temp: {0}c",
            		'justification':"center",
            		'scroll':False
          		}
        	]
      	}
    ]
}


ALERT_LIST = [ ALERT_Volume, ALERT_TempTooHigh ]

class RaspDac_Display:


	def __init__(self):
		logging.info("RaspDac_Display Initializing")

		self.tempreadexpired = 0
		self.diskreadexpired = 0

		self.tempc = 0.0
		self.tempf = 0.0
		self.avail = 0
		self.availp = 0


		# Initilize the connections to the music Daemons.  Currently supporting
		# MPD and SPOP (for Spotify)

		ATTEMPTS=3
		# Will try to connect multiple times

		if MPD_ENABLED:
			for i in range (1,ATTEMPTS):
				self.client = MPDClient(use_unicode=True)

				try:
					# Connect to the MPD daemon
					self.client.connect(MPD_SERVER, MPD_PORT)
					break
				except:
					time.sleep(2)
			else:
				# After the alloted number of attempts did not succeed in connecting
				logging.debug("Unable to connect to MPD service on startup")

		if SPOP_ENABLED:
			# Now attempting to connect to the Spotify daemon
			# This may fail if Spotify is not configured.  That's ok!
			for i in range (1,ATTEMPTS):
				try:
					self.spotclient = telnetlib.Telnet(SPOP_SERVER,SPOP_PORT)
					self.spotclient.read_until("\n")
					break
				except:
					time.sleep(2)
			else:
				# After the alloted number of attempts did not succeed in connecting
				logging.debug("Unable to connect to Spotify service on startup")

		if LMS_ENABLED:
			for i in range (1,ATTEMPTS):
				try:
					# Connect to the LMS daemon
					self.lmsserver = pylms.server.Server(LMS_SERVER, LMS_PORT, LMS_USER, LMS_PASSWORD)
					self.lmsserver.connect()

					# Find correct player
					players = self.lmsserver.get_players()
					for p in players:
						### Need to find out how to get the MAC address from player
						if p.get_ref() == LMS_PLAYER:
							self.lmsplayer = p
							break
					if self.lmsplayer is None:
						self.lmsplayer = self.lmsserver.get_players()[0]
						if self.lmsplayer is None:
							raise Exception('Could not find any LMS player')
					break
				except (socket_error, AttributeError, IndexError):
					logging.debug("Connect attempt {0} to LMS server failed".format(i))
					time.sleep(2)
			else:
				# After the alloted number of attempts did not succeed in connecting
				logging.debug("Unable to connect to LMS service on startup")


	def status_mpd(self):
		# Try to get status from MPD daemon

		try:
			m_status = self.client.status()
			m_currentsong = self.client.currentsong()
		except:
			# Attempt to reestablish connection to daemon
			try:
				self.client.connect(MPD_SERVER, MPD_PORT)
				m_status=self.client.status()
				m_currentsong = self.client.currentsong()
			except:
				logging.debug("Could not get status from MPD daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u"" }

		state = m_status.get('state')
		if state == "play":
			artist = m_currentsong.get('artist')
			name = m_currentsong.get('name')

			# Trying to have something to display.  If artist is empty, try the
			# name field instead.
			if artist is None:
				artist = name

			title = m_currentsong.get('title')
			album = m_currentsong.get('album')
			playlist_position = int(m_status.get('songid'))
			playlist_count = int(m_status.get('playlistlength'))
			volume = int(m_status.get('volume'))
			bitrate = m_status.get('bitrate')

			# Haven't found a way to get the file type from MPD
			tracktype = u""

			(current, duration) = (m_status.get('time').split(":"))

			# since we are returning the info as a JSON formatted return, convert
			# any None's into reasonable values
			if artist is None: artist = u""
			if title is None: title = u""
			if album is None: album = u""
			if current is None: current = 0
			if volume is None: volume = 0
			if bitrate is None: bitrate = u""
			if tracktype is None: tracktype = u""
			if duration is None: duration = 0

			# if duration is not available, then suppress its display
			if int(duration) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))

			return { 'state':u"play", 'artist':artist, 'title':title, 'album':album, 'current':current, 'duration':duration, 'position':timepos, 'volume':volume, 'playlist_position':playlist_position, 'playlist_count':playlist_count, 'bitrate':bitrate, 'type':tracktype }
	  	else:
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}

	def status_spop(self):
		# Try to get status from SPOP daemon

		try:
			self.spotclient.write("status\n")
			spot_status_string = self.spotclient.read_until("\n").strip()
		except:
			# Try to reestablish connection to daemon
			try:
				self.spotclient = telnetlib.Telnet(SPOP_SERVER,SPOP_PORT)
				self.spotclient.read_until("\n")
				self.spotclient.write("status\n")
				spot_status_string = self.spotclient.read_until("\n").strip()
			except:
				logging.debug("Could not get status from SPOP daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}

		spot_status = json.loads(spot_status_string)

	  	if spot_status.get('status') == "playing":
			artist = spot_status.get('artist')
			title = spot_status.get('title')
			album = spot_status.get('album')
			current = spot_status.get('position')
			duration = spot_status.get('duration')
			playlist_position = spot_status.get('current_track')
			playlist_count = spot_status.get('total_tracks')

			# SPOP doesn't seem to have bitrate, track type, or volume available
			bitrate = u""
			tracktype = u""
			volume = 0

		  	# since we are returning the info as a JSON formatted return, convert
		  	# any None's into reasonable values

			if artist is None: artist = u""
			if title is None: title = u""
			if album is None: album = u""
			if current is None: current = 0
			if volume is None: volume = 0
			if bitrate is None: bitrate = u""
			if tracktype is None: tracktype = u""
			if duration is None:
				duration = 0
			else:
				# The spotify client returns time in 1000's of a second
				# Need to adjust to seconds to be consistent with MPD
				duration = duration / 1000

			# if duration is not available, then suppress its display
			if int(duration) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))

			return { 'state':u"play", 'artist':artist, 'title':title, 'album':album, 'current':current, 'duration':duration, 'position':timepos, 'volume':volume, 'playlist_position':playlist_position, 'playlist_count':playlist_count, 'bitrate':bitrate, 'type':tracktype }
	  	else:
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}


	def status_lms(self):
		# Try to get status from LMS daemon

		try:
			lms_status = self.lmsplayer.get_mode()
		except:
			# Try to reestablish connection to daemon
			try:
				self.lmsserver = pylms.server.Server(LMS_SERVER, LMS_PORT, LMS_USER, LMS_PASSWORD)
				self.lmsserver.connect()

				# Find correct player
				players = self.lmsserver.get_players()
				for p in players:
					### Need to find out how to get the MAC address from player
					if p.get_ref() == LMS_PLAYER:
						self.lmsplayer = p
						break
				if self.lmsplayer is None:
					self.lmsplayer = self.lmsserver.get_players()[0]
					if self.lmsplayer is None:
						raise Exception('Could not find any LMS player')

				lms_status = self.lmsplayer.get_mode()
			except (socket_error, AttributeError, IndexError):
				logging.debug("Could not get status from LMS daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u"", 'current_time':u""}


	  	if lms_status == "play":
			import urllib

			artist = urllib.unquote(str(self.lmsplayer.request("artist ?", True))).decode('utf-8')
			title = urllib.unquote(str(self.lmsplayer.request("title ?", True))).decode('utf-8')
			album = urllib.unquote(str(self.lmsplayer.request("album ?", True))).decode('utf-8')
			playlist_position = int(self.lmsplayer.request("playlist index ?"))+1
			playlist_count = self.lmsplayer.playlist_track_count()
			volume = self.lmsplayer.get_volume()
			current = self.lmsplayer.get_time_elapsed()
			duration = self.lmsplayer.get_track_duration()
			url = self.lmsplayer.get_track_path()

			# Get bitrate and tracktype if they are available.  Try blocks used to prevent array out of bounds exception if values are not found
			try:
				bitrate = urllib.unquote(str(self.lmsplayer.request("songinfo 2 1 url:"+url+" tags:r", True))).decode('utf-8').split("bitrate:", 1)[1]
			except:
				bitrate = u""

			try:
				tracktype = urllib.unquote(str(self.lmsplayer.request("songinfo 2 1 url:"+url+" tags:o", True))).decode('utf-8').split("type:",1)[1]
			except:
				tracktype = u""

		  	# since we are returning the info as a JSON formatted return, convert
		  	# any None's into reasonable values

			if artist is None: artist = u""
			if title is None: title = u""
			if album is None: album = u""
			if current is None: current = 0
			if volume is None: volume = 0
			if bitrate is None: bitrate = u""
			if tracktype is None: tracktype = u""
			if duration is None: duration = 0

			# if duration is not available, then suppress its display
			if int(duration) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))


			return { 'state':u"play", 'artist':artist, 'title':title, 'album':album, 'current':current, 'duration':duration, 'position':timepos, 'volume':volume, 'playlist_position':playlist_position, 'playlist_count':playlist_count, 'bitrate':bitrate, 'type':tracktype }
	  	else:
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'album':u"", 'current':0, 'duration':0, 'position':u"", 'volume':0, 'playlist_position':0, 'playlist_count':0, 'bitrate':u"", 'type':u""}


	def status(self):


		# Try MPD daemon first
		if MPD_ENABLED:
			status = self.status_mpd()
		else:
			status = { 'state': "stopped" }

		# If MPD is stopped
		if status.get('state') != "play":

			# Try SPOP
			if SPOP_ENABLED:
				status = self.status_spop()
			else:
				status = { 'state': "stopped" }

			# If SPOP is stopped
			if status.get('state') != "play":

				# Try LMS
				if LMS_ENABLED:
					status = self.status_lms()
				else:
					status = { 'state': "stopped" }


		# Add system variables

		if TIME24HOUR == True:
			current_time = moment.utcnow().timezone(TIMEZONE).format("HH:mm").strip()
		else:
			current_time = moment.utcnow().timezone(TIMEZONE).format("h:m a").strip()

		current_ip = commands.getoutput("ip -4 route get 1 | head -1 | cut -d' ' -f8 | tr -d '\n'").strip()


		# Read Temperature from Pi's on-board temperature sensor once every 20 seconds
		if self.tempreadexpired < time.time():
			self.tempreadexpired = time.time()+20
			try:
				file = open("/sys/class/thermal/thermal_zone0/temp")
				self.tempc = int(file.read())

				# Convert value to float and correct decimal place
				self.tempc = round(float(self.tempc) / 1000,1)

				# convert to fahrenheit
				self.tempf = round(self.tempc*9/5+32,1)

				file.close()
			except IOError:
				self.tempc = 0.0
				self.tempf = 0.0
			except AttributeError:
				file.close()
				self.tempc = 0.0
				self.tempf = 0.0

		# Read available disk space remaining every 20 seconds
		if self.diskreadexpired < time.time():
			self.diskreadexpired = time.time() + 20
			try:
				p = os.popen("df --output='avail','pcent' /")
				line = p.readline()
				line = p.readline().strip()
				self.avail = line[0:line.find("   ")]
				self.availp = line[line.find("   ")+3:]
				# remove % sign
				self.availp = self.availp[0:len(self.availp)-1]

				self.avail = int(self.avail)
				self.availp = int(self.availp)

				p.close()
			except IOError:
				self.avail = 0
				self.availp = 0
			except AttributeError:
				p.close()
				self.avail = 0
				self.availp = 0


		status['current_tempc'] = self.tempc
		status['current_tempf'] = self.tempf
		status['disk_avail'] = self.avail
		status['disk_availp'] = self.availp
		status['current_time'] = current_time
		status['current_ip'] = current_ip

		return status


def Display(q, l, c):
  # q - Queue to receive updates from
  # l - number of lines in display
  # c - number of columns in display

  lines = []
  columns = []

  lcd = Winstar_GraphicOLED.Winstar_GraphicOLED()
  lcd.oledReset()
  lcd.home()
  lcd.clear()

  lcd.message(STARTUP_MSG)
  time.sleep(2)

  for i in range (0, l):
	lines.append("")
	columns.append(0)

  # Get first display update off of the queue
  item = q.get()
  q.task_done()

  lcd.home()
  lcd.clear()

  for i in range(len(item)):
	# Convert from Unicode to UTF-8
	#item[i] = item[i].encode("utf-8")
	lines[i] = item[i]
	lcd.setCursor(0,i)
	lcd.message( lines[i][0:c] )

  prev_time = time.time()

  while True:
	  short_lines=True

	  # Smooth animation
	  if time.time() - prev_time < ANIMATION_SMOOTHING:
		  time.sleep(ANIMATION_SMOOTHING-(time.time()-prev_time))
	  try:
		  # Determine if any lines have been updated and if yes display them
		  for i in range(len(item)):

			  # Convert from Unicode into UTF-8
			  #item[i] = item[i].encode("utf-8")
			  # Check if line is longer than display
			  if len(item[i])>c:
				  short_lines = False

			  # Check if line has been updated
			  if lines[i] != item[i]:
				  # Create a line to print that is at least as long as the existing line
				  # This is to erase any extraneous characters on the display
				  buf = item[i].ljust(len(lines[i]))

				  # Reset cursor to beginning of changed line and then display the change
				  lcd.setCursor(0,i)
				  lcd.message(buf[0:c])

				  # Update the local line data and reset the column position for the line
				  lines[i] = item[i]
				  columns[i] = 0

		  # If lines all fit on display then we can wait for new input
		  if short_lines:
			  item=q.get()
			  q.task_done()
		  else:
			  # Update all long lines
			  for i in range(len(lines)):
				  if len(lines[i])>c:
					  buf = "%s          %s" % (lines[i], lines[i][0:DISPLAY_WIDTH-1])
				  	  #buf = "{}		{}".format(lines[i],lines[i][0:DISPLAY_WIDTH-1])
					  #buf = lines[i]+"		  "+lines[i][0:c]

					  columns[i] = columns[i]+1
					  if columns[i] > len(buf)-c:
						  columns[i]=0

					  lcd.setCursor(0,i)

					  # Print the portion of the string that is currently visible
					  lcd.message(buf[columns[i]:columns[i]+c])
			  # Since we have to continue updating the display, check for a new update but don't block
			  item=q.get_nowait()
			  q.task_done()


		  prev_time = time.time()
	  except Queue.Empty:
		  prev_time = time.time()
		  pass

def sigterm_handler(_signo, _stack_frame):
        sys.exit(0)

if __name__ == '__main__':
        signal.signal(signal.SIGTERM, sigterm_handler)
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=LOGFILE, level=LOGLEVEL)
	logging.info("RaspDac Display Startup")

	try:
		dq = Queue.Queue()  # Create display Queue
		dm = Thread(target=Display, args=(dq,DISPLAY_HEIGHT,DISPLAY_WIDTH))
		dm.setDaemon(True)
		dm.start()

		rd = RaspDac_Display()
	except:
		#e = sys.exc_info()[0]
		#logging.critical("Received exception: %s" % e)
		e = sys.exc_info()[0]
		logging.critical("Caught {0}. Unable to initialize RaspDac Display.  Exiting...".format(e))
		sys.exit(0)

	try:

		current_page_number = -1
		current_line_number = 0
		page_expires = 0
		hesitation_expires = 0
		curlines = []
		hesitate_expires = []
		alert_mode = False

		# Reset all of the alert message cooling values
		for pl in ALERT_LIST:
			pl['cooling_expires'] = 0

		# Initialize previous state
		prev_state = rd.status()

		# Force the system to recognize the start state as a change
		prev_state['state'] = ""

		while True:
			# Get current state of the player
			cstatus = rd.status()
			state = cstatus.get('state')

			alert_check = False
			# Check to see if any alerts are triggered
			for pl in ALERT_LIST:


				# Check to see if alert is in its cooling period
				if pl['cooling_expires'] < time.time():

					# Use try block to skip page if variables are missing
					try:
						# Check to see what type of monitoring to perform
						if pl['alert']['type'] == "change":
							if cstatus[pl['alert']['variable']] != prev_state[pl['alert']['variable']]:
								prev_state[pl['alert']['variable']] = cstatus[pl['alert']['variable']]
								# Some state changes cause variable changes like volume
								# Check to see if these dependent variable changes
								# should be suppressed
								try:
									if not pl['alert']['suppressonstatechange']:
										alert_check = True
								except KeyError:
									pass
						elif pl['alert']['type'] == "above":
							if cstatus[pl['alert']['variable']] > pl['alert']['values'][0]:
								alert_check = True
						elif pl['alert']['type'] == "below":
							if cstatus[pl['alert']['variable']] < pl['alert']['values'][0]:
								alert_check = True
						elif pl['alert']['type'] == "range":
							if cstatus[pl['alert']['variable']] > pl['alert']['values'][0] and cstatus[pl['alert']['variable']] < pl['alert']['values'][1]:
								alert_check = True

						if alert_check:
							alert_mode = True

							# Set current_pages to the alert page
							current_pages = pl
							current_page_number = 0
							current_line_number = 0
							page_expires = time.time() + current_pages['pages'][current_page_number]['duration']
							curlines = []
							hesitate_expires = []

							# Set cooling expiry time.  If not coolingperiod directive, use default
							try:
								pl['cooling_expires'] = time.time() + pl['alert']['coolingperiod']
							except KeyError:
								pl['cooling_expires'] = time.time() + COOLING_PERIOD

							# if an alert has been found, break out of the loop
							# this has the effect of making the order of the list the priority of the messages
							break

					except (KeyError, AttributeError, IndexError):
						pass


			# Set interruptible value.  If value not present, set to default value of True
			try:
				# interruptible is only an override until the page expires.  If page expires, allow page updates to continue.
				if page_expires < time.time():
					interruptible = True

					# if page just expired on an alert page then force restore to current play state
					if alert_mode:
						alert_mode = False
						prev_state['state'] = ""
				else:
					interruptible = current_pages['interruptible']
			except KeyError:
				interruptible = True

			# check to see if we need to change the display to something new
			if (alert_mode or state != prev_state['state']) and interruptible:
				current_page_number = -1
				current_line_number = 0
				page_expires = 0
				curlines = []
				hesitate_expires = []

				# if change caused by state change and not alert
				if alert_mode == False:
					prev_state['state'] = state

					# Set to new display page
					if state != "play":
						current_pages = PAGES_Stop
					# else display the PAGES_Playing pages
					else:
						current_pages = PAGES_Play

			# if page has expired then move to the next page
			if page_expires < time.time():

				# Move to next page and check to see if it should be displayed or hidden
				for i in range(len(current_pages['pages'])):
					current_page_number = current_page_number + 1

					# if on last page, return to first page
					if current_page_number > len(current_pages['pages'])-1:
						current_page_number = 0

					page_expires = time.time() + current_pages['pages'][current_page_number]['duration']

					cp = current_pages['pages'][current_page_number]

					try:
						hwe = cp['hidewhenempty']
					except KeyError:
						hwe = False

					if hwe:
						allempty = True
						try:
							hvars = cp['hidewhenemptyvars']
						except KeyError:
							hvars = [ ]

						for v in hvars:

							try:
								# if the variable is a string
								if type(cstatus[v]) is unicode:
									# and it is not empty, then set allempty False and exit loop
									if len(cstatus[v]) > 0:
										allempty = False
										break
								else:
									# All other variable types are considered not empty
									allempty = False
									break
							except KeyError:
								# if the variable is not in cstatus consider it empty
								pass
						if not allempty:
							break
					else:
						# If not hidewhenempty then exit loop
						break



			# Set current_page
			current_page = current_pages['pages'][current_page_number]

			# Now display the lines from the current page
			lines = []
			for i in range(len(current_page['lines'])):

				# make sure curlines is big enough.  curlines is used to detect when the display has changed
				# if not expanded here it will cause an IndexError later if it has not already been initialized
				while len(curlines) < len(current_page['lines']):
					curlines.append("")

				# make sure hesitate_expires is big enough as well
				while len(hesitate_expires) < len(current_page['lines']):
					hesitate_expires.append(0)

				current_line = current_page['lines'][i]
				try:
					justification = current_line['justification']
				except KeyError:
					justification = "left"

				try:
					scroll = current_line['scroll']
				except KeyError:
					scroll = False

				try:
					variables = current_line['variables']
				except KeyError:
					variables = []

				format = current_line['format']

				# Get paramaters
				# ignore KeyError exceptions if variable is unavailable
				parms = []
				try:
					for j in range(len(current_line['variables'])):
						try:
							if type(cstatus[current_line['variables'][j]]) is unicode:
								parms.append(cstatus[current_line['variables'][j]].encode('utf-8'))
							else:
								parms.append(cstatus[current_line['variables'][j]])
						except KeyError:
							pass
				except KeyError:
					pass

				# create line to display
				line = format.format(*parms).decode('utf-8')

				# justify line
				try:
					if current_line['justification'] == "center":
						line = "{0:^{1}}".format(line, DISPLAY_WIDTH)
					elif current_line['justification'] == "right":
						line = "{0:>{1}}".format(line, DISPLAY_WIDTH)
				except KeyError:
					pass

				lines.append(line)

				# determine whether to scroll or not
				# if scroll is false, set hesitation time to large value which
				# effectively shuts off the scroll function
				if lines[i] != curlines[i]:
					curlines[i] = lines[i]
					try:
						if current_line['scroll']:
							hesitate_expires[i] = time.time() + HESITATION_TIME
						else:
							hesitate_expires[i] = time.time() + 86400 # Do not scroll
					except KeyError:
						hesitate_expires[i] = time.time() + 86400 # Do not scroll

			# Determine if the display should hesitate before scrolling
			dispval = []
			for i in range(len(lines)):
				if hesitate_expires[i] < time.time():
					dispval.append(lines[i])
				else:
					dispval.append(lines[i][0:DISPLAY_WIDTH])

			# Send dispval to the queue
			dq.put(dispval)

			# sleep before next update
			time.sleep(.25)


	except KeyboardInterrupt:
		pass

	finally:
		dq.put(["Goodbye!",""])
		logging.info("Goodbye!")
		try:
			rd.client.disconnect()
		except:
			pass
		try:
			rd.spotclient.write("bye\n")
			rd.spotclient.close()
		except:
			pass

		time.sleep(2)
		dq.put(["",""])
		time.sleep(1)
		if DISPLAY_INSTALLED:
			GPIO.cleanup()
		else:
			curses.endwin()

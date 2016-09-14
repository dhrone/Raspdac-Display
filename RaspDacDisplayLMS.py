import Winstar_GraphicOLED
import moment
import time
import json
import logging
import commands
from mpd import MPDClient
import pylms
from pylms import server
from pylms import player
import telnetlib

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

ARTIST_TIME = 8.0 # Amount of time to display Artist name (in seconds)
TITLE_TIME = 10.0 # Amount of time to display the Title  (in seconds)
HESITATION_TIME = 2.5 # Amount of time to hesistate before scrolling (in seconds)
ANIMATION_SMOOTHING = .24 # Amount of time before repainting display
NOTPLAYING_TIMEDISPLAY = 8.0 # Amount of time to display Time
NOTPLAYING_IPDISPLAY   = 1.5 # Amount of time to display IP address

# The Winstar display shipped with the RaspDac is capable of two lines of display
# when the 5x8 font is used.  This code assumes that is what you will be using.
# The display logic would need significant rework to support a different number
# of display lines!

DISPLAY_WIDTH = 16 # the character width of the display
DISPLAY_HEIGHT = 2 # the number of lines on the display

# This is where the log file will be written
#LOGFILE='/var/log/RaspDacDisplay.log'
LOGFILE='./log/RaspDacDisplay.log'

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
MPD_ENABLED = False
MPD_SERVER = "localhost"
MPD_PORT = 6600

SPOP_ENABLED = False
SPOP_SERVER = "localhost"
SPOP_PORT = 6602

LMS_ENABLED = True
LMS_SERVER = "localhost"
LMS_PORT = 9090
LMS_USER = ""
LMS_PASSWORD = ""

# Set this to MAC address of the Player you want to monitor.
# THis should be the MAC of the RaspDac system if using Max2Play with SqueezePlayer
LMS_PLAYER = "00:01:02:aa:bb:cc"


# Page Definitions
PAGE_Play = {
  'name':"Play",
  'pages':
    [
      {
        'name':"Artist",
        'duration':6,
        'lines': [
          {
            'name':"top",
            'variables': [ "artist" ],
            'format':"{0}",
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
        'duration':1,
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
        'lines': [
          {
            'name':"top",
            'variables': [ "title" ],
            'format':"{0}",
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

PAGE_Stop = {
  'name':"Stop",
  'pages':
    [
      {
        'name':"Ready",
        'duration':10,
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
      }
    ]
}


class RaspDac_Display:


	def __init__(self):
		logging.info("RaspDac_Display Initializing")

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
					self.lmsserver = pylms.server.Server(LMS_SERVER)
					self.lmsserver.connect()
					self.lmsplayer = self.lmsserver.get_players()[0]
					break
				except:
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
				self.client.connect("localhost", 6600)
				m_status=self.client.status()
				m_currentsong = self.client.currentsong()
			except:
				logging.debug("Could not get status from MPD daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'current':0, 'duration':0, 'position':u"", 'bitrate':u"", 'type':u"", 'current_time':u""}

		state = m_status.get('state')
		if state == "play":
			artist = m_currentsong.get('artist')
			name = m_currentsong.get('name')

			# Trying to have something to display.  If artist is empty, try the
			# name field instead.
			if artist is None:
				artist = name
				title = m_currentsong.get('title')

			(current, duration) = (m_status.get('time').split(":"))

			# since we are returning the info as a JSON formatted return, convert
			# any None's into reasonable values
		  	if artist is None: artist = u""
		  	if title is None: title = u""
		  	if current is None: current = 0
		  	if duration is None: duration = 0

		  	# if duration is not available, then surpress its display
  			if int(duration) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))

			return { 'state':state, 'artist':artist, 'title':title, 'current':current, 'position':timepos, 'duration': duration }
		else:
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'current':0, 'duration':0 }

	def status_spop(self):
		# Try to get status from SPOP daemon

		try:
			self.spotclient.write("status\n")
			spot_status_string = self.spotclient.read_until("\n").strip()
		except:
			# Try to reestablish connection to daemon
			try:
				self.spotclient = telnetlib.Telnet("localhost",6602)
				self.spotclient.read_until("\n")
				self.spotclient.write("status\n")
				spot_status_string = self.spotclient.read_until("\n").strip()
			except:
				logging.debug("Could not get status from SPOP daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'current':0, 'duration':0, 'position':u"", 'bitrate':u"", 'type':u"", 'current_time':u""}

		spot_status = json.loads(spot_status_string)

	  	if spot_status.get('status') == "playing":
			artist = spot_status.get('artist')
			title = spot_status.get('title')
			current = spot_status.get('position')
			duration = spot_status.get('duration')

		  	# since we are returning the info as a JSON formatted return, convert
		  	# any None's into reasonable values

			if artist is None: artist = u""
			if title is None: title = u""
			if current is None: current = 0
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

			return { 'state':u"play", 'artist':artist, 'title':title, 'current':current, 'duration': duration, 'position':timepos }
	  	else:
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'current':0, 'duration':0 }


	def status_lms(self):
		# Try to get status from LMS daemon

		try:
			lms_status = self.lmsplayer.get_mode()
		except:
			# Try to reestablish connection to daemon
			try:
				self.lmsserver = pylms.server.Server()
				self.lmsserver.connect()
				self.lmsplayer = self.lmsserver.get_players()[0]
				lms_status = self.lmsplayer.get_mode()
			except:
				logging.debug("Could not get status from LMS daemon")
				return { 'state':u"stop", 'artist':u"", 'title':u"", 'current':0, 'duration':0, 'position':u"", 'bitrate':u"", 'type':u"", 'current_time':u""}


	  	if lms_status == "play":
			import urllib

			artist = urllib.unquote(str(self.lmsplayer.request("artist ?", True))).decode('utf-8')
			title = urllib.unquote(str(self.lmsplayer.request("title ?", True))).decode('utf-8')
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
			if current is None: current = 0
			if bitrate is None: bitrate = u""
			if tracktype is None: tracktype = u""
			if duration is None:
				duration = 0

			# if duration is not available, then suppress its display
			if int(duration) > 0:
				timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
			else:
				timepos = time.strftime("%M:%S", time.gmtime(int(current)))


			return { 'state':u"play", 'artist':artist, 'title':title, 'current':current, 'duration':duration, 'position':timepos, 'bitrate':bitrate, 'type':tracktype }
	  	else:
			return { 'state':u"stop", 'artist':u"", 'title':u"", 'current':0, 'duration':0, 'position':u"", 'bitrate':u"", 'type':u""}


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
		  # Determine if any lines have been udpated and if yes display them
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
		logging.critical("Unable to initialize RaspDac Display.  Exiting...")
		sys.exit(0)

	try:


#		display_mode = "ARTIST"
#		beenplaying = True
#		currentArtist = ""
#		currentTitle = ""
#		cpos = ""

#		ctime = ""
#		hesitate = False
#		hesitation_etime = 0
#		display_etime = 0
#		notplaying_state = "TIME"
#		ctime = ""
#		hesitation_etime = time.time() + HESITATION_TIME

		current_page_number = -1
		current_line_number = 0
		current_state = ""
		state_change = False
		page_expires = 0
		hesitation_expires = 0
		curlines = []
		hesitate_expires = []

		while True:
			# Get current state of the player
			cstatus = rd.status()
			state = cstatus.get('state')

			# check for player state changed
			if state != current_state:
				current_state = state
				state_change = True
				current_page_number = -1
				current_line_number = 0
				page_expires = 0
				curlines = []
				hesitate_expires = []

			# if not playing then display the PAGE_Stop pages
			if state != "play":
				current_pages = PAGE_Stop
			else:
				current_pages = PAGE_Play

			# if page has expired then move to the next page
			if page_expires < time.time():
				current_page_number = current_page_number + 1

				# if on last page, return to first page
				if current_page_number > len(current_pages['pages'])-1:
					current_page_number = 0

				page_expires = time.time() + current_pages['pages'][current_page_number]['duration']

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
							parms.append(cstatus[current_line['variables'][j]])
						except KeyError:
							pass
				except KeyError:
					pass

				# create line to display
				line = format.format(*parms)

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
				if lines[i] != curlines[i]:
					curlines[i] = lines[i]
					try:
						if current_line['scroll']:
							hesitate_expires[i] = time.time() + HESITATION_TIME
						else:
							hesitate_expires[i] = 0
					except KeyError:
						hesitate_expires[i] = 0

			# Determine if the display should hesitate before scrolling
			dispval = []
			for i in range(len(lines)):
				if hesitate_expires[i] < time.time():
					dispval.append(lines[i])
				else:
					dispval.append(lines[i][0:DISPLAY_WIDTH])

			# Send dispval to the queue
#			logging.info("Putting: {0}".format(dispval))
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

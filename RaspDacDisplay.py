import Winstar_GraphicOLED
import moment
import time
import json
import logging
from mpd import MPDClient
import telnetlib
import RPi.GPIO as GPIO
import Queue
from threading import Thread
import sys


ARTIST_TIME = 8.0 # Amount of time to display Artist name (in seconds)
TITLE_TIME = 10.0 # Amount of time to display the Title  (in seconds)
HESITATION_TIME = 2.5 # Amount of time to hesistate before scrolling (in seconds)

# The Winstar display shipped with the RaspDac is capable of two lines of display
# when the 5x8 font is used.  This code assumes that is what you will be using.
# The display logic would need significant rework to support a different number
# of display lines!

DISPLAY_WIDTH = 16 # the character width of the display
DISPLAY_HEIGHT = 2 # the number of lines on the display

# This is where the log file will be written
LOGFILE='/var/log/RaspDacDisplay.log'

# Adjust this setting to localize the time display to your region
TIMEZONE="US/Eastern"


class RaspDac_Display:


	def __init__(self):
		logging.info("RaspDac_Display Initializing")

		# Initilize the connections to the music Daemons.  Currently supporting
		# MPD and SPOP (for Spotify)

		ATTEMPTS=10
		# Will try to connect multiple times

		for i in range (1,ATTEMPTS):
			self.client = MPDClient()

			try:
				# Connect to the MPD daemon
				self.client.connect("localhost", 6600)
				break
			except:
				logging.warning("Connection to MPD service attempt " + str(i) + " failed")
				time.sleep(2)
		else:
			# After the alloted number of attempts did not succeed in connecting
			logging.critical("Unable to connect to MPD service")

			# Passing Exception on to calling routine which will likely exit
			raise

		# Now attempting to connect to the Spotify daemon
		for i in range (1,ATTEMPTS):
			try:
				self.spotclient = telnetlib.Telnet("localhost",6602)
				self.spotclient.read_until("\n")
				break
			except:
				logging.warning("Connection to Spotify service attempt " + str(i) + " failed")
				time.sleep(2)
		else:
			# After the alloted number of attempts did not succeed in connecting
			logging.critical("Unable to connect to Spotify service")

			# Passing Exception on to calling routine which will likely exit
			raise



	def status(self):
		# Try MPD daemon first
		m_status = self.client.status()
		m_currentsong = self.client.currentsong()

		# Get the MPD player state and act accordingly
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
		  if artist is None: artist = ""
		  if title is None: title = ""
		  if current is None: current = 0
		  if duration is None: duration = 0
		  return { 'state':state, 'artist':artist, 'title':title, 'current':current, 'duration': duration }
		else :

		  # Try SPOT if MPD is not playing
		  self.spotclient.write("status\n")
		  spot_status_string = self.spotclient.read_until("\n").strip()
		  spot_status = json.loads(spot_status_string)
		  if spot_status.get('status') == "playing":
			artist = spot_status.get('artist')
			title = spot_status.get('title')
			current = spot_status.get('position')
			duration = spot_status.get('duration')

		  	# since we are returning the info as a JSON formatted return, convert
		  	# any None's into reasonable values

			if artist is None: artist = ""
			if title is None: title = ""
			if current is None: current = 0
			if duration is None:
				duration = 0
			else:
				# The spotify client returns time in 1000's of a second
				# Need to adjust to seconds to be consistent with MPD
				duration = duration / 1000

			return { 'state':"play", 'artist':artist, 'title':title, 'current':current, 'duration': duration }
		  else :
			return { 'state':"stop" }


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

  lcd.message("RaspDac\nStarting")
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
	lines[i] = item[i]
	lcd.setCursor(0,i)
	lcd.message( lines[i][0:c] )

  prev_time = time.time()

  while True:
	  short_lines=True

	  # Smooth animation
	  if time.time() - prev_time < .05:
		  time.sleep(.05-(time.time()-prev_time))
	  try:
		  # Determine if any lines have been udpated and if yes display them
		  for i in range(len(item)):
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
				  	  buf = "{0:s}        {1:s}".format(lines[i],lines[i][0:DISPLAY_WIDTH-1])
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


if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename=LOGFILE, level=logging.INFO)
	logging.info("RaspDac Display Startup")

	try:
		rd = RaspDac_Display()
	except:
		#e = sys.exc_info()[0]
		#logging.critical("Received exception: %s" % e)
		logging.critical("Unable to initialize RaspDac Display.  Exiting...")
		sys.exit(0)

	try:

		q = Queue.Queue()
		dm = Thread(target=Display, args=(q,DISPLAY_HEIGHT,DISPLAY_WIDTH))
		dm.setDaemon(True)
		dm.start()

		display_mode = "ARTIST"
		beenplaying = True
		currentArtist = ""
		currentTitle = ""
		cpos = ""

		ctime = ""
		hesitate = False
		hesitation_etime = 0
		display_etime = 0


		while True:
			current_time = moment.utcnow().timezone(TIMEZONE).format("h:m A").strip()

			cstatus = rd.status()
			state = cstatus.get('state')

			if state != "play":
				if beenplaying:
					beenplaying = False
					currentArtist = ""
					currentTitle = ""
					logging.info("Ready " + current_time)
					q.put(["Ready",current_time])


				# Only update display time if the time has changed
				if current_time != ctime:
					logging.info("Ready " + current_time)
					q.put(["Ready", current_time])
					ctime = current_time

				time.sleep(1)

			else:
				title = cstatus.get('title')
				artist = cstatus.get('artist')
				playing_song = artist + ": " + title

				current = cstatus.get("current")
				duration = cstatus.get("duration")

				# if duration is not available, then suppress its display
				if int(duration) > 0:
					timepos = time.strftime("%M:%S", time.gmtime(int(current))) + "/" + time.strftime("%M:%S", time.gmtime(int(duration)))
				else:
					timepos = time.strftime("%M:%S", time.gmtime(int(current)))

				update_needed = False
				if (beenplaying == False) or (currentTitle != title) or (currentArtist != artist):
					beenplaying = True
					currentTitle = title
					currentArtist = artist
					logging.info(current_time + " (local): " + playing_song)
					display_mode = "ARTIST"
					display_etime = time.time()+ARTIST_TIME
					if (len(str(artist))>DISPLAY_WIDTH):
						hesitation_etime = time.time()+HESITATION_TIME
						hesitate=True
						display = artist[0:DISPLAY_WIDTH]
					elif (len(str(artist)) > 0):
						display = artist
					else:
						display_etime = 0 # force artist display to be skipped if the field is empty
					update_needed = True
				else:
					# Only update display if the time position has changed
					if timepos != cpos:
						update_needed = True
						cpos = timepos

				if (hesitation_etime < time.time() and hesitate):
					update_needed = True
					hesitate = False
					if display_mode == "ARTIST":
						display = artist
					else:
						display = title


				if display_etime < time.time():
					update_needed = True
					if display_mode == "ARTIST":
						display_etime = time.time() + TITLE_TIME
						if len(str(title)) > 0:
							display_mode = "TITLE"
							display = title
					else:
						display_etime = time.time() + ARTIST_TIME
						if len(str(artist)) > 0:
							display_mode = "ARTIST"
							display = artist

					if len(str(artist)) == 0 and len(str(title)) == 0:
						# if neither artist and title contain values
						display = "No song info"

					if (len(display)>DISPLAY_WIDTH):
						hesitate = True
						hesitation_etime = time.time() + HESITATION_TIME
						display = display[0:DISPLAY_WIDTH]

				# Only update if one of the display items has changed
				if update_needed:
					# add new display items to display queue
					q.put([display, timepos])
					update_needed = False

				time.sleep(.25)


	except KeyboardInterrupt:
		pass

	finally:
		q.put(["Goodbye!",""])
		logging.info("Goodbye!")
		rd.client.disconnect()
		rd.spotclient.write("bye\n")
		rd.spotclient.close()
		time.sleep(2)
		q.put(["",""])
		time.sleep(1)
		GPIO.cleanup()

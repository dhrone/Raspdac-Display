# This version rotates between Album, Artist, and Title Pages and then includes
# a page to show metadata about the song.
# It places a short "blank" page between each that shows a blank line on top but
# continues to show song position on the bottom.
# At the bottom of each page, the track position, track length, current song
# playtime, and current song length are displayed.  If the current track position
# and track length are > 1 the line with be truncated due to the 16 character limit
# of the display.  To keep the look of the bottom of the display stable, scrolling
# has been set off.
PAGES_Play = {
  'name':"Play",
  'pages':
    [
      {
        'name':"Album",
        'duration':10,
		'hidewhenempty':'any',
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Artist",
        'duration':10,
		'hidewhenempty':'any',
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Title",
        'duration':10,
		'hidewhenempty':'any',
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
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
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      },
      {
        'name':"Meta Data",
        'duration':10,
		'hidewhenempty':'any',
        'hidewhenemptyvars': [ "bitrate", "type" ],
        'lines': [
          {
            'name':"top",
            'variables': [ "bitrate", "type" ],
            'format':"Rate: {0}, Type: {1}",
            'justification':"left",
            'scroll':True
          },
          {
            'name':"bottom",
            'variables': [ "playlist_display", "position" ],
            'format':"{0} {1}",
            'justification':"left",
            'scroll':False
          }
        ]
      }

    ]
}

# This version rotates between Album, Artist, and Title Pages and then includes
# a page to show track position, and a page to display metadata about the song
# It places a short "blank" page between each that shows a blank line on top but
# continues to show song position on the bottom.
# Because it does not show track position and length at the bottom of each
# page, it doesn't need to worry about the line being truncated.
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
        'name':"Track Data",
        'duration':10,
		'hidewhenempty':True,
        'hidewhenemptyvars': [ "playlist_count" ],
        'lines': [
          {
            'name':"top",
            'variables': [ "playlist_position", "playlist_count" ],
            'format':"Playing {0} of {1}",
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
        'name':"Meta Data",
        'duration':10,
		'hidewhenempty':True,
        'hidewhenemptyvars': [ "bitrate", "type" ],
        'lines': [
          {
            'name':"top",
            'variables': [ "bitrate", "type" ],
            'format':"Rate: {0}, Type: {1}",
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

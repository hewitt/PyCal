#!/usr/bin/env python
"""
USAGE: PyCal.py  [OPTIONS]

A very simple text-based calendar event tracker. If, like me, you don't
have every second of your day timetabled but do want to keep track
of a handful of events, then most app/web-based calendars are overkill. 
The aim here is to do only very simple things, via text files and CLI.
I wanted to make something that works like todo.sh 
(http://ginatrapani.github.com/todo.txt-cli/) but keeps track of a few 
date-tagged items.

See the top of the code for defaults, including the filename of the
calendar file.

Past events are dropped silently from the calendar file after a set
period of time.

OPTIONS:

  agenda <number>; lists all events <number> days into the future from today.

  add <datetime, event>; adds the string <event> to <datetime>. The <datetime> 
    may be in a fuzzy format, e.g "Thursday" or "Jun 14th 10am". A comma must
    be used as a separator. Any events lacking a time will default to 00:00.

  ls <date>; lists the events in the calendar for day <date>.

EXAMPLE: 

PyCal.py add "Thursday 7am, Walk the dog"

License: GPL3, http://www.gnu.org/copyleft/gpl.html

"""
__author__="Rich.E.Hewitt"
__version__="0.1"

#
# BEGIN CUSTOMISATION
#

# text file for storing the calendar
CAL_FILENAME = "/home/hewitt/CURRENT/cal.txt"
# global dictionary storage of the calendar
CAL_DICT = {}
# if true then dates are stored as DD/MM/YY
# US users may prefer MM/DD/YY
DAY_FIRST_FORMAT = True
# drop events from the calendar after these many days
DROP_AFTER_DAYS = 7

#
# END CUSTOMISATION
#


# system imports
import getopt
#import time
import os, sys
# 3rd party datetime for fuzzy date parsing
try:
  from dateutil.parser import *
  from dateutil.tz import *
  from datetime import *
except ImportError:
  print "[ ERROR ] We rely on the python-dateutil package."
  print "[ ERROR ] See http://labix.org/python-dateutil "
  print "[ ERROR ] eg. on Debian try, sudo apt-get install python-dateutil"
  sys.exit()




def datetime_parse(string):
  """ Parse the a string into a datetime object. Catch any exceptions."""
  try:
    return parse( string, dayfirst = DAY_FIRST_FORMAT )
  except:    
    print "[ ERROR ] Badly formatted event string."
    sys.exit()




def cal_add(string):
  """ Add an entry to the calendar. Allow for fuzzy dates
  by parsing with the 3rd party dateutil module. A comma
  must occur between the date and the event title and be the
  first such comma in the string to be added to the calendar.
  """
  # split the string into a (potentially fuzzy) date and an event string 
  separator_index = string.index( ',' )
  date_string = string[0:separator_index]
  event_string = string[separator_index+1:].lstrip(' ')
  CAL_DICT[ datetime_parse( date_string ) ] = event_string




def cal_parse(cal_filename):
  """ Parse the calendar text file. The format is
      DD/MM/YY HH:MM event_string
      where the first two spaces are field separators.
  """
  # open the calendar file
  if ( cal_filename != "" ):
    try:
        cal_file = open( cal_filename, 'r')
    except IOError:
        print "[ ERROR ] Calendar file is missing!"
        sys.exit()
  else:
    print "[ ERROR ] No calendar file specified"
    sys.exit()
  # read the whole calendar file in one go
  cal_lines = cal_file.readlines()
  # for each line in the calendar file 
  for line in cal_lines:
    # get rid of any trailing new line characters
    line = line.rstrip( '\n' )
    # we assume a comma separates the date from the event
    separator_index = line.index( ',' )
    datetime_string = line[ 0 : separator_index ]
    event_string = line[ separator_index + 1 : ].lstrip( ' ' )
    # convert from the txt date representation to a datetime object for later date comparisons
    date = datetime_parse( datetime_string )
    # store the entry in a dictionary with the datetime as a key
    CAL_DICT[ date ] = event_string




def cal_list( day_string ):
  """ List events on a specific date."""
  # parse the date
  day = datetime_parse( day_string )
  # loop through the calendar in order
  for key in sorted(CAL_DICT.iterkeys()): 
    if key.date() == day.date():
      print key.strftime( "%H:%M" ) + ", " + CAL_DICT[ key ]  




def cal_display( days_ahead ):
  """ Display the calendar contents for a set number of 
  days into the future.
  """
  # today's date
  start = date.today()
  # check each day in the calendar from today
  for day in range( 0, days_ahead ):
    output_day = start.strftime( "%A %d %B" ) + "\n"
    output_events = ""
    # loop through the calendar in order
    for key in sorted(CAL_DICT.iterkeys()): 
      if key.date() == start:
        output_events += key.strftime( "%H:%M" ) + ", " + CAL_DICT[ key ] + "\n"
    # output days with events in them
    if output_events != "":
      print output_day + output_events    
    # move to the next day
    start += timedelta( days = 1 )




def cal_write(cal_filename):
  """ Write the calendar file."""
  try:
	  cal_file = open( cal_filename, 'w')
  except IOError:
    print "[ ERROR ] Calendar file missing."
    sys.exit()
  # current date/time
  now = datetime.now()
  # we'll silently drop events from the calendar after
  # a set number of days
  delta_past = timedelta( days = DROP_AFTER_DAYS )
  # loop through the dates in order & write each one
  for key in sorted(CAL_DICT.iterkeys()):
    if ( key > now - delta_past ):
      cal_file.write( key.strftime( "%d/%m/%y %H:%M" ) + ", " + CAL_DICT[ key ] + "\n" )
  cal_file.close()




################
# MAIN PROGRAM #
################

def main():
  args = sys.argv[1:]
  # parse the calendar
  cal_parse( CAL_FILENAME )
  
  if ( len( args ) > 0 ):
    # Extract the arguments/switches
    if ( "add" == args[0] ):
      # add an entry to the calendar
      event_string = ""
      # assume other arguments form the event string
      for i in range( 1, len(args) ):
        event_string += args[i] + " "
      # add the event to the calendar
      cal_add( event_string )
      # write the file, currently hoping we've not
      # just screwed things up & trashed the file ;-)
      cal_write( CAL_FILENAME )
      # exit
      sys.exit() 
    elif ( "agenda" == args[0] ):
      # list coming events 'days' into the future from today
      # default to a week      
      days = 7
      if ( len(args) >= 2 ):
        days = int(args[1])
      # display the events
      cal_display( days )
      # exit
      sys.exit()
    elif ( "ls" == args[0] ):
      # list events on a specific day
      # assume the date is the remaining arguments
      date_string = ""
      for i in range( 1, len(args) ):
        date_string += args[i] + " "
      # list the events on the day
      cal_list( date_string )
      # exit
      sys.exit()
  # don't know what user wants, so print the documentation
  print __doc__
  # exit
  sys.exit()

if __name__ == "__main__":
  main()

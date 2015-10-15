#!/usr/bin/python
import sys
from datetime import datetime, timedelta, date
import argparse
import re

intervals = ('second', 'minute', 'hour', 'day')
curryear = date.today().year

tzts_re = re.compile('(?P<datestring>(?P<date>[0-9]{2}/[A-Za-z]{3}/[0-9]{4}):(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}) (?P<offset_dir>[+-])(?P<offset>[0-9]{4}))')
syslog_re = re.compile('(?P<datestring>(?P<date>[A-Za-z]{3} [0-9 ]{2}) (?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}))')

parser = argparse.ArgumentParser(description='Shift the syslog date for all entries in an input data set by a specified interval of time.  Offset and interval options are required unless using --utcmode.')
parser.add_argument('-o', '--offset', help='Amount of time to shift (pos/neg integer)', type=int)
parser.add_argument('-i', '--interval', help='Interval of time to shift', choices = intervals)
parser.add_argument('-u', '--utcmode', help='Automatically parse timestamps such as "29/Aug/2013:23:46:33 -0400" to UTC', action='store_true', default=False)
parser.add_argument('-y', '--year', help='Year to assume (default %d)' % curryear, default=curryear, type=int)
parser.add_argument('-r', '--infile', help='Input file to process (default STDIN)')
parser.add_argument('-w', '--outfile', help='Output file to create - will be overwritten if exists (default STDOUT)')
args = parser.parse_args()

if args.utcmode == None and (args.offset == None or args.interval == None):
    stderr.write('ERROR: Offset and interval options are both required when not using --utcmode\n')
    sys.exit(2)

# open the input file or use STDIN if not specified
if args.infile:
    try:
        infile = open(args.infile, 'r')
    except IOError:
        print 'Could not open input file'
        exit(2)
else:
    infile = sys.stdin

# open the output file or use STDOUT if not specified
if args.outfile:
    try:
        outfile = open(args.outfile, 'w')
    except IOError:
        print 'Could not open output file'
        exit(2)
else:
    outfile = sys.stdout

# iterate through each line of the input data
for line in infile:
    if args.utcmode:
        parts = tzts_re.search(line)

        origtimestring = '%s %s' % (parts.group('date'), parts.group('time'))
        origtime = datetime.strptime(origtimestring, '%d/%b/%Y %X')

        offset_dir = parts.group('offset_dir')
        offset = parts.group('offset')
        offset_hr = int(offset[0:2])
        offset_min = int(offset[2:4])
        offset = timedelta(hours=offset_hr, minutes = offset_min)

        # we are correcting the time zone to UTC, so the math is opposite the TZ direction
        if offset_dir == '+':
            newtime = origtime - offset
        else:
            newtime = origtime + offset

        newtimestring = newtime.strftime('%d/%b/%Y:%X')
        newline = tzts_re.sub(newtimestring+' +0000\0', line)

    else:
        # establish a timedelta object that defines the requested offset and interval
        if args.interval == 'second':
            offset = timedelta(seconds = args.offset)
        elif args.interval == 'minute':
            offest = timedelta(minutes = args.offset)
        elif args.interval == 'hour':
            offset = timedelta(hours = args.offset)
        elif args.interval == 'day':
            offset = timedelta(hours = args.offset * 24)

        # syslog timestamp is the first 15 characters by default (e.g. "Nov 20 15:20:02")
        # then add a year, which may matter in a leap year
        parts = syslog_re.search(line)

        origtimestring = '%s %s' % (parts.group('datestring'), args.year)
        origtime = datetime.strptime(origtimestring, '%b %d %X %Y')

        # calculate the new time in a time object
        newtime = origtime + offset

        # reconstruct the new line
        # the %-2d format string is a two-character wide format that omits any leading zeroes (uses space instead) - nice!
        newtimestring = newtime.strftime('%b %-2d %X')
        newline = syslog_re.sub(newtimestring+'\0', line)

        #'%s%s' % (newtime.strftime('%b %-2d %X'), remainder)

    # write the new line, including a formatted timestamp for the corrected time
    outfile.write(newline)
#!/usr/bin/python
import sys
from datetime import datetime, timedelta, date
import argparse

intervals = ('second', 'minute', 'hour', 'day')
curryear = date.today().year

parser = argparse.ArgumentParser(description='Shift the syslog date for all entries in an input data set by a specified interval of time.  Offset and Interval options are required.')
parser.add_argument('-o', '--offset', help='Amount of time to shift (pos/neg integer)', required=True, type=int)
parser.add_argument('-i', '--interval', help='Interval of time to shift', required=True, choices = intervals)
parser.add_argument('-y', '--year', help='Year to assume (default %d)' % curryear, default=curryear, type=int)
parser.add_argument('-r', '--infile', help='Input file to process (default STDIN)')
parser.add_argument('-w', '--outfile', help='Output file to create - will be overwritten if exists (default STDOUT)')
args = parser.parse_args()

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

# establish a timedelta object that defines the requested offset and interval
if args.interval == 'second':
    offset = timedelta(seconds = args.offset)
elif args.interval == 'minute':
    offest = timedelta(minutes = args.offset)
elif args.interval == 'hour':
    offset = timedelta(hours = args.offset)
elif args.interval == 'day':
    offset = timedelta(hours = args.offset * 24)

# iterate through each line of the input data
for line in infile:
    # syslog timestamp is the first 15 characters by default (e.g. "Nov 20 15:20:02")
    # then add a year, which may matter in a leap year
    origtimestring = line[0:15] + ' %d' % args.year
    origtime = datetime.strptime(origtimestring, '%b %d %X %Y')

    # rest of the line will remain the same
    remainder = line[15:]

    # calculate the new time in a time object
    newtime = origtime + offset

    # write the new line, including a formatted timestamp for the new time
    # the %-2d format string is a two-character wide format that omits any leading zeroes (uses space instead) - nice!
    outfile.write('%s%s' % (newtime.strftime('%b %-2d %X'), remainder))

#!/usr/bin/python
# (C)2018 Lewes Technology Consulting, LLC
import sys
from datetime import datetime, timedelta, date
import argparse
import re

intervals = ('second', 'minute', 'hour', 'day')
conversion_modes = ('syslog', 'httpdlog', 'rfc3339', 'cobaltstrike')
curryear = date.today().year

syslog_re = re.compile('(?P<datestring>(?P<date>[A-Za-z]{3} [0-9 ]{2}) (?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}))')
httpd_re = re.compile('(?P<datestring>(?P<date>[0-9]{2}/[A-Za-z]{3}/[0-9]{4}):(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}) (?P<offset_dir>[+-])(?P<offset>[0-9]{4}))')
rfc3339_re = re.compile('(?P<datestring>(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?P<subsecond>\.[0-9]{6})(?P<offset_dir>[+-])(?P<offset>[0-9]{2}:[0-9]{2}))')
cobaltstrike_re = re.compile('(?P<datestring>(?P<date>[0-9]{2}/[0-9 ]{2}) (?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}))')

parser = argparse.ArgumentParser(description='Shift the date for all entries in an input data set by a specified interval of time. Offset and interval options are required when using syslog mode.')
parser.add_argument('-m', '--mode', help='Type of timestamp to seek and adjust (default = syslog)', choices = conversion_modes, default='syslog')
parser.add_argument('-o', '--offset', help='Amount of time to shift (pos/neg integer, only required for "syslog" mode', type=int)
parser.add_argument('-i', '--interval', help='Interval of time to shift (only required for "syslog" and "cobaltstrike" modes', choices = intervals)
parser.add_argument('-y', '--year', help='Year to assume (default %d)' % curryear, default=curryear, type=int)
parser.add_argument('-r', '--infile', help='Input file to process (default STDIN)')
parser.add_argument('-w', '--outfile', help='Output file to create - will be overwritten if exists (default STDOUT)')
args = parser.parse_args()

if args.mode == 'syslog' and (args.offset == None or args.interval == None):
    sys.stderr.write('ERROR: Offset and interval options are both required when not using --mode syslog\n')
    sys.exit(2)

# open the input file or use STDIN if not specified
if args.infile:
    try:
        infile = open(args.infile, 'r')
    except IOError:
        sys.stderr.write('Could not open input file')
        exit(2)
else:
    infile = sys.stdin

# open the output file or use STDOUT if not specified
if args.outfile:
    try:
        outfile = open(args.outfile, 'w')
    except IOError:
        sys.stderr.write('Could not open output file')
        exit(2)
else:
    outfile = sys.stdout

# iterate through each line of the input data
for line in infile:
    if args.mode == 'httpdlog':
        parts = httpd_re.search(line)

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
        newline = httpd_re.sub(newtimestring+' +0000', line)

    elif args.mode == 'rfc3339':
        parts = rfc3339_re.search(line)

        origtimestring = '%sT%s' % (parts.group('date'), parts.group('time'))
        origtime = datetime.strptime(origtimestring, '%Y-%m-%dT%X')

        offset_dir = parts.group('offset_dir')
        (offset_hr, offset_min) = [ int(x) for x in parts.group('offset').split(':') ]
        offset = timedelta(hours=offset_hr, minutes = offset_min)

        # we are correcting the time zone to UTC, so the math is opposite the TZ direction
        if offset_dir == '+':
            newtime = origtime - offset
        else:
            newtime = origtime + offset

        newtimestring = newtime.strftime('%Y-%m-%dT%X')
        newline = rfc3339_re.sub(newtimestring+parts.group('subsecond')+'+00:00', line)


    elif args.mode == 'cobaltstrike':
        # establish a timedelta object that defines the requested offset and interval
        if args.interval == 'second':
            offset = timedelta(seconds = args.offset)
        elif args.interval == 'minute':
            offset = timedelta(minutes = args.offset)
        elif args.interval == 'hour':
            offset = timedelta(hours = args.offset)
        elif args.interval == 'day':
            offset = timedelta(hours = args.offset * 24)

        # cobalt strike timestamps don't include a year.  add it.
        parts = cobaltstrike_re.search(line)

        if parts != None:
            origtimestring = '%s/%s %s' % (parts.group('date'), args.year, parts.group('time'))
            origtime = datetime.strptime(origtimestring, '%m/%d/%Y %X')

            # calculate the new time in a time object
            newtime = origtime + offset

            # reconstruct the new line
            newtimestring = newtime.strftime('%Y-%m-%dT%X')
            newline = cobaltstrike_re.sub(newtimestring, line)

        else:
            newline = line

    #assuming syslog format below!
    else:
        # establish a timedelta object that defines the requested offset and interval
        if args.interval == 'second':
            offset = timedelta(seconds = args.offset)
        elif args.interval == 'minute':
            offset = timedelta(minutes = args.offset)
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
        newline = syslog_re.sub(newtimestring, line)

        #'%s%s' % (newtime.strftime('%b %-2d %X'), remainder)

    # write the new line, including a formatted timestamp for the corrected time
    outfile.write(newline)
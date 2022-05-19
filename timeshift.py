#!env python3
# (C)2022 Lewes Technology Consulting, LLC
import sys
from datetime import datetime, timedelta, date
import argparse
import re
# import json

intervals = ('second', 'minute', 'hour', 'day')
conversion_modes = ('syslog', 'httpdlog', 'rfc3339', 'cobaltstrike', 'ual')
# conversion_modes = ('syslog', 'httpdlog', 'rfc3339', 'cobaltstrike', 'json')
curryear = date.today().year

syslog_re = re.compile('(?P<full_dts_string>(?P<date>[A-Za-z]{3} [0-9 ]{2}) (?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}))')
httpd_re = re.compile('(?P<full_dts_string>(?P<date>[0-9]{2}/[A-Za-z]{3}/[0-9]{4}):(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}) (?P<offset_dir>[+-])(?P<offset>[0-9]{4}))')
rfc3339_re = re.compile('(?P<full_dts_string>(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?P<subsecond>\.[0-9]{6})(?P<offset_dir>[+-])(?P<offset>[0-9]{2}:[0-9]{2}))')
rfc3339dtonly_re = re.compile('(?P<full_dts_string>(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T)(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})')
# technically, this is "rfc3339-ish" in that it will also match just %FT%T style date/time, variable subsecond lengths, and "Z" instead of an explicit offset
rfc3339ish_re = re.compile('(?P<full_dts_string>(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})(?P<t_separator>[T ])(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})(?P<subsecond>\.[0-9]+)?(?:(?P<offset_dir>[+-])(?P<offset>[0-9]{2}:[0-9]{2})|(?P<zulu>Z))?)')
cobaltstrike_re = re.compile('(?P<full_dts_string>(?P<date>[0-9]{2}/[0-9 ]{2}) (?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2}))')

parser = argparse.ArgumentParser(description='Shift the date for all entries in an input data set by a specified interval of time.')
parser.add_argument('-m', '--mode', help='Type of timestamp to seek and adjust (default = syslog)', choices = conversion_modes, default='syslog')
# parser.add_argument('-j', '--jsonpath', help='JSON path to modify, in dotted notation for nested fields (only required for "json" mode)')
parser.add_argument('-o', '--offset', help='Amount of time to shift (pos/neg integer, only required for "syslog" or "ual" modes)', type=int)
parser.add_argument('-i', '--interval', help='Interval of time to shift (only required for "syslog", "cobaltstrike", or "ual" modes)', choices = intervals)
parser.add_argument('-y', '--year', help='Year to assume (default %d)' % curryear, default=curryear, type=int)
parser.add_argument('-r', '--infile', help='Input file to process (default STDIN)')
parser.add_argument('-w', '--outfile', help='Output file to create - will be overwritten if exists (default STDOUT)')
args = parser.parse_args()

# NOTE: right now, syslog, CS, and UAL allow arbitrary adjustment, while others only normalize to UTC (e.g. no arbitrary adjustments)

if (args.mode == 'syslog' or args.mode == 'cobaltstrike' or args.mode == 'ual') and (args.offset == None or args.interval == None):
    sys.stderr.write('ERROR: Offset and interval options are both required when not using syslog, cobaltstrike, or ual modes\n')
    sys.exit(2)

# if (args.mode == 'json' and args.jsonpath == None):
#     sys.stderr.write('ERROR: JSON field is required when using --mode json\n')
#     sys.exit(2)

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

# if args.mode == 'json':
#     try:
#         raw_json = json.load(infile)
    
#     except json.decoder.JSONDecodeError:
#         sys.stderr.write('Could not process input file JSON')
#         exit(2)

#     parts = rfc3339_re.search(raw_json[args.jsonpath])

#     if parts != None:
#         origtimestring = '%sT%s%s' % (parts.group('date'), parts.group('time'), parts.group('subsecond'))
#         origtime = datetime.strptime(origtimestring, '%Y-%m-%dT%X%f')

#         # establish a timedelta object that defines the requested offset and interval
#         if args.interval == 'second':
#             offset = timedelta(seconds = args.offset)
#         elif args.interval == 'minute':
#             offset = timedelta(minutes = args.offset)
#         elif args.interval == 'hour':
#             offset = timedelta(hours = args.offset)
#         elif args.interval == 'day':
#             offset = timedelta(hours = args.offset * 24)
#         else:
#             offset_dir = parts.group('offset_dir')
#             offset = parts.group('offset')
#             offset_hr = int(offset[0:2])
#             offset_min = int(offset[2:4])
#             offset = timedelta(hours=offset_hr, minutes=offset_min)

#             # we are correcting the time zone to UTC, so the math is opposite the TZ direction
#             if offset_dir == '+':
#                 offset = -offset

#         newtime = origtime + offset

#         newtimestring_format = '%%d%s%%X' % (parts.group('dtseparator'))
#         if parts.group

#     #outfile.write('%s\n' % (json.dumps(xxxxxxxxx)))

# else:

# iterate through each line of the input data
for line in infile:
    if args.mode == 'httpdlog':
        parts = httpd_re.search(line)

        if parts != None:
            origtimestring = '%s %s' % (parts.group('date'), parts.group('time'))
            origtime = datetime.strptime(origtimestring, '%d/%b/%Y %X')

            offset_dir = parts.group('offset_dir')
            offset = parts.group('offset')
            offset_hr = int(offset[0:2])
            offset_min = int(offset[2:4])
            offset = timedelta(hours=offset_hr, minutes = offset_min)

            # we are correcting the time zone to UTC, so the math is opposite the TZ direction
            if offset_dir == '+':
                offset = -offset
            newtime = origtime + offset

            newtimestring = newtime.strftime('%d/%b/%Y:%X'+' +0000')
            line = line.replace(parts.group('full_dts_string'), newtimestring)

    elif args.mode == 'rfc3339':
        parts = rfc3339_re.search(line)

        if parts != None:
            origtimestring = '%sT%s' % (parts.group('date'), parts.group('time'))
            origtime = datetime.strptime(origtimestring, '%Y-%m-%dT%X')

            offset_dir = parts.group('offset_dir')
            (offset_hr, offset_min) = [ int(x) for x in parts.group('offset').split(':') ]
            offset = timedelta(hours=offset_hr, minutes = offset_min)

            # we are correcting the time zone to UTC, so the math is opposite the TZ direction
            if offset_dir == '+':
                offset = -offset
            newtime = origtime + offset

            newtimestring = newtime.strftime('%Y-%m-%dT%X'+parts.group('subsecond')+'+00:00')
            line = line.replace(parts.group('full_dts_string'), newtimestring)

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
            line = line.replace(parts.group('full_dts_string'), newtimestring)

    elif args.mode == 'ual':
        # establish a timedelta object that defines the requested offset and interval
        if args.interval == 'second':
            offset = timedelta(seconds = args.offset)
        elif args.interval == 'minute':
            offset = timedelta(minutes = args.offset)
        elif args.interval == 'hour':
            offset = timedelta(hours = args.offset)
        elif args.interval == 'day':
            offset = timedelta(hours = args.offset * 24)

        for parts in rfc3339ish_re.finditer(line):
            if parts != None:
                origtimestring = '%sT%s' % (parts.group('date'), parts.group('time'))
                origtime = datetime.strptime(origtimestring, '%Y-%m-%dT%X')

                # calculate the new time in a time object
                newtime = origtime + offset

                newtimestring = newtime.strftime('%Y-%m-%dT%X')
                if parts.group('subsecond'):
                    newtimestring = newtimestring+parts.group('subsecond')
                if parts.group('zulu'):
                    newtimestring = newtimestring+parts.group('zulu')
                elif parts.group('offset'):
                    newtimestring = newtimestring+'00:00'
                
                line = line.replace(parts.group('full_dts_string'), newtimestring)

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

        if parts != None:
            origtimestring = '%s %s' % (parts.group('full_dts_string'), args.year)
            origtime = datetime.strptime(origtimestring, '%b %d %X %Y')

            # calculate the new time in a time object
            newtime = origtime + offset

            # reconstruct the new line
            # the %-2d format string is a two-character wide format that omits any leading zeroes (uses space instead) - nice!
            newtimestring = newtime.strftime('%b %-2d %X')
            line = line.replace(parts.group('full_dts_string'), newtimestring)

            #'%s%s' % (newtime.strftime('%b %-2d %X'), remainder)

    # write the new line, including a formatted timestamp for the corrected time
    outfile.write(line)

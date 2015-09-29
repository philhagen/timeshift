# syslog-timeshift
A python script to shift the timestamp on syslog data. Useful for forensicators combating time skew.

## Usage

```
$ ./timeshift.py --help
usage: timeshift.py [-h] -o OFFSET -i {second,minute,hour,day} [-y YEAR]
                    [-r INFILE] [-w OUTFILE]

Shift the syslog date for all entries in an input data set by a specified
interval of time. Offset and Interval options are required.

optional arguments:
  -h, --help            show this help message and exit
  -o OFFSET, --offset OFFSET
                        Amount of time to shift (pos/neg integer)
  -i {second,minute,hour,day}, --interval {second,minute,hour,day}
                        Interval of time to shift
  -y YEAR, --year YEAR  Year to assume (default 2015)
  -r INFILE, --infile INFILE
                        Input file to process (default STDIN)
  -w OUTFILE, --outfile OUTFILE
                        Output file to create - will be overwritten if exists
                        (default STDOUT)
```

### Example Usage
Original contents of syslog file:

```
$ cat maillog 
Jun  8 15:20:02 proxy sendmail[2295]: alias database /etc/aliases rebuilt by root
Jun  8 15:20:02 proxy sendmail[2295]: /etc/aliases: 76 aliases, longest 10 bytes, 765 bytes total
Jun  8 15:20:02 proxy sendmail[2300]: starting daemon (8.13.8): SMTP+queueing@01:00:00
Jun  8 15:20:02 proxy sm-msp-queue[2308]: starting daemon (8.13.8): queueing@01:00:00
```

Assuming source file is reflected in EDT (UTC-0400), change to UTC (as it should be!):
```
$ timeshift.py -o 4 -i hour -r maillog
Jun  8 19:20:02 proxy sendmail[2295]: alias database /etc/aliases rebuilt by root
Jun  8 19:20:02 proxy sendmail[2295]: /etc/aliases: 76 aliases, longest 10 bytes, 765 bytes total
Jun  8 19:20:02 proxy sendmail[2300]: starting daemon (8.13.8): SMTP+queueing@01:00:00
Jun  8 19:20:02 proxy sm-msp-queue[2308]: starting daemon (8.13.8): queueing@01:00:00
```

Correct sendmail entries in source file to account for the system's clock being 23 seconds fast
```
$ grep sendmail maillog | ./timeshift.py -o -23 -i second
Jun  8 15:19:39 proxy sendmail[2295]: alias database /etc/aliases rebuilt by root
Jun  8 15:19:39 proxy sendmail[2295]: /etc/aliases: 76 aliases, longest 10 bytes, 765 bytes total
Jun  8 15:19:39 proxy sendmail[2300]: starting daemon (8.13.8): SMTP+queueing@01:00:00
```

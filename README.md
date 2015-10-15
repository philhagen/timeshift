# syslog-timeshift
A python script to shift the timestamp on syslog data. Useful for forensicators combating time skew.

## Usage

```
$ ./timeshift.py --help
usage: timeshift.py [-h] [-o OFFSET] [-i {second,minute,hour,day}] [-u]
                    [-y YEAR] [-r INFILE] [-w OUTFILE]

Shift the syslog date for all entries in an input data set by a specified
interval of time. Offset and interval options are required unless using
--utcmode.

optional arguments:
  -h, --help            show this help message and exit
  -o OFFSET, --offset OFFSET
                        Amount of time to shift (pos/neg integer)
  -i {second,minute,hour,day}, --interval {second,minute,hour,day}
                        Interval of time to shift
  -u, --utcmode         Automatically parse timestamps such as
                        "29/Aug/2013:23:46:33 -0400" to UTC
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

Original contents of HTTPD access log file:
```
$ cat lewestech.com-access
82.220.38.35 - - [11/Oct/2015:10:42:02 +0400] "POST /wp-login.php HTTP/1.1" 200 4697 "http://lewestech.com/wp-login.php" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0"
208.115.113.85 - - [11/Oct/2015:11:27:15 +0400] "GET /clients/clients/waggies-by-maggie HTTP/1.1" 301 128 "-" "Mozilla/5.0 (compatible; DotBot/1.1; http://www.opensiteexplorer.org/dotbot, help@moz.com)"
65.254.225.173 - - [11/Oct/2015:11:29:49 +0400] "POST /wp-login.php HTTP/1.1" 200 4697 "http://lewestech.com/wp-login.php" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0"
82.239.166.225 - - [11/Oct/2015:11:58:49 +0400] "GET /tag/for572/ HTTP/1.1" 200 24951 "https://www.google.fr" "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"
82.239.166.225 - - [11/Oct/2015:11:58:50 +0400] "GET /wp-content/themes/lewestech/style.css HTTP/1.1" 200 10512 "http://lewestech.com/tag/for572/" "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"
82.239.166.225 - - [11/Oct/2015:11:58:51 +0400] "GET /wp-content/themes/lewestech/scripts/utils.js HTTP/1.1" 200 123 "http://lewestech.com/tag/for572/" "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"
```

Convert HTTPD access log with UTC offset to UTC native
```
$ cat lewestech.com-access | ./timeshift.py -u
82.220.38.35 - - [11/Oct/2015:06:42:02 +0000] "POST /wp-login.php HTTP/1.1" 200 4697 "http://lewestech.com/wp-login.php" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0"
208.115.113.85 - - [11/Oct/2015:07:27:15 +0000] "GET /clients/clients/waggies-by-maggie HTTP/1.1" 301 128 "-" "Mozilla/5.0 (compatible; DotBot/1.1; http://www.opensiteexplorer.org/dotbot, help@moz.com)"
65.254.225.173 - - [11/Oct/2015:07:29:49 +0000] "POST /wp-login.php HTTP/1.1" 200 4697 "http://lewestech.com/wp-login.php" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0"
82.239.166.225 - - [11/Oct/2015:07:58:49 +0000] "GET /tag/for572/ HTTP/1.1" 200 24951 "https://www.google.fr" "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"
82.239.166.225 - - [11/Oct/2015:07:58:50 +0000] "GET /wp-content/themes/lewestech/style.css HTTP/1.1" 200 10512 "http://lewestech.com/tag/for572/" "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"
82.239.166.225 - - [11/Oct/2015:07:58:51 +0000] "GET /wp-content/themes/lewestech/scripts/utils.js HTTP/1.1" 200 123 "http://lewestech.com/tag/for572/" "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"
```
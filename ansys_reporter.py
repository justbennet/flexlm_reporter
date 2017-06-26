#!/usr/bin/env python

import os
import re
import csv
from glob import glob
from os.path import join as pathjoin

logdir = '/Users/bennet/github/flexlm_reporter/ansys'
workdir = '/tmp'

log_files = glob(logdir + '/*.log')

# One file for testing
log_files = ['/Users/bennet/github/flexlm_reporter//ansys/ansys.2017-01-08_17:17:45.log',]

#  Example data patterns needed for processing
#  and the regular expressions that will match them
#
# Beware of whitespace at line ends!
#
# Example startup date line.
# 9:49:40 (lmgrd) Server's System Date and Time: Thu Jun 08 2017 09:49:40 EDT
lmgrd_start = re.compile('([ ]*\d{1,2}:\d{1,2}:\d{1,2}) \(lmgrd\) .* \(linux\) \((\d+/\d+/\d+)\)')

# Example TIMESTAMP entries
#  9:49:41 (lmgrd) TIMESTAMP 6/23/2017
# 14:50:01 (ansyslmd) TIMESTAMP 6/23/2017
timestamp = re.compile(r'([ ]*\d{1,2}:\d{1,2}:\d{1,2}) \(\w+\) TIMESTAMP (\d+/\d+/\d+)')

# Example checkout lines; note that there are two formats
# HFSS features
# 21:06:15 (ansyslmd) OUT: "hfsshpc" manikafa@nyx7005.arc-ts.umich.edu  (20 licenses) 
# 21:06:15 (ansyslmd) OUT: "hfss_solve" manikafa@nyx7005.arc-ts.umich.edu  
#
# 16:42:19 (ansyslmd) IN: "hfss_solve" caixz@nyx7005.arc-ts.umich.edu  
# 16:42:19 (ansyslmd) IN: "hfsshpc" caixz@nyx7005.arc-ts.umich.edu  (8 licenses) 

# Ansys features
# 16:56:03 (ansyslmd) OUT: "aa_r_hpc" imchae@nyx5525.arc-ts.umich.edu  (32 licenses) 
# 18:15:02 (ansyslmd) OUT: "aa_r" imchae@nyx5525.arc-ts.umich.edu  
#
#  6:28:32 (ansyslmd) IN: "aa_r" minkikim@nyx5510.arc-ts.umich.edu  
# 16:18:10 (ansyslmd) IN: "aa_r_hpc" imchae@nyx5512.arc-ts.umich.edu  (32 licenses) 

# This one matches both, but it doesn't capture the optional license count
# ansys_feature = re.compile('([ ]*\d{1,2}:\d{1,2}:\d{2}) \(ansyslmd\) (\w+): \"(\S+)\" (\w+)@(\S+)')
ansys_feature = re.compile('[ ]*(?P<time>\d{1,2}:\d{1,2}:\d{2}) \(ansyslmd\) (?P<action>\w+): \"(?P<feature>\S+)\" (?P<user>\w+)@(?P<host>\S+)\s+\(*(?P<count>[0-9]*)\)*')
ansys_tokens = re.compile('\(\d+\)')

# List for the log data
data = []

# Dictionary for the feature usage
usage = {}

for file_name in log_files:
    print("\nWorking on " + os.path.basename(file_name))
    print("Initializing all licenses to 0")
    # List for the log data
    data = []
    # Dictionary for the feature usage
    usage = {}
    with open(file_name) as f:
        for line in f:
            line.strip()
            # Note that the match() method starts at the beginning and looks
            # forward.
            if ansys_feature.match(line):
                p = ansys_feature.match(line)
                time = p.group('time')
                feature = p.group('feature')
                user = p.group('user')
                host = p.group('host')
                if p.group('count') == '':
                    count = 1
                else:
                    count = p.group('count')
                    count = int(count)
                if p.group('action') == 'OUT':
                    print ( "Checked out %s on %s at %s to %s %s tokens" %
                       (feature, date, time, user, count))
                    if feature in usage:
                        usage[feature] += count
                    else:
                        usage[feature] = count
                elif p.group('action') == 'IN':
                    print ( "Checked in %s on %s at %s to %s %s tokens" %
                       (feature, date, time, user, count))
                    usage[feature] -= count
                else:
                    p = ''
                    pass
                data.append([date, time, feature, user, host, p.group('action'), count])
                print("%s has %s tokens checked out" % (feature, usage[feature]))
            elif timestamp.match(line):
                p = timestamp.match(line)
                time = p.group(1)
                date = p.group(2)
                # print("TIMESTAMP recorded at: %s %s\n" % (date, time))
            elif lmgrd_start.match(line):
                # We create a match object, and it has the bits that match
                p = lmgrd_start.match(line)
                # We pull them out and assign them to objects that will persist
                date = p.group(2)
                time = p.group(1)
                print ( "%-25s %s %s"
                         % ("License server started", date, time) )
        print("%-25s %s %s"
               % ("License server stopped", date, time))

    headings = ['date', 'time', 'feature', 'user', 'host', 'action', 'count']

    with open(file_name + '.csv', 'w') as csv_output:
        wtr = csv.writer(csv_output, lineterminator='\n')
        wtr.writerow(headings)
        [wtr.writerow(line) for line in data]
    csv_output.close()

print "\n\nPrinting usages for each feature\n" + "="*32 + '\n'
for key in sorted(usage.keys()):
    print "Feature %-25s:  %d" % (key, usage[key])

print("\n\n")


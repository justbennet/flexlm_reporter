#!/usr/bin/env python

def process_ansys():
    import os
    import re
    import csv
    from glob import glob
    from os.path import join as pathjoin
    from collections import defaultdict

    # Set the root of the log file directories and get log filenames
    logdir = '/Users/bennet/github/flexlm_reporter/ansys'
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
    lmgrd_start = re.compile('(?P<time>[ ]*\d{1,2}:\d{1,2}:\d{1,2}) \(lmgrd\) .* \(linux\) \((?P<date>\d+/\d+/\d+)\)')

    # Example TIMESTAMP entries
    #  9:49:41 (lmgrd) TIMESTAMP 6/23/2017
    # 14:50:01 (ansyslmd) TIMESTAMP 6/23/2017
    timestamp = re.compile(r'(?P<time>[ ]*\d{1,2}:\d{1,2}:\d{1,2}) \(\w+\) TIMESTAMP (?P<date>\d+/\d+/\d+)')

    # Example checkout lines; note that there are two formats
    #
    # HFSS features
    # 21:06:15 (ansyslmd) OUT: "hfsshpc" manikafa@nyx7005.arc-ts.umich.edu  (20 licenses) 
    # 21:06:15 (ansyslmd) OUT: "hfss_solve" manikafa@nyx7005.arc-ts.umich.edu  
    #
    # 16:42:19 (ansyslmd) IN: "hfss_solve" caixz@nyx7005.arc-ts.umich.edu  
    # 16:42:19 (ansyslmd) IN: "hfsshpc" caixz@nyx7005.arc-ts.umich.edu  (8 licenses) 
    #
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

    for file_name in log_files:
        print("\nWorking on " + os.path.basename(file_name))
        print("Initializing all licenses to 0")
        # List for the log data
        data = []
        # Dictionary for the feature usage
        usage = {}
        # Default dictionary for the feature cumulative counts
        cum_usage = defaultdict(int)
        
        with open(file_name) as f:
            for line in f:
                line.strip()
                # Note that the match() method starts at the beginning and looks
                # forward.

                # Do we match a feature IN/OUT line?
                if ansys_feature.match(line):
                    p = ansys_feature.match(line)
                    # Assign values matched to variables
                    time = p.group('time')
                    feature = p.group('feature')
                    user = p.group('user')
                    host = p.group('host')

                    # The log lines have an optional number of tokens at the end
                    # We need to make missing = 1
                    if p.group('count') == '':
                        count = 1
                    else:
                        count = p.group('count')
                        count = int(count)

                    # We are checking out license(s)
                    if p.group('action') == 'OUT':
                        # Debugging print statement
                        # print ( "Checked out %s on %s at %s to %s %s tokens" %
                        #    (feature, date, time, user, count))

                        # We have to check to see if the key exists.  If it does, we add
                        # the current number of licenses being checked out, otherwise set
                        # to the number being checked out
                        if feature in usage:
                            usage[feature] += count
                        else:
                            usage[feature] = count
                        # We want eventually to know how many times during the logging
                        # period each count of checked out licenses was reached.  To do
                        # this, we are going to create a new dictionary key that contains
                        # both the feature name and the count of checked out licenses at
                        # the conclusion of that transaction.
                        #
                        # We do this at checkout and checkin

                        feature_count_key = '{:12s}: {:>4d}'.format(feature, usage[feature])
                        cum_usage[feature_count_key] += usage[feature]

                    # We are checking in license(s)
                    elif p.group('action') == 'IN':
                        # Debugging print statement
                        # print ( "Checked in %s on %s at %s to %s %s tokens" %
                        #    (feature, date, time, user, count))

                        # We want to set usage to 0 if it would go negative
                        if usage[feature] > count:
                            usage[feature] -= count
                        else:
                            usage[feature] = 0

                        # Update the cumulative usage counts
                        feature_count_key = '{:12s}: {:>4d}'.format(feature, usage[feature])
                        cum_usage[feature_count_key] += usage[feature]

                    # End feature processing

                    # We don't know what this is, so we set p to null and pass
                    else:
                        p = ''
                        pass
                    # We are going to create a .csv file with one row for every transaction
                    data.append([date, time, feature, user, host, p.group('action'), count])

                    # Debugging print statement
                    # print("%s has %s tokens checked out" % (feature, usage[feature]))

                # We matched a timestamp line
                elif timestamp.match(line):
                    p = timestamp.match(line)
                    time = p.group('time')
                    date = p.group('date')
                    # print("TIMESTAMP recorded at: %s %s\n" % (date, time))

                # We matched the lmgrd server start line
                elif lmgrd_start.match(line):
                    p = lmgrd_start.match(line)
                    date = p.group('date')
                    time = p.group('time')
                    print ( "%-25s %s %s"
                             % ("License server started", date, time) )

            # We are now done with log processing, so we print the final date
            print("%-25s %s %s"
                   % ("License server stopped", date, time))

        # Define the headings for the .csv file
        headings = ['date', 'time', 'feature', 'user', 'host', 'action', 'count']

        # Write the .csv output
        with open(file_name + '.csv', 'w') as csv_output:
            wtr = csv.writer(csv_output, lineterminator='\n')
            wtr.writerow(headings)
            [wtr.writerow(line) for line in data]
        csv_output.close()
        return data, cum_usage

if __name__ == '__main__':

    data, cum_usage = process_ansys()
    print("{}       ".format("Feature    Used", "Occurrences"))
    print("="*40)
    last_key = ''
    for usage in sorted(cum_usage.keys()):
        # Need to split the key on the colon and compare the value of the
        # feature name only.
        #
        if usage == last_key:
            print("{}   {:>4d}".format(usage, cum_usage[usage]))
            last_key = usage
        else:
            print("{}{}".format(40*'-', "\n"))
            print("{}   {:>4d}".format(usage, cum_usage[usage]))
            last_key = usage
    print("="*40)


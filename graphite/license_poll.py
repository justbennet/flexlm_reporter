#####  Script to collect license usage samples

# import needed libraries
from subprocess import check_output
from collections import defaultdict
import datetime

# record the date and time for use in output, formatted as we want
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# setting verbose to yes will cause usernames to be printed in the report
verbose = 'yes'

# we want to use defaultdicts so we can add to a nonexistent key
license_count = defaultdict(int)
license_total = defaultdict(int)
license_users = defaultdict(set)

# these are the licenses we will check
license_daemons = {}
license_daemons['matlab'] = { 'port':  '1709', 'host': 'flux-license1.miserver.it.umich.edu'}
license_daemons['abaqus'] = { 'port': '27000', 'host': 'flux-license1.miserver.it.umich.edu'}

# this is the command we will check with
lmstat = '/sw/arc/centos7/flexlm/11.11.1.2/bin/lmstat'

# cycle through the defined daemons
for daemon in sorted(license_daemons.keys()):
    # we need a string like: port@host to query with
    license_host = ( license_daemons[daemon]['port']
                     + '@' + license_daemons[daemon]['host'] )
    # this runs the check; -a signals all features, -c specifies port@host
    # this comes back as one string, which we split to make a list
    lmstat_output = check_output([lmstat, '-a', '-c', license_host],
                          universal_newlines=True).split('\n')
    # process the output
    for line in lmstat_output:
        # find the summary line
        if line.find('Users of') == 0:
            # grab the feature name, which is the third item and strip the colon
            feature = line.split()[2]
            feature = feature.rstrip(':')
            # some licenses do not increment by one per use, so we have to
            # get the total used here or do fancy arithmetic later; we also
            # want to know from how many total, which is also here
            license_count[feature] = line.split()[10]
            license_total[feature] = line.split()[5]
        # user activity lines have the hostname and port in them
        if line.find(license_daemons[daemon]['host'] + '/' + license_daemons[daemon]['port']) > 0:
            # license_users is a set, so we split the username from the line
            # and add it to the set and we don't have to think about dupliates
            license_users[feature].add(line.split()[0])
        else:
            pass

    # create text output
    # header for each license daemon
    print("{} licenses {}".format(daemon, timestamp))

    # header for the licenses used
    print("licenses used count")
    for feature in sorted(license_count.keys()):
        # only print if something is used
        if int(license_count[feature]) > 0:
            print("    {:32s}:  {:>3} of {:>6}".format(feature, license_count[feature], license_total[feature]))

    # header for the active users
    print("unique user counts")
    for feature in sorted(license_users.keys()):
        # the number of users in the set will be unique users
        print("    {:32s}:  {:>3}".format(feature, len(license_users[feature])))
        # if verbose is set, list the usernames
        if verbose == 'yes' :
            for user in license_users[feature]:
                print("    {}{}".format(40*' ', user))

# end program
# vim: tabstop=4 shiftwidth=4 expandtab

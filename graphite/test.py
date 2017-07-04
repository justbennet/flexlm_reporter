import sys
import socket
import datetime
import random

# This was the old location
# hpc/software/licenses/FEATURE

# This is proposed
# hpc/flux/software/licenses/vendor/feature

# where to send it
carbon_url = 'graphite.arc-ts.umich.edu'
carbon_port = 2003

# create time stamp for current time
timestamp = datetime.datetime.now().strftime('%s')

# create data to test
daemon   = 'greeting'
features = [ 'hello', 'yowza', 'whazzup' ]

# initialize empty message list
messages = []

for feature in features:
    # generate some fake data
    available   = '50'
    used        = str(random.randrange(2, int(available)))
    users       = str(random.randrange(1, int(used)))

    # line it up for sending
    feature_root = '.'.join(['hpc.flux.software.licenses', daemon, feature])
    messages.append(' '.join([feature_root + '.available',
                             available, timestamp]))
    messages.append(' '.join([feature_root + '.users',
                             users, timestamp]))
    messages.append(' '.join([feature_root + '.used',
                             used, timestamp]))
messages.append('')

# set up the socket and timeout
sock = socket.socket()
sock.settimeout(10.0)

try:
    # message away
    sock.connect((carbon_url, carbon_port))
    sock.sendall('\n'.join(messages).encode('utf-8'))
    sock.close()
    # we want confirmation for now
    for line in messages:
        print(line)
except:
    print('Problem sending data to Graphite/Carbon')
    sys.exit(1)

print('SUCCESS')


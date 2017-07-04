import sys
import socket
import datetime

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
daemon  = 'hello'
feature = 'greeting'
used   = '4'
total   = '10'
users   = '2'

# initialize empty message list
messages = []

messages.append(' '.join(['hpc.flux.software.licenses' + '.'
                           + daemon + feature + '.'
                           + 'number_available', total, timestamp]))
messages.append(' '.join(['hpc.flux.software.licenses' + '.'
                           + daemon + feature + '.'
                           + 'number_used', used, timestamp]))
messages.append(' '.join(['hpc.flux.software.licenses' + '.'
                           + daemon + feature + '.'
                           + 'number_users', users, timestamp]))

sock = socket.socket()
sock.settimeout(10.0)

try:
    sock.connect((carbon_url, carbon_port))
    sock.sendall('\n'.join(messages).encode('utf-8'))
    sock.close()
except:
    print('Problem sending data to Graphite/Carbon')
    sys.exit(1)

print('SUCCESS')


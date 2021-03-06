"""
Server for RaaSIO Robot.

This server listens to port 1137.  Clients include the Cyclops app
as well as the Arduino sensors.

To run this, first install SL4A (Scripting Layer for Android), then
install the Python interpreter using SL4a.  The latest SL4A apk is
available at:

    http://www.mithril.com.au/android/sl4a_r5x.apk

To run this from the command line on the phone, some environment 
variables need to be set:

    $ sh PY raasio_server.py
    
where PY contains:
    
    $ cat PY
    
    PW=`pwd`
    export EXTERNAL_STORAGE=/mnt/sdcard
    export LANG=en
    PYTHONPATH=/mnt/sdcard/com.googlecode.pythonforandroid/extras/python
    PYTHONPATH=${PYTHONPATH}:/data/data/com.googlecode.pythonforandroid/files/python/lib/python2.6/lib-dynload
    export PYTHONPATH
    export TEMP=/mnt/storage/com.googlecode.pythonforandroid/extras/python/tmp
    export PYTHON_EGG_CACHE=$TEMP
    export PYTHONHOME=/data/data/com.googlecode.pythonforandroid/files/python
    export LD_LIBRARY_PATH=/data/data/com.googlecode.pythonforandroid/files/python/lib
    cd $PW
    /data/data/com.googlecode.pythonforandroid/files/python/bin/python "$@"

"""
from socket import *
import threading
import thread

HOST = '' 
PORT = 1137
BACKLOG = 5 
BUFSIZE = 512
DEBUG = False

THROTTLE_SERVO = 10
STEERING_SERVO = 11
TILT_SERVO     = 12
PAN_SERVO      = 13


def handler(clientsock,addr):
    while True:
        data = clientsock.recv(BUFSIZE)
        if not data:
            if DEBUG: print "no data"
            break
            
        if DEBUG: print "RECIEVED:" , data
        if not data.startswith('$'):
            return
            
        sentence = data.split('*')[0]
        x = sentence.split(',')
        header = x[0]
        if header == '$GPGGA':
            print 'GPS: ', x[1:]
            
        elif header == '$PRSO100':
            print 'LRF: ', x[1]
            
        elif header == '$PRSO200':
            print 'OFS: ', x[1:]
            
        elif header.startswith('$PRSO30'):
            print 'SONAR' + header[-1] + ': ', x[1]
            
        elif header == '$PRSO400':
            print 'BUMPER: ', x[1]
            
        elif header == '$PRSO500':
            area, cx, cy = int(x[1]), int(x[2]), int(x[3])
            print 'BLOB: ', area, cx, cy
            if area == 0:
                return

            # move servo depending on the horizontal
            # location of the largest bounding box found.

            # dx is the normalized offset from center of screen.
            # -1 < dx < 1.  dx = 0 implies center.
            dx = (cx - 640)/640.0  # assumes screen width = 1280

            # estimate an appropriate angle for the pan servo.
            # assume field of view ~= 60 degrees  (+/- 30 degrees)
            # this assume:
            #    servo_angle command   0 = extreme left (-90 deg)
            #    servo_angle command 255 = extreme right (90 deg)
            servo_angle = int(dx * 30.0 * 0.7 + 128)  # 0.7 = gain

            msg = '\02%02x%02x' % (PAN_SERVO, servo_angle)

            print 'SERVO CMD: ', servo_angle
            #clientsock.send(msg)
            
                    
    #clientsock.close()

if __name__ == '__main__':
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.bind((HOST, PORT))
    serversock.listen(BACKLOG)

    while True:
        print 'waiting for connection...'
        clientsock, addr = serversock.accept()
        print '...connected from:', addr
        thread.start_new_thread(handler, (clientsock, addr))



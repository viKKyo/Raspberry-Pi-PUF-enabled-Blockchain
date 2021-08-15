#! /bin/sh

#sshpass -p 'raspberry' scp ./pufTrusted.py pi@192.168.100.102:/home/pi/masters
sshpass -p 'raspberry' scp ./pufUntrusted.py pi@192.168.100.102:/home/pi/masters

sleep 2

#sshpass -p 'raspberry' scp ./pufTrusted.py pi@192.168.100.103:/home/pi/masters
sshpass -p 'raspberry' scp ./pufUntrusted.py pi@192.168.100.103:/home/pi/masters

sleep 2

#sshpass -p 'raspberry' scp ./pufTrusted.py pi@192.168.100.104:/home/pi/masters
sshpass -p 'raspberry' scp ./pufUntrusted.py pi@192.168.100.104:/home/pi/masters

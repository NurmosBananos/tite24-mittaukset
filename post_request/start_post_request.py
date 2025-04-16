#!/bin/sh
### BEGIN INIT INFO
# Provides:          start_post_request
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start post_request.py on boot
# Description:       Launches the Python script on startup
### END INIT INFO

case "$1" in
  start)
    echo "Starting post_request.py"
    /usr/bin/python3 /home/palju/IOT/post_request.py &
    ;;
  stop)
    echo "Stopping post_request.py"
    pkill -f /home/palju/IOT/post_request.py
    ;;
  *)
    echo "Usage: /etc/init.d/start_post_request {start|stop}"
    exit 1
    ;;
esac

exit 0
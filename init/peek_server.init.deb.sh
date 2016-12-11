#!/bin/sh
 
### BEGIN INIT INFO
# Provides:          peek_server
# Required-Start:    $remote_fs $syslog postgresql
# Required-Stop:     $remote_fs $syslog postgresql
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: peek_server, Extensible Model Viewer
# Description:       peek_server, Extensible Model Viewer
### END INIT INFO

# Change the next 3 lines to suit where you install your script and what you want to call it
HOME=/home/peek
DIR=${HOME}/peek
DAEMON="$DIR/peek_server.pyc"
DAEMON_NAME=peek

# This next line determines what user the script runs as.
DAEMON_USER=peek

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

# Add the python paths
export PYTHONPATH=$DIR
export PATH=${HOME}/python/bin:$PATH


# Rotate Logs
LOG=$HOME/peek.log
[ -f ${LOG}.1 ] && mv ${LOG}.1 ${LOG}.2
[ -f ${LOG} ] && mv ${LOG} ${LOG}.1


do_start () {
    log_daemon_msg "Starting system $DAEMON_NAME daemon"
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas /bin/bash -- -c "exec python -u $DAEMON > ${LOG} 2>&1"
    log_end_msg $?
}
do_stop () {
    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}
 
case "$1" in
 
    start|stop)
        do_${1}
        ;;
 
    restart|reload|force-reload)
        do_stop
        do_start
        ;;
 
    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;

    *)
        echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
        exit 1
        ;;
 
esac
exit 0



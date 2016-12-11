#!/bin/sh
#
# Peek - Extensible Model Viewer
#
# chkconfig:   2345 20 80
# description: Peek - Extensible Model Viewer
#

### BEGIN INIT INFO
# Provides: peek_server
# Required-Start: sshd postgresql
# Required-Stop: sshd postgresql
# Should-Start:
# Should-Stop:
# Default-Start: 3 4 5
# Default-Stop: 0 1 2 6
# Short-Description: Peek - Extensible Model Viewer
# Description: Peek - Extensible Model Viewer
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

HOME=/home/peek
DIR=${HOME}/peek
DAEMON="$DIR/peek_server.pyc"
DAEMON_NAME=peek
DAEMON_USER=peek
PYTHON=${HOME}/python/bin/python

# Change the next 3 lines to suit where you install your script and what you want to call it
exec="$DAEMON"
prog="$DAEMON_NAME"


[ -e /etc/sysconfig/$prog ] && . /etc/sysconfig/$prog

lockfile=/var/lock/subsys/$prog

# Add the python paths
export PYTHONPATH=$DIR
export PATH=${HOME}/python/bin:$PATH

start() {
    echo -n $"Starting $prog: "
    # if not running, start it up here, usually something like "daemon $exec"
    su - $DAEMON_USER -c "$PYTHON $DAEMON >> $HOME/peek_server.log 2>&1 &" && success || failure

    retval=$?
    echo
    [ $retval -eq 0 ] && touch $lockfile
    return $retval
}

stop() {
    echo -n $"Stopping $prog: "
    # stop it here, often "killproc $prog"
    killproc $PYTHON
    retval=$?
    echo
    [ $retval -eq 0 ] && rm -f $lockfile
    return $retval
}

restart() {
    stop
    start
}

rh_status() {
    # run checks to determine if the service is running or use generic status
    status $prog
}

rh_status_q() {
    rh_status >/dev/null 2>&1
}


case "$1" in
    start)
        rh_status_q && exit 0
        $1
        ;;
    stop)
        rh_status_q || exit 0
        $1
        ;;
    restart)
        $1
        ;;
    status)
        rh_status
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart}"
        exit 2
esac
exit $?


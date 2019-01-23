#!/bin/sh

cd `dirname $0`

RSYNC="rsync --exclude=*-eps-converted-to.pdf --exclude=.FBCIndex --exclude=.FBCLockFolder/ --exclude=.DS_Store --exclude=.git/ --exclude=.svn/ --exclude=python2.7 --exclude=python3.6m --exclude=.Python --exclude=bin/ --exclude==include/ --exclude=lib/ --exclude=__pycache__/ --exclude=patches/"' --exclude=*.pyc --exclude=*/*.pyc'" -avrz ${@:2}"
SSH="ssh"

case "$1" in
    up)
	src=./
	dst=flab-pc:/home/ishida/follow_vehicle_sensing
	SSH=ssh
	;;
    down)
	src=flab-pc:/home/ishida/follow_vehicle_sensing
	dst=./
	SSH=ssh
	;;
    *)
	echo "Usage: $0 {up|down} [<rsync-option1> <rsync-option2> ...]"
	exit 1
	;;
esac

${RSYNC} -e "${SSH}" ${src} ${dst}

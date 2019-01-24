#!/bin/sh

cd `dirname $0`

RSYNC="rsync --exclude=*-eps-converted-to.pdf --exclude=.FBCIndex --exclude=.FBCLockFolder/ --exclude=.DS_Store --exclude=.git/ --exclude=.svn/ --exclude=python2.7 --exclude=python3.6m --exclude=.Python --exclude=bin/ --exclude==include/ --exclude=lib/ --exclude=__pycache__/ --exclude=patches/"' --exclude=*.pyc --exclude=*/*.pyc'" -avrz ${@:2}"
SSH="ssh"

case "$1" in
    up)
	src=./
	dst=destpc:/path/to/dir/
	SSH=ssh
	;;
    down)
	src=destpc:/path/to/dir/
	dst=./
	SSH=ssh
	;;
    *)
	echo "Usage: $0 {up|down} [<rsync-option1> <rsync-option2> ...]"
	exit 1
	;;
esac

${RSYNC} -e "${SSH}" ${src} ${dst}

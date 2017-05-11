#!/bin/bash

# TODO: virtualenv

APP_DIR=$PWD
GIT_DIR=${APP_DIR}/discordion.git
GIT_URL=https://github.com/davidsluo/discordion.git
PYTHON=python3.6

POST_RECEIVE_SCRIPT='#!/bin/bash
git --work-tree=${APP_DIR} --git-dir=${GIT_DIR} checkout -f
./$0 -r'

function init_git() {
     git clone --bare ${GIT_URL} ${GIT_DIR}
     printf ${POST_RECEIVE_SCRIPT} ${APP_DIR} ${GIT_DIR} > ${GIT_DIR}/hooks/post-receive
     chmod +x ${GIT_DIR}/hooks/post-receive
     git --work-tree=${APP_DIR} --git-dir=${GIT_DIR} checkout -f
}

# Start the bot
# If $1 is true, will try to SIGINT current instance and start a new one
# If $2 is true, then will use SIGKILL instead.
# If $3 is true, then will run in foreground.
function start() {
    if [ $1 == true ]; then
        pid=$(ps aux | grep -v grep | grep "$PYTHON ${APP_DIR}/bot.py" | awk '{ print $2 }')
        if [ $2 == true ]; then
            kill -s SIGKILL ${pid}
        else
            kill -s SIGINT ${pid}
        fi

        wait ${pid}
    fi

    if [ $3 == true ]; then
        ${PYTHON} ${APP_DIR}/bot.py
    else
        nohup ${PYTHON} ${APP_DIR}/bot.py &
    fi
}

restart=false
foreground=false
kill_=false
init=false

while getopts ":rfki" opt; do
    case ${opt} in
        r)
            restart=true
            ;;
        f)
            foreground=true
            ;;
        k)
            kill_=true
            ;;
        i)
            init=true
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            ;;
    esac
done

if [ ${init} == true ]; then
    init_git
elif [ ! -d ${GIT_DIR} ]; then
    echo "Git directory not initialized. Rerun with -i to initialize."
    exit 1
else
    start ${restart} ${kill_} ${foreground}
fi

exit 0

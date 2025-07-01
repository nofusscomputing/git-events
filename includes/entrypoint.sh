#!/bin/sh

set -e

if [ $# -eq 0 ]; then

    cd ${HOME};

    ansible-rulebook \
        -r nofusscomputing.git_events.${GIT_EVENT_RULEBOOK_NAME} \
        --env-vars GIT_EVENT_RULEBOOK_PORT,GIT_EVENT_RULEBOOK_TOKEN \
        -v;

else

  exec "$@"

fi

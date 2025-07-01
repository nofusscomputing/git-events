#!/bin/sh

set -e

if [ $# -eq 0 ]; then

    cd ${HOME};

    ansible-rulebook \
        -r nofusscomputing.git_events.${GIT_EVENT_RULEBOOK_NAME} \
        --env-vars PROBLEM_MATCHER_PORT,PROBLEM_MATCHER_TOKEN \
        -v;

else

  exec "$@"

fi


FROM python:3.11-alpine3.22 AS Build


RUN apk update; \
    apk add \
        build-base \
        gcc;


RUN pip install --upgrade \
    setuptools \
    wheel


RUN apk add openjdk21-jdk;


RUN apk add \ 
    alpine-sdk \
    libffi-dev \
    maven \
    build-base libc-dev;


ENV JAVA_HOME /usr/lib/jvm/java-21-openjdk

# ChatGPT suggestion to fix alpine version >3.19
ENV CFLAGS "-Wno-incompatible-pointer-types"


COPY requirements.txt /tmp/requirements.txt


RUN mkdir -p /tmp/python_modules; \
  cd /tmp/python_modules; \
  pip download --dest . \
    pip \
    --check-build-dependencies \
    -r /tmp/requirements.txt


RUN cd /tmp/python_modules; \
  mkdir -p /tmp/python_builds; \
  echo "[DEBUG] PATH=$PATH"; \
  ls -l; \
  pip wheel --wheel-dir /tmp/python_builds --find-links . *.whl; \
  pip wheel --wheel-dir /tmp/python_builds --find-links . *.tar.gz;



FROM python:3.11-alpine3.22


RUN apk --no-cache update; \
    apk --no-cache add \
    openjdk21-jdk


ENV ANSIBLE_FORCE_COLOR true

ENV ANSIBLE_INVENTORY hosts.yaml

ENV JAVA_HOME /usr/lib/jvm/java-21-openjdk


COPY includes/ /

COPY . /home/eda/.ansible/collections/ansible_collections/nofusscomputing/git_events/

COPY --from=build /tmp/python_builds /tmp/python_builds


RUN pip install --no-cache-dir /tmp/python_builds/*; \
    rm -R /tmp/python_builds; \
    ansible-galaxy collection install ansible.eda; \
    addgroup eda; \
    adduser -D --ingroup eda eda; \
    cp -r /root/.ansible /home/eda/; \
    rm -rf /home/eda/.ansible/collections/ansible_collections/nofusscomputing/git_events/includes; \
    mv /usr/bin/annotations.py /usr/bin/annotations; \
    chmod +x /usr/bin/annotations; \
    chown eda:eda -R /home/eda;


WORKDIR /home/eda


USER eda


CMD [ \
    "ansible-rulebook", \
    "-r", "nofusscomputing.git_events.webhook", \
    "--env-vars", "PROBLEM_MATCHER_PORT,PROBLEM_MATCHER_TOKEN", \
    "-v" \
]

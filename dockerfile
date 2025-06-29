FROM harbor.earth.nww/docker/python:3.11-slim


RUN apt-get update; \
    apt-get install -y \
        curl \
        openjdk-17-jdk-headless; \
    pip install ansible-core ansible-rulebook;

RUN addgroup eda; \
    adduser --ingroup eda eda

# COPY extensions/eda/rulebooks/webhook.yaml /eda/

RUN ansible-galaxy collection install ansible.eda

# RUN ls -la /home/eda/.ansible/collections/nofusscomputing/git_events/

COPY . /home/eda/.ansible/collections/ansible_collections/nofusscomputing/git_events/

RUN pip install --no-cache-dir -r /home/eda/.ansible/collections/ansible_collections/nofusscomputing/git_events/requirements.txt

COPY includes/ /

RUN cp -r /root/.ansible /home/eda/; \
    # cp -r /home/eda/.ansible/collections/ansible_collections/nofusscomputing/git_events/includes/* /; \
    rm -rf /home/eda/.ansible/collections/ansible_collections/nofusscomputing/git_events/includes; \
    mv /usr/bin/annotations.py /usr/bin/annotations; \
    chmod +x /usr/bin/annotations; \
    chown eda:eda -R /home/eda;

WORKDIR /home/eda

ENV ANSIBLE_INVENTORY hosts.yaml

# required for parser script

USER eda

CMD [ \
    "ansible-rulebook", \
    "-r", "nofusscomputing.git_events.webhook", \
    "--env-vars", "PROBLEM_MATCHER_PORT,PROBLEM_MATCHER_TOKEN", \
    "-v" \
]
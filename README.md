# No Fuss Computings Git[ea/hub] Event Processing

Documentation for the collection.


## TL;DR

| Name | required | Description |
|:---:|:---:|:---|
| GIT_API_TOKEN | :white_check_mark: | API token to access Git[ea/hub] to post PR Review. |
| GIT_API_URL | :white_check_mark: | API URL to access Git[ea/hub]. To create random one `echo $(head -c 50 /dev/urandom | xxd -p | head -c 50)` |
| GIT_INTERNAL_API_URL | :x: | An internal URL to use in place of the public API URL. i.e. DMZ url. |
| GIT_EVENT_RULEBOOK_TOKEN | :white_check_mark: | The token to set for the inbound connection to the container. |
| GIT_EVENT_RULEBOOK_PORT | :x: | The port to listen for inbound webhooks. Defaults to 5000 |
| ENABLE_DEBUG_LOGGING | :x: | Turn on playbook debug logging. Defaults to `false` :warning: Doing this will output you auth tokens to the log. |


### Steps

1. deploy somewhere that git[ea/hub] has access to the container
1. ensure vars above are set within the container
1. **Gor Gitea** Go to `Site ADministration -> Integrations-> Webhooks`
    1. Add a system webhook
    1. set the http url to the container ip/dns name. ensure port is specifed. suffic `:<port number>`
    1. select `Trigger On -> Workflow Jobs`
    1. set `Authorization Header` to `Bearer <actual value of GIT_EVENT_RULEBOOK_TOKEN>`
    1. click `Update Webhook` to save
1. you are now GTG and all jobs will get posted to the container for processing.


### Setup Parsing of matchers

1. Ansible Lint

    1. before pylint runs, ensure the following commands are executed in your workflow.

    ``` bash

    echo "NFC_PROBLEM_MATCHER_TYPE=pylint-json";

    ```

    1. the output format for pylint is json. i.e. `ansible-lint -f json .`

1. Parsing normal GitHub Problem matchers

    1. Before the job runs, give the matcher a name, no spaces, only letters and can have `-` and `_`

    ``` bash

    echo "NFC_PROBLEM_MATCHER_TYPE=My-Job-Name";

    ```

    1. now run the job that outputs in standrd Github style problem matchers.

1. Now the user will have a PR reviews done with the contents of the problem matcher(s) as review comments.

#!/usr/bin/env python

import sys
import re
import json
# import requests
import os



def default_matcher( entry, tool_name = '' ) -> dict:

    if tool_name == 'default':
        tool_name = ''
    else:

        tool_name = tool_name + ' '

    filename = str(entry['file'])

    msg_type = str(entry['type']).upper()

    # if msg_type in type_count:

    #     type_count[msg_type] += 1

    # else:

    #     type_count[msg_type] = 1

    if filename.startswith('./'):

        filename = str(entry['file'])[2:]

    admonition_level = 'NOTE'
    if msg_type in [ 'ERROR' ]:

        admonition_level = 'IMPORTANT'


    elif msg_type in [ 'WARNING' ]:

        admonition_level = 'WARNING'


    body =str (
        f"> [!{admonition_level}]"
        "\n>"
        f"\n> **{tool_name}Severity:** _{str(msg_type).lower()}_ "
        f"\n> **file**: _{filename}_ "
        f"**Line**: _{str(entry['line'])}_ **Column**: _{str(entry['column'])}_"
        "\n>"
        f"\n> {str(entry['text'])}"
        "\n>"
    )

    return {
        "body": body,
        "new_position": int(entry['line']),
        "old_position": 0,
        "path": filename
    }



def pylint_matcher( entry ) -> dict:

    if not entry.get('line', int(1)):

        comment_line = 1

    else:

        comment_line = int(entry.get('line', int(1)))

    severity = str(entry['severity']).lower()
    admonition_level = 'NOTE'

    if severity in [ 'major' ]:

        admonition_level = 'IMPORTANT'

    if severity in [ 'minor' ]:

        admonition_level = 'WARNING'

    body = str(
            f"> [!{admonition_level}] "
            f"\n> "
            f"\n>**PyLint Severity**: {severity} "
            f"\n>**file**: _{entry['path']}_ "
            f"**Line**: _{entry.get('line', 0)}_ "
            f"\n>"
            f"\n> [{entry['check_name']}]({entry['url']}): {entry['description']} "
            f"\n>"
        )


    if(
        entry.get('body', '') != 'None'
        and entry.get('body', '') != ''
        and entry.get('body', '') is not None
    ):

        body = body + str(
            f"\n>_{entry.get('body', '')}_ "
            f"\n>"
        )


    return {
        "body": body,
        "new_position": comment_line,
        "old_position": 0,
        "path": str(entry['path'])
    }






regex = {

    "default": os.getenv("PROBLEM_MATCHER_REGEX",
        r"::(?P<type>\S+)\s+"
        r"(?:file=)(?P<file>.+?),"
        r"(?:line=)(?P<line>\d+),"
        r"(?:col=)(?P<column>\d+).+?"
        # r"\s\[(?P<rule>\S+)]\s(?P<text>.+)"
        r"\s(?P<text>.+)"
    ),

# \{\s*"type":\s*"(?P<type>[^"]+)",\s*"check_name":\s*"(?P<check_name>[^"]+)",\s*"categories":\s*\[(?P<categories>[^\]]*)\],\s*"url":\s*"(?P<url>[^"]+)",\s*"severity":\s*"(?P<severity>[^"]+)",\s*"description":\s*"(?P<description>[^"]+)",\s*"fingerprint":\s*"(?P<fingerprint>[^"]+)",\s*"location":\s*\{\s*"path":\s*"(?P<path>[^"]+)"(?:,\s*"lines":\s*\{\s*"begin":\s*(?P<line>\d+)\})?.*?\}},(?:\s"content":\s\{"body":\s"(?P<body>.+?)")?
    "pylint-json": str(
        # r'\{\s*"type":\s*"(?P<type>[^"]+)",\s*'
        # r'"check_name":\s*"(?P<check_name>[^"]+)",\s*'
        # r'"categories":\s*\[(?P<categories>[^\]]*)\],\s*'
        # r'"url":\s*"(?P<url>[^"]+)",\s*'
        # r'"severity":\s*"(?P<severity>[^"]+)",\s*'
        # r'"description":\s*"(?P<description>[^"]+)",\s*'
        # r'"fingerprint":\s*"(?P<fingerprint>[^"]+)",\s*'
        # r'"location":\s*\{\s*"path":\s*"(?P<path>[^"]+)'
        # # r'"(?:,\s*"lines":\s*\{\s*"begin":\s*(?P<line>\d+)\})?.*?\}},'
        # r'(?:(?:,\s*"lines":\s*\{\s*"begin":\s*)|(?:{"line":\s))(?P<line>\d+)?.*?\}},'
        # r'(?:\s"content":\s\{"body":\s"(?P<body>.+?)")?'

        # \{\s*"type":\s*"(?P<type>[^"]+)",\s*"check_name":\s*"(?P<check_name>[^"]+)",\s*"categories":\s*\[(?P<categories>[^\]]*)\],\s*"url":\s*"(?P<url>[^"]+)",\s*"severity":\s*"(?P<severity>[^"]+)",\s*"description":\s*"(?P<description>[^"]+)",\s*"fingerprint":\s*"(?P<fingerprint>[^"]+)",\s*"location":\s*\{\s*"path":\s*"(?P<path>[^"]+)".+?"line[s]?":.+?(?P<line>\d+)?.*?\}},(?:\s"content":\s\{"body":\s"(?P<body>.+?)")?

        r'\{\s*"type":\s*"(?P<type>[^"]+)",\s*'
        r'"check_name":\s*"(?P<check_name>[^"]+)",\s*'
        r'"categories":\s*\[(?P<categories>[^\]]*)\],\s*'
        r'"url":\s*"(?P<url>[^"]+)",\s*'
        r'"severity":\s*"(?P<severity>[^"]+)",\s*'
        r'"description":\s*"(?P<description>[^"]+)",\s*'
        r'"fingerprint":\s*"(?P<fingerprint>[^"]+)",\s*'
        r'"location":\s*\{\s*"path":\s*"(?P<path>[^"]+)".+?'
        r'"line[s]?":.+?(?P<line>\d+).*?\}},'
        r'(?:\s"content":\s\{"body":\s"(?P<body>.+?)")?'
    )
}



results = {}

NFC_PROBLEM_MATCHER = False

pull_request: int = None

matcher = re.compile(r'NFC_PROBLEM_MATCHER=(?P<pull_number>\d+)')
matcher_type = re.compile(r'NFC_PROBLEM_MATCHER_TYPE=(?P<type>[a-zA-Z_-]+)')

regex_type = 'default'
pattern = re.compile( regex[regex_type] )
matcher_name = 'Default Matcher'

for line in sys.stdin:

    match_matcher_type = matcher_type.search(line)

    if match_matcher_type:
        regex_type = match_matcher_type['type']
        matcher_name = match_matcher_type['type']

        if regex_type in regex:

            pattern = re.compile( regex[regex_type] )

        else:

            pattern = re.compile( regex['default'] )

    match = pattern.finditer(line)

    problem_matcher = matcher.search(line)

    if problem_matcher:

        NFC_PROBLEM_MATCHER = True

        pull_request = int(problem_matcher['pull_number'])


    if match:

        if matcher_name not in results:
            results[matcher_name] = []


        for obj in match:

            results[matcher_name].append(obj.groupdict())



if not NFC_PROBLEM_MATCHER:

    sys.exit(2)


if not results:
    print("No matching lines found.")
    sys.exit(0)


api_body: dict = {
  "body": "boo",
  "comments": [],
  "commit_id": os.getenv("GITHUB_SHA"),
  "event": "REQUEST_CHANGES"
}


type_count = {}

for tool, tool_results in results.items():

    for entry in tool_results:

        if tool == 'pylint-json':

            api_body['comments'] += [ pylint_matcher( entry ) ]

        else:

            api_body['comments'] += [ default_matcher( entry, tool_name = tool ) ]

        if tool not in type_count:

            type_count[tool] = 1

        else:

            type_count[tool] += 1


review_body = {
    'header': str(
        '## :no_entry_sign: Annotations found \n' \
        f'@{os.getenv("GITHUB_ACTOR")}, \n\n'
        'I found some issues that need addressing. \n\n'
    )
}

for msg_type, cnt in type_count.items():

    if msg_type not in review_body:

        review_body[msg_type] = str('| Type | Count | \n|:---|:---:| \n')

    review_body[msg_type] += f'| {msg_type} | {cnt} | \n'


api_body['body'] = review_body['header']

for msg_type, value in review_body.items():

    if msg_type != 'header':

        api_body['body'] += str(
            f'### {msg_type} issues found '
            '\n'
            f'{value}\n'
            '\n'
        )


data = {
    "pull_request": pull_request,
    "api_body": api_body
}

print(json.dumps(data, indent=4))


# URL = os.getenv("GITHUB_API_URL") + '/repos/' + os.getenv("GITHUB_REPOSITORY") + '/pulls/' + os.getenv("GITHUB_REF_NAME") + '/reviews?token=' + str(os.getenv("AGITHUB_TOKEN"))
# try:
#     response = requests.post(URL, json=api_body)
#     response.raise_for_status()
#     print(f"\n✅ Successfully posted to {URL}")
#     print(f"🔁 Server responded with: {response.status_code} {response.reason}")
# except requests.exceptions.RequestException as e:
#     print(f"\n❌ Failed to post to {URL}")
#     print(f"Error: {e}")
#     sys.exit(1)

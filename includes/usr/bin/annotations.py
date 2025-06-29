#!/usr/bin/env python

import sys
import re
import json
# import requests
import os

# Setup CLI argument parsing
# parser = argparse.ArgumentParser(description="Parse input and POST to API.")
# parser.add_argument("url", nargs="?", help="API endpoint URL", default=os.getenv("API_URL"))
# args = parser.parse_args()

# if not args.url:
#     print("❌ Error: API endpoint URL must be provided as an argument or via the API_URL environment variable.")
#     sys.exit(1)


def default_matcher( entry ) -> dict:


    filename = str(entry['file'])

    msg_type = str(entry['type']).upper()

    if msg_type in type_count:

        type_count[msg_type] += 1

    else:

        type_count[msg_type] = 1

    if filename.startswith('./'):

        filename = str(entry['file'])[2:]

    body = f"> [!NOTE]\n>\n> **{msg_type} in file: {filename}** " \
        f"_Line: {str(entry['line'])} Column: {str(entry['column'])}_" \
        f"\n>\n> _{str(entry['text'])}_\n>"

    if msg_type in [ 'ERROR' ]:



        body = f"> [!IMPORTANT]\n>\n> **{msg_type} in file: {filename}** " \
            f"_Line: {str(entry['line'])} Column: {str(entry['column'])}_" \
            f"\n>\n> _{str(entry['text'])}_\n>"

    elif msg_type in [ 'WARNING' ]:

        body = f"> [!WARNING]\n>\n> **{msg_type} in file: {filename}** " \
            f"_Line: {str(entry['line'])} Column: {str(entry['column'])}_" \
            f"\n>\n> _{str(entry['text'])}_\n>"

    return {
        "body": body,
        "new_position": int(entry['line']),
        "old_position": 0,
        "path": filename
    }



def pylint_matcher( entry ) -> dict:

    # print(f'{entry}')

    # annotation = {}

    if not entry.get('line', int(1)):

        comment_line = 1

    else:

        comment_line = int(entry.get('line', int(1)))

    return {
        "body": str(
            f"> [!IMPORTANT] \n"
            f"\n> "
            f"\n>**{entry['severity']} in file: {entry['path']}**"
            f"_Line: {entry.get('line', 0)}_ "
            f"\n>"
            f"\n> [{entry['check_name']}]({entry['url']}): {entry['description']} "
            f"_{entry.get('body', '')}_ "
            f"\n>"
        ),
        "new_position": comment_line,
        "old_position": 0,
        "path": str(entry['path'])
    }






# Yaml Lint
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


# tool_name = os.getenv("PROBLEM_MATCHER_TOOL_NAME", '')
# What level to fail on

# Regex pattern


results = {}

NFC_PROBLEM_MATCHER = False

pull_request: int = None

matcher = re.compile(r'NFC_PROBLEM_MATCHER=(?P<pull_number>\d+)')
matcher_type = re.compile(r'NFC_PROBLEM_MATCHER_TYPE=(?P<type>[a-z_-]+)')

regex_type = 'default'
pattern = re.compile( regex[regex_type] )
# Read and parse lines
for line in sys.stdin:


    match_matcher_type = matcher_type.search(line)

    if match_matcher_type:
        regex_type = match_matcher_type['type']
        pattern = re.compile( regex[regex_type] )



    # print(f'matcher type is {regex_type}')


    match = pattern.finditer(line)

    problem_matcher = matcher.search(line,)

    if problem_matcher:

        NFC_PROBLEM_MATCHER = True

        pull_request = int(problem_matcher['pull_number'])

    if match:

        # print(f'was match: {match}')

        if regex_type not in results:
            results[regex_type] = []

        # print(match.groupdict())

        for obj in match:

            # print(f'obj: {obj}')

            results[regex_type].append(obj.groupdict())


if not NFC_PROBLEM_MATCHER:

    sys.exit(2)

if not results:
    print("No matching lines found.")
    sys.exit(0)

# Output JSON locally for visibility
# print("Parsed JSON:")
# print(json.dumps(results, indent=2))

api_body: dict = {
  "body": "boo",
  "comments": [
    # {
    #   "body": "[line-length] line too long (96 > 80 characters) - 7",
    #   "new_position": 22,
    #   "old_position": 0,
    #   "path": "Application-alert-manager.yaml"
    # }
  ],
  "commit_id": os.getenv("GITHUB_SHA"),
  "event": "REQUEST_CHANGES"
}

# Send to API

type_count = {}

for tool, tool_results in results.items():

    for entry in tool_results:

        if tool == 'default':

            api_body['comments'] += [ default_matcher( entry ) ]

        elif tool == 'pylint-json':

            api_body['comments'] += [ pylint_matcher( entry ) ]


review_body = '## :no_entry_sign: Annotations found\n\n' \
    f'@{os.getenv("GITHUB_ACTOR")}, found some issues.\n\n' \
    '| Type | Count | \n|:---|:---:| \n'

for msg_type, cnt in type_count.items():

    review_body += f'| {msg_type} | {cnt} | \n'


api_body['body'] = review_body + '\n'

data = {
    "pull_request": pull_request,
    "api_body": api_body
}

print(json.dumps(data))


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

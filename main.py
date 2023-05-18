# This is a sample Python script.
import json
import os
import requests
from bs4 import BeautifulSoup
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
token = os.getenv('GITHUB_TOKEN')

data = {
    'repo': 'vuejs/vue',
    'stars': 179271,
    'language': 'JavaScript',
    'note_url': 'https://github.com/vuejs/vue/releases/tag/v2.6.8',
    'commits_url': 'https://github.com/vuejs/vue/compare/v2.6.7...v2.6.8'
}

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

# Github API base URL
base_url = 'https://api.github.com/repos/'


# Get commit diffs
commits_url = data['commits_url'].replace('https://github.com/', base_url) + '.diff'
headers["Accept"] = "application/vnd.github.diff"
response = requests.get(commits_url, headers=headers)

# Check if request was successful
if response.status_code == 200:
    diff = response.text
else:
    diff = 'Could not fetch data'

# Get release notes
note_url = data['note_url']
response = requests.get(note_url)

# Check if request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    notes = soup.find('div', {'class': 'markdown-body'}).get_text()
else:
    notes = 'Could not fetch data'

# Prepare data for JSON
data_point = {
    'repo': data['repo'],
    'stars': data['stars'],
    'language': data['language'],
    'release_notes': notes,
    'commits': diff.split('\n\n')
}

# Save data to JSON file
with open('data.json', 'w') as file:
    json.dump(data_point, file, indent=4)
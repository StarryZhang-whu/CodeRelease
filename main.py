import json
import os
import requests
from bs4 import BeautifulSoup

# configure GitHub api
token = os.getenv('GITHUB_TOKEN')
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}
base_url = 'https://api.github.com/repos/'

with open('versions.jsonl', 'r') as f:
    versions = list(map(json.loads, f.readlines()))

results = []


def get_diff(repo, start_sha, end_sha):
    diff_url = f"https://api.github.com/repos/{repo}/compare/{start_sha}...{end_sha}"
    headers["Accept"] = "application/vnd.github.diff"
    _response = requests.get(diff_url, headers=headers)

    if _response.status_code == 200:
        return _response.text
    else:
        return None


for data in versions:
    # 获取版本的提交信息
    commit_url = data['commits_url'].replace('compare', 'commits')
    commits_data = requests.get(commit_url, headers=headers).json()

    # 获取版本之间的所有commit
    commits = []
    if commits_data and 'commits' in commits_data:
        for i in range(1, len(commits_data['commits'])):
            commit_info = {'sha': commits_data['commits'][i]['sha'], 'commit_message': commits_data['commits'][i]['commit']['message']}
            diff = get_diff(data['repo'], commits_data['commits'][i-1]['sha'], commits_data['commits'][i]['sha'])
            commit_info['diff'] = diff
            commits.append(commit_info)

    # 获取版本的发布说明
    response = requests.get(data['note_url'])
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        notes = soup.find('div', {'class': 'markdown-body'}).get_text()
    else:
        notes = 'Could not fetch data'

    # 构建结果数据
    result = {
        'repo': data['repo'],
        'stars': data['stars'],
        'language': data['language'],
        'release_notes': notes,
        'commits': commits
    }
    results.append(result)

# 将结果保存到新的jsonl文件中
with open('data/results.jsonl', 'w') as f:
    for result in results:
        f.write(json.dumps(result))
        f.write('\n')

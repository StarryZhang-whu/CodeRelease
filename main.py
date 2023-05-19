import json
import os
import requests
from bs4 import BeautifulSoup

# configure GitHub api
token = os.environ.get('GITHUB_TOKEN')
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
    headers["Accept"] = "application/vnd.github.v3+json"
    # 获取版本的提交信息
    commit_url = data['commits_url'].replace('https://github.com/', 'https://api.github.com/repos/')
    print("Now request:", commit_url)
    response = requests.get(commit_url, headers=headers)
    # commits_data = requests.get(commit_url, headers=headers).json()
    commits = []
    if response.status_code == 200:
        print("Request commits success")
        # 获取版本之间的所有commit
        try:
            commits_data = response.json()
        except json.decoder.JSONDecodeError as e:
            print("Failed to decode JSON: ", e)
            print("Response: ", response.text)
            continue
        print("Json parser success")
        raw_commits = commits_data['commits']
        for i in range(1, len(raw_commits)):
            commit_info = {'sha': raw_commits[i]['sha'], 'commit_message': raw_commits[i]['commit']['message']}
            diff = get_diff(data['repo'], raw_commits[i - 1]['sha'], raw_commits[i]['sha'])
            commit_info['diff'] = diff
            commits.append(commit_info)
    else:
        print("Error: ", response.status_code)
    # 获取版本的发布说明
    response = requests.get(data['note_url'], headers=headers)
    if response.status_code == 200:
        print("Request release notes success")
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

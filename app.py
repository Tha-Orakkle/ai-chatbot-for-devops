from flask import Flask, jsonify, request
from integration_config import integration_config
from transformers import pipeline

import io, requests, zipfile

# only provess request when it starts with /devops
# return a immediate response that request is processing 
# and continue to prorcess reqyuest asynchronously  


app = Flask(__name__)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
labels = [
    "CI/CD Pipeline Issues",
    "Build Failures",
    "Deployment Issues",
    "Testing Failures",
    "GitHub Actions",
    "Pipeline Configuration",
    "Environment Setup",
    "Continuous Monitoring",
    "API Integration",
    "Version Control Issues",
    "Artifact Deployment",
    "Code Review Issues",
    "Automation & Scripting",
    "Performance/Speed",
    "Secrets Management",
    "Docker/Container Issues",
    "Notification/Alerts",
    "Infrastructure as Code (IaC)",
    "Caching Issues",
    "Access Control and Permissions"
]


# classifies the request text
def classify_query(text):
    result = classifier(text, labels)
    top_label = result['labels'][0]
    score = result['score'][0]
    return top_label, score

# decompress and extract log
def extract_log_content(content):
    zip_file = zipfile.ZipFile(io.BytesIO(content))
    with open(zip_file.extract('0_deploy.txt'), 'r') as f:
        log_content = f.readlines()
    return log_content[-20:]



# fetch workflow run log from github
def fetch_github_logs(owner, repo, token):
    if not repo:
        return None
    
    gh_api_url = "https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {'Authorization': f'token {token}'}

    response = requests.get(gh_api_url, headers=headers)
    if response.status_code != 200:
        return None

    runs = response.json().get('workflow_runs', [])
    if not runs:
        return None
    run_id = runs[0]['id']
    logs_url = gh_api_url + f"/{run_id}/logs"
    log_response = requests.get(logs_url, headers=headers)
    if log_response != 200:
        return None
    return extract_log_content(response.content)
    

# ROUTES

# handles request to the integration specification
@app.route('/integration.json', methods=['GET'])
def get_integration_config():
    return jsonify(integration_config)


# handles the request from telex
@app.route('/webhook', methods=['POST'])
def request_handler():
    data = request.get_json()
    print(data)
    text = data.get('message')
    label, score = classify_query(text)
    if label == "Github Actions" and score > 0.85:
        owner = data['settings'].get('github_owner', None)
        repo = data['settings'].get('github_repo', None)
        pat = data['settings'].get('github_PAT', None)
        github_logs = fetch_github_logs(owner, repo, pat)
        if not github_logs:
            return jsonify({'result': 'couldnt generate github logs'})
         


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
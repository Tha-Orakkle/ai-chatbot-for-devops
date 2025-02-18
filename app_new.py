from flask import Flask, jsonify, request
from integration_config import integration_config
from transformers import pipeline

from helpers import fetch_github_logs

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


# ROUTES

# handles request to the integration specification
@app.route('/integration.json', methods=['GET'])
def get_integration_config():
    return jsonify(integration_config)


# handles the request from telex
@app.route('/webhook', methods=['POST'])
def request_handler():
    data = request.data
    text = data.get('message')
    label, score = classify_query(text)
    if label == "Github Actions" and score > 0.85:
        owner = data['settings'].get('github_owner', None)
        repo = data['settings'].get('github_repo', None)
        pat = data['settings'].get('github_PAT', None)
        fetch_github_logs(owner, repo, pat)
         


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
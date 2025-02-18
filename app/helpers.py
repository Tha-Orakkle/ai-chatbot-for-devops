from flask import jsonify

import io
import aiohttp
import zipfile
import os

from . import classifier

labels = [
    "CI/CD Pipeline Issues", "Build Failures", "Deployment Issues",
    "Testing Failures", "GitHub Actions", "Pipeline Configuration",
    "Environment Setup", "Continuous Monitoring", "API Integration",
    "Version Control Issues", "Artifact Deployment", "Code Review Issues",
    "Automation & Scripting", "Performance/Speed", "Secrets Management",
    "Docker/Container Issues", "Notification/Alerts", "Infrastructure as Code (IaC)",
    "Caching Issues", "Access Control and Permissions", "Logs"
]

headers = {
    'Content-Type': 'application/json'
}

# classifies the request text
def classify_query(text):
    result = classifier(text, labels)
    top_label = result['labels'][0]
    score = result['scores'][0]
    return top_label, score


# decompress and extract log
def extract_log_content(content):
    zip_file = zipfile.ZipFile(io.BytesIO(content))
    with open(zip_file.extract('0_deploy.txt'), 'r') as f:
        log_content = f.readlines()
        os.remove('0_deploy.txt')
    return "".join(log_content[-20:])

# fetch workflow run log from github
async def fetch_github_logs(owner, repo, token):
    
    gh_api_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {'Authorization': f'token {token}'}

    async with aiohttp.ClientSession() as session:
        print("=========")
        print(owner, repo, token)
        print("=========")
        async with session.get(gh_api_url, headers=headers) as response:
            res_json = await response.json()
            if response.status != 200:
                print(res_json)
                return "failed", res_json.message

            runs = (await response.json()).get('workflow_runs', [])
            if not runs:
                print("You have not made any deployments via github action workflow", runs)
                return "failed", "You have not made any deployments via github action workflow."

            run_id = runs[0]['id']
            logs_url = f"{gh_api_url}/{run_id}/logs"
            async with session.get(logs_url, headers=headers) as log_response:
                if log_response.status != 200:
                    logs_json = await log_response.json()
                    print("Error occured while trying to get logs", logs_json.message)
                    return "failed", logs_json.message

                return "success", extract_log_content(await log_response.read())


async def request_handler(channel_url, text, settings):
    label, score = classify_query(text)
    print("==============label, score============")
    print(label, score)
    print("==============label, score============")
    print(channel_url)
    async with aiohttp.ClientSession() as session:
        print("processing request")
        try:
            async with session.post(
                channel_url,
                headers=headers,
                json={    
                    "username": "bot_devops",
                    "event_name":  "request accepted",
                    "message": "Your request is being processed",
                    "status": "success"
                }) as res:
                    print(res.status, res)
        except Exception as e:
            print(f"An error occured: {e}" )


    if label == "Logs" and score > 0.5:
        owner=settings.get('repo_owner', None)
        repo=settings.get('github_repo', None)
        token=settings.get('github_PAT', None)
        print("==============settings============")
        print(owner, repo, token)
        print("==============settings============")

        if not owner or not repo:
            # Generate AI reponse
            pass

        async with aiohttp.ClientSession() as session:
            await session.post(channel_url, json={
                "username": "bot_devops",
                "event_name":  "fetching log",
                "message": "Fetching log from github",
                "status": "success"

        })

        status, log = await fetch_github_logs(owner, repo, token)
        if status == "failed":
            async with aiohttp.ClientSession() as session:
                await session.post(channel_url, json={
                    "username": "bot_devops",
                    "event_name":  "Log fetch failed",
                    "message": log,
                    "status": "success"
            })

        payload = {
            "username": "bot_devops",
            "event_name":  "Log Check",
            "message": log,
            "status": "success"
        }
        async with aiohttp.ClientSession() as session:
            await session.post(channel_url, json=payload)

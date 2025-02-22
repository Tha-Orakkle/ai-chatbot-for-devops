from flask import jsonify
from google.genai import types
from sentence_transformers.util import cos_sim

import asyncio
import httpx
import io
import os
import zipfile

from . import (
    ai_client,
    classifier,
    sys_instruct,
    model,
    embedding_label,
    nli_hypothesis
)


def classify_query(text):
    """
    checks query if it relates to getting log from github workflow runs
    Args:
        text(string) - query
    """

    embeddings = model.encode([text, embedding_label], convert_to_tensor=True)
    similarity = cos_sim(embeddings[0], embeddings[1])
    score = similarity.item()

    print(f"embedding score: {score}")

    if score >= 0.80:
        return "github_related"
    elif score <= 0.55:
        return "not_github_related"
    else:
        # if text is ambiguous conduct a logical context comparison
        # using an NLI-based model
        nli_result = classifier(text, nli_hypothesis)
        nli_score = nli_result['scores'][0]
        print(f"NLI score: {nli_score}")
        if nli_score >= 0.6:
            return "github_related"
        return "not_github_related"


def extract_log_content(content):
    """
    Extracts log from compressed file
    Args:
        content(bytes) - compressed file
    """
    zip_file = zipfile.ZipFile(io.BytesIO(content))
    with open(zip_file.extract('0_deploy.txt'), 'r') as f:
        log_content = f.readlines()
        os.remove('0_deploy.txt')
    return "".join(log_content[-30:])


async def fetch_github_logs(owner, repo, token):
    """
    Fetches github workflows runs logs

    Args:
        owner(string)- repository owner
        repo(string): repository name
        token(string): read only personal access token
    """

    if not owner or not repo or not token:
        return [
            "failed",
            "Can't fetch log without your repo credentials, please provide " +
            "repo, repo owner and PAT in settings"
        ]

    gh_api_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {'Authorization': f'Bearer {token}'}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(gh_api_url, headers=headers) # gets all runs
        res_json = response.json()

        if response.status_code != 200:
            print(res_json)
            return [
                "failed",
                "Repository not found. Confirm github owner and repo are " +
                "valid in settings"
            ]

        runs = res_json.get('workflow_runs', [])

        if not runs:
            return [
                "failed",
                "You have not made any deployments via github action workflow."
            ]

        run_id = runs[0]['id']

        logs_url = f"{gh_api_url}/{run_id}/logs"
        log_response = await client.get(logs_url, headers=headers) # get run_id-specific log
        print(log_response)
        if log_response.status_code != 200:
            logs_json = log_response.json()
            print("Error occured while trying to get logs", logs_json.message)
            return "failed", logs_json.message

        return "success", extract_log_content(log_response.content)


async def generate_ai_response(text):
    """
    Generates AI response using google's gemini API

    Args:
        text(string) - user input
    """
    response = ai_client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            system_instruction=sys_instruct),
        contents=[text]
    )
    return response.text


async def request_handler(channel_url, text, settings):
    """
    Handles the request by:
        Fetching log from GitHub or generates an AI response

    Args:
        channel_url(string): telex channel webhook url
        text(string): user input
        settings(string): channel settings
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                channel_url,
                headers={"Content-Type": "application/json"},
                json={
                    "username": "bot_devops",
                    "event_name": "request accepted",
                    "message": "Your request is being processed",
                    "status": "success"
                }
            )
            response.raise_for_status()
            print(response)
        except Exception as e:
            print(f"Error in request_handler: {e}")

        query_class = classify_query(text)

        owner = settings.get('repo_owner', None)
        repo = settings.get('github_repo', None)
        token = settings.get('github_PAT', None)

        if query_class == "github_related":
            try:
                await client.post(channel_url, json={
                    "username": "bot_devops",
                    "event_name": "fetching log",
                    "message": "Fetching log from github",
                    "status": "success"
                })
                response.raise_for_status()
            except Exception as e:
                print(f"Error in request_handler: {e}")

            status, log = await fetch_github_logs(owner, repo, token)
            if status == "failed":
                try:
                    await client.post(channel_url, json={
                        "username": "bot_devops",
                        "event_name":  "Log failed to fetch.",
                        "message": log,
                        "status": "success"
                    })
                except Exception as e:
                    print(f"Error in request_handler: {e}")
                return

            payload = {
                "username": "bot_devops",
                "event_name":  "GitHub Log Check",
                "message": log,
                "status": "success"
            }
            await client.post(channel_url, json=payload)
        else:
            ai_response = await generate_ai_response(text)
            await client.post(channel_url, json={
                "username": "bot_devops",
                "event_name":  "bot_devops says",
                "message": ai_response,
                "status": "success"
            })


def call_request_handler_in_thread(channel_url, text, settings):
    """
    creates event loop for the new thread and adds coroutine to the loop.

    Args:
        channel_url(string): telex channel webhook url
        text(string): user input
        settings(string): channel settings
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(request_handler(channel_url, text, settings))
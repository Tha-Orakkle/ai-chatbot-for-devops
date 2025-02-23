from bs4 import BeautifulSoup
from flask import jsonify
from google.genai import types
from sentence_transformers.util import cos_sim

import asyncio
import httpx
import io
import markdown
import os
import zipfile

from . import (
    ai_client,
    classifier,
    embedding_label,
    logger,
    model,
    nli_hypothesis,
    sys_instruct
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
    logger.info(f"Embedding score {score}")
    if score >= 0.80:
        return "github_related"
    elif score <= 0.55:
        return "not_github_related"
    else:
        # if text is ambiguous conduct a logical context comparison
        # using an NLI-based model
        nli_result = classifier(text, nli_hypothesis)
        nli_score = nli_result['scores'][0]
        logger.info(f"NLI score: {nli_score}")
        if nli_score >= 0.6:
            return "github_related"
        return "not_github_related"

def clean_ai_response(text):
    html = markdown.markdown(text)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

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
        runs = None
        try:
            response = await client.get(gh_api_url, headers=headers) # gets all runs
            if response.status_code != 200:
                logger.info(f"GitHub API returned {response.status_code} {response.text}")
                return [
                    "failed",
                    "Please, ensure a valid github owner, repo and token have " +
                    "been provided in the settings."
                ]
            runs = response.json().get('workflow_runs', [])
        except Exception as e:
            logger.info(f"An error occured fetching GitHub Action runs: {e}")
    
        if not runs:
            return [
                "failed",
                "You have not made any deployments via github action workflow."
            ]

        run_id = runs[0]['id']

        logs_url = f"{gh_api_url}/{run_id}/logs"
        try:
            log_response = await client.get(logs_url, headers=headers) # get run_id-specific log
            if log_response.status_code != 200:
                return [
                    "failed",
                    f"An error occured fetching log for run {run_id}"
                ]
            return "success", extract_log_content(log_response.content)
        except Exception as e:
            logger.info(f"An error occured fetching log for run {run_id}: {e}")


async def generate_ai_response(text):
    """
    Generates AI response using google's gemini API

    Args:
        text(string) - user input
    """
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                temperature=0.8,
                top_p=0.9,
                top_k=50,
                system_instruction=sys_instruct),
            contents=[text]
        )
        return response.text
    except Exception as e:
        logger.info(f"An error occured while getting AI response from Gemini: {e}")


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
                    "username": "devbot",
                    "event_name": "Request accepted",
                    "message": "Your request is being processed",
                    "status": "success"
                }
            )
            response.raise_for_status()
        except Exception as e:
            logger.info(f"Error in request_handler: {e}")

        query_class = classify_query(text)

        owner = settings.get('repo_owner', None)
        repo = settings.get('github_repo', None)
        token = settings.get('github_PAT', None)

        if query_class == "github_related":
            try:
                response = await client.post(channel_url, json={
                    "username": "devbot",
                    "event_name": "fetching log",
                    "message": "Fetching log from github",
                    "status": "success"
                })
                response.raise_for_status()
            except Exception as e:
                logger.info(f"Error occurred while notifying log fetch: {e}")

            status, log = await fetch_github_logs(owner, repo, token)
            if status == "failed":
                try:
                    response = await client.post(channel_url, json={
                        "username": "devbot",
                        "event_name":  "Log failed to fetch.",
                        "message": log,
                        "status": "Error"
                    })
                    response.raise_for_status()
                except Exception as e:
                    logger.info(f"Error occurred while sending log request errors to channel: {e}")
                return

            payload = {
                "username": "devbot",
                "event_name":  "GitHub Deployment Log",
                "message": log,
                "status": "success"
            }
            try:
                response = await client.post(channel_url, json=payload)
            except Exception as e:
                logger.info(f"Error occurred while sending log to channel: {e}")
                

        else:
            ai_response = await generate_ai_response(text)
            cleaned_ai_text = clean_ai_response(ai_response)
            logger.info(cleaned_ai_text)
            try:
                response = await client.post(channel_url, json={
                    "username": "devbot",
                    "event_name":  "devbot thinks",
                    "message": cleaned_ai_text,
                    "status": "success"
                })
                response.raise_for_status()
            except Exception as e:
                logger.info("Error occurred while sending AI-generated response")


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
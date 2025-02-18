import io
import aiohttp
import zipfile

# decompress and extract log
def extract_log_content(content):
    zip_file = zipfile.ZipFile(io.BytesIO(content))
    with open(zip_file.extract('0_deploy.txt'), 'r') as f:
        log_content = f.readlines()
    return log_content[-20:]

# fetch workflow run log from github
async def fetch_github_logs(owner, repo, token):
    if not repo:
        return None
    
    gh_api_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {'Authorization': f'token {token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(gh_api_url, headers=headers) as response:
            if response.status != 200:
                return None

            runs = (await response.json()).get('workflow_runs', [])
            if not runs:
                return None
            run_id = runs[0]['id']
            logs_url = f"{gh_api_url}/{run_id}/logs"
            async with session.get(logs_url, headers=headers) as log_response:
                if log_response.status != 200:
                    return None
                return extract_log_content(await log_response.read())

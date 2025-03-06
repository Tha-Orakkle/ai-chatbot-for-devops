# AI-CHATBOT-FOR-DEVOPS (DEVBOT)

## Description

An integration for an event-monitoring application -[Telex](https://telex.im)- that provides an interface to access deployment logs from GitHub workflow runs and to get DevOps and CI/CD related assitance from AI.

This integration leverages the power of embedding and NLI-based models (`all-MiniLM-L6-V2` and `MoritzLaurer/DeBERTa-v3-base-mnli`) to classify context of messages from the Telex channel in order to generate the appropriate response.

### Syntax

```bash
/devbot how can i deploy my program to AWS?
# prefix query with /devbot
```

## Environmental Variables

- Add keys to your environment

```bash
GEMINI_KEY=<your-google-gemini-API-key>
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Tha-Orakkle/ai-chatbot-for-devops.git

   cd ai-chatbot-for-devops # navigate to project directory
   ```

2. Create and activate a virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate # Linux/MacOS
   .\venv\bin\activate.bat
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements
   ```
4. Run:
   ```bash
   hypercorn main:app
   ```

## Request

- POST /v1/webhook
- request body:

```json
{
  "settings": [
    {
      "label": "channel_url",
      "default": "<your-channel-webhook-url>"
    },
    {
      "label": "github_repo",
      "default": "fastapi-book-project"
    },
    {
      "label": "repo_owner",
      "default": "Tha-Orakkle"
    },
    {
      "label": "github_PAT",
      "default": "<github-personal-access-token>" // generate a token with read only access
    }
  ],
  "message": "/devbot fetch my deployment log from github"
}
```

- [How to generate GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

## Response

```json
{
  "username": "devbot",
  "event_type": "<operation-that-was-performed by bot>",
  "message": "devbot-response",
  "status": "success"
}
```

## Integration Specification

:clipboard: Integration specification available at [devbot-integration-spec](https://devbot-integration-spec.up.railway.app/v1/integration.json)

## Author

- Paul Adegbiran-Ayinoluwa (adegbiranayinoluwa.paul@yahoo.com)

## License

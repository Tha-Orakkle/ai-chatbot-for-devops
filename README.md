# AI-CHATBOT-FOR-DEVOPS (DEVBOT)

## Description

An integration for an event-monitoring application -[Telex](https://telex.im)- that provides an interface to access deployment logs from GitHub workflow runs and to get DevOps and CI/CD related assitance from AI. 

This integration leverages the power of embedding and NLI-based models (`all-MiniLM-L6-V2`, `MoritzLaurer/DeBERTa-v3-base-mnli`) to classify context of messages from the Telex channel in order to generate the appropriate response.
### Syntax
```json
/devbot how do i fetch my deployment logs? 
# prefix query with /devbot
```



## Environmental Variables
* Add keys to your environment
```bash
GEMINI_KEY=<your-google-gemini-API-key>
CHANNEL_URl=<telex-channel-webhook-url>
```

## Installation
1. Clone the repository:
    ```
    git clone https://github.com/{telex_organisation}/ai-chatbot-for-devops.git

    cd ai-chatbot-for-devops # navigate to project directory
    ```
2. Create and activate a virtual environment
    ```bash
    python3 -m venv venv
    source venv/bin/activate # Linux/MacOS
    .\venv\bin\activate.bat
    ```
3. Install dependencies:
    ```
    pip install -r requirements
    ```
4. Run:
    ```bash
    hypercorn main:app
    ```


## Integration Specification

:clipboard: [specification format](./app/integration_config.py)

You can also access the specification [here](https://devbot-integration-spec.up.railway.app/v1/integration.json).

## Author
* Paul Adegbiran-Ayinoluwa [Mail](mailto:adegbiranayinoluwa.paul@yahoo.com)

## License

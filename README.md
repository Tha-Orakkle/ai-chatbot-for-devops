# AI-CHATBOT-FOR-DEVOPS (DEVBOT)

## Description

An integration for an event-monitoring solution -[Telex](https://telex.im)- that provides an interface to access deployment logs from GitHub workflow runs and to get DevOps and CI/CD related assitance from AI. 

This integration leverages the power of embedding and NLI-based models (`all-MiniLM-L6-V2`, `facebook/bart-large-mnli`) to classify context of messages from the Telex channel in order to generate the appropriate response.

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

You can also access the integration specification on [https://...].

## Author
* Paul Adegbiran-Ayinoluwa (adegbiranayinoluwa.paul@yahoo.com)

## License

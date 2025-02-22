SPECIFICATION = {
    'data': {
        'date': {
            'created_at': '2025-02-17',
            'updated_at': '2025-02-17',
        },
        "descriptions": {
            "app_description": "An AI-powered assistant that provides responses to " +
            "Devops and CI/CD related queries and fetches logs from github action workflows " +
            "on request.",

            "app_logo": "https://devbot-integration-spec.up.railway.app/v1/devbot-logo.jpg",  # url to app_logo
            "app_name": "ai-chatbot-for-devops",
            "app_url": "http://54.175.31.188",
            "background_color": "#e7e7e7" 
        },
        "integration_category": "DevOps & CI/CD",
        "integration_type": "modifier",
        "is_active": False,
        "key_features": [
            "Natural Language Understanding (NLP) - Understands and interprets DevOps-related queries.",
            "CI/CD Logs Lookup - Fetches the latest pipeline logs from GitHub on request.",
            "Deployment Insights - Provides quick tips on fixing deployment issues.",
            "Documentation Assistant - Suggests solutions from official docs",
        ],
        "settings": [
            {
                "label": "github_repo",
                "type": "text",
                "required": False,
                "default": "",
            },
            {
                "label": "repo_owner",
                "type": "text",
                "required": False,
                "default": ""
            },
            {
                "label": "github_PAT",
                "type": "text",
                "required": False,
                "default": ""
            },
        ],
        "target_url": "http://54.175.31.188/v1/webhook",
        "NOTE": "prefix query with '/devbot'",
        "author": "tha_orakkle",
        "email": "adegbiranayinoluwa.paul@yahoo.com"
    }
}
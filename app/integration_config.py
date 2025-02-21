integration_config = {
    'data': {
        'date': {
            'created_at': '2025-02-17',
            'updated_at': '2025-02-17',
        },
        "descriptions": {
            "app_description": "An AI-powered assistant that provides responses to " +
            "Devops and CI/CD related queries in form of github actions workflows run logs " +
            "or as ai-generated response",

            "app_logo": "app_logo",  # url to app_logo
            "app_name": "ai-chatbot-for-devops",
            "app_url": "app_url",  # app_url
            "background_color": "#333333"  # hexcode for the backgrund-color
        },
        "integration_category": "DevOps & CI/CD ",
        "integration_type": "modifier",
        "is_active": False,
        "key_features": [
            "Natural Language Understanding (NLP) - Understands and interprets DevOps-related queries.",
            "CI/CD Logs Lookup - Fetches the latest pipeline logs on request.",
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
        "target_url": "url"  # where data will be sent to
    }
}

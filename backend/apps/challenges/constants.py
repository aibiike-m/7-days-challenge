MIN_GOAL_LENGTH = 10
MAX_GOAL_LENGTH = 500
CHALLENGE_DURATION_DAYS = 7
MAX_ACTIVE_CHALLENGES = 3

# Color palette for challenges
CHALLENGE_COLORS = [
    "#F4A7B9",  # Cherry Blossom (Soft Pink)
    "#E0B2C8",  # Orchid Petal (Muted Pink/Purple)
    "#A7E6D8",  # Aquamarine (Bright Mint)
    "#B6EB6E",  # Lime Sorbet (Fresh Light Green)
    "#479FC8",  # Ocean Blue (Clear Blue)
    "#B58FEB",  # Bright Lavender (Soft Violet)
    "#FF8080",  # Coral Red (Warm Salmon)
    "#F72F57",  # Deep Rose (Vibrant Pink/Red)
    "#8FECF7",  # Electric Ice (Bright Cyan)
    "#EDCB5A",  # Golden Sand (Warm Mustard/Yellow)
]

# Challenge statuses
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"
STATUS_ABANDONED = "abandoned"

STATUS_CHOICES = [
    (STATUS_ACTIVE, "Active"),
    (STATUS_COMPLETED, "Completed"),
    (STATUS_ABANDONED, "Abandoned"),
]

# AI Prompt Template
AI_PROMPT_TEMPLATE = """
You are an assistant in creating plans to achieve goals.
Create a detailed {days} day plan to achieve the following goal:
"{goal}"

Requirements:
- Create 1 to 8 tasks each day (depending on the complexity of the goal)
- Tasks should be specific and achievable within a day
- Consider the context of the goal:
    * For learning (languages, skills) → repetitive tasks
    * For projects (creating something) → unique tasks
    * For habits (sports, health) → gradual increase in workload
- Tasks from simple to complex
- Task title: short (up to 100 characters)
- Description: detailed with specific steps

Return the response STRICTLY in JSON format, without additional text:
{{
    "goal_ru": "Translation of goal to Russian",
    "goal_en": "Translation of goal to English",
    "tasks": [
        {{"day": 1, "title_ru": "...", "title_en": "...", "description_ru": "...", "description_en": "..."}},
        {{"day": 1, "title_ru": "...", "title_en": "...", "description_ru": "...", "description_en": "..."}}
    ]
}}

IMPORTANT:
- Provide titles and descriptions in BOTH Russian and English
- Return ONLY the JSON object
- No Markdown formatting
- No ```json``` or other characters
- Pure, valid JSON
"""

# AI retry settings
AI_MAX_RETRIES = 3
AI_RETRY_DELAY = 1
AI_RETRY_BACKOFF = 2

# Error messages
ERROR_AI_INVALID_FORMAT = "AI returned invalid format (expected dict with 'tasks' key)"
ERROR_AI_INVALID_JSON = "AI returned invalid JSON"
ERROR_AI_NO_RESPONSE = "Failed to get response from AI"
ERROR_AI_GENERATION_FAILED = "Failed to generate challenge plan"
ERROR_GEMINI_API_KEY_MISSING = "GEMINI_API_KEY not found in environment variables"

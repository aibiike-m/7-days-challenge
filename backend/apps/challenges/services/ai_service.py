import os
import json
import time
import google.generativeai as genai
from google.generativeai import GenerationConfig
from ..constants import (
    AI_PROMPT_TEMPLATE,
    AI_MAX_RETRIES,
    AI_RETRY_DELAY,
    AI_RETRY_BACKOFF,
    ERROR_GEMINI_API_KEY_MISSING,
    ERROR_AI_INVALID_FORMAT,
    ERROR_AI_INVALID_JSON,
    ERROR_AI_NO_RESPONSE,
    ERROR_AI_GENERATION_FAILED,
    CHALLENGE_DURATION_DAYS,
)
import logging
logger = logging.getLogger(__name__)


class AIService:
    """Google Gemini AI Service"""

    def __init__(self):
        """
        Initialize AI service with Gemini API.

        Raises:
            ValueError: If GEMINI_API_KEY is not set in environment
        """
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError(ERROR_GEMINI_API_KEY_MISSING)

        genai.configure(api_key=api_key)

        generation_config = GenerationConfig(response_mime_type="application/json")

        self.model = genai.GenerativeModel(
            "gemini-2.5-flash", generation_config=generation_config
        )
        logger.info("AI Service initialized successfully")

    def _parse_ai_response(self, response_text: str) -> dict:
        """
        Parse and validate AI response.

        Args:
            response_text: Raw response text from AI

        Returns:
            dict: Parsed and validated response data

        Raises:
            ValueError: If response format is invalid
        """
        try:
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            data = json.loads(clean_text)

            if not isinstance(data, dict) or "tasks" not in data:
                logger.warning(
                    f"Invalid AI response structure: {list(data.keys()) if isinstance(data, dict) else type(data)}"
                )
                raise ValueError(ERROR_AI_INVALID_FORMAT)

            logger.debug(
                f"Successfully parsed AI response with {len(data.get('tasks', []))} tasks"
            )
            return data

        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {str(e)}")
            raise ValueError(f"{ERROR_AI_INVALID_JSON}: {str(e)}")

    def generate_challenge_plan(
        self, goal: str, days: int = CHALLENGE_DURATION_DAYS
    ) -> dict:
        """
        Generate a task plan based on the goal with retry mechanism.

        Attempts to generate a plan up to AI_MAX_RETRIES times with
        exponential backoff between attempts.

        Args:
            goal: User's goal description
            days: Number of days for the challenge (default: 7)

        Returns:
            dict: Challenge plan with tasks in both languages
                  Structure: {
                      'goal_ru': str,
                      'goal_en': str,
                      'tasks': [
                          {
                              'day': int,
                              'title_ru': str,
                              'title_en': str,
                              'description_ru': str,
                              'description_en': str
                          },
                          ...
                      ]
                  }

        Raises:
            ValueError: If AI returns invalid format
            Exception: If generation fails after all retries
        """
        logger.info(
            f"Generating challenge plan for goal: '{goal[:50]}{'...' if len(goal) > 50 else ''}' ({days} days)"
        )

        prompt = AI_PROMPT_TEMPLATE.format(days=days, goal=goal)

        last_error = None
        retry_delay = AI_RETRY_DELAY

        for attempt in range(AI_MAX_RETRIES):
            try:
                logger.debug(
                    f"Attempt {attempt + 1}/{AI_MAX_RETRIES}: Calling Gemini API"
                )
                response = self.model.generate_content(prompt)

                if not response or not hasattr(response, "text"):
                    raise AttributeError(ERROR_AI_NO_RESPONSE)

                response_text = response.text.strip()
                data = self._parse_ai_response(response_text)

                tasks_count = len(data.get("tasks", []))
                logger.info(
                    f"✓ Successfully generated plan with {tasks_count} tasks on attempt {attempt + 1}"
                )
                return data

            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt + 1}/{AI_MAX_RETRIES}: Invalid JSON from AI - {str(e)}"
                )
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Response preview: {response_text[:200]}...")
    
            except ValueError as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}/{AI_MAX_RETRIES}: {str(e)}")

            except AttributeError as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}/{AI_MAX_RETRIES}: {str(e)}")

            except Exception as e:
                last_error = e
                logger.error(
                    f"Attempt {attempt + 1}/{AI_MAX_RETRIES}: Unexpected error: {str(e)}",
                    exc_info=True, 
                )

            if attempt < AI_MAX_RETRIES - 1:
                logger.debug(f"Waiting {retry_delay}s before retry...")
                time.sleep(retry_delay)
                retry_delay *= AI_RETRY_BACKOFF

        error_message = f"{ERROR_AI_GENERATION_FAILED}: {str(last_error)}"
        logger.error(
            f"Failed to generate plan after {AI_MAX_RETRIES} attempts: {error_message}"
        )
        raise Exception(error_message)

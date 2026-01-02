import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai import GenerationConfig


load_dotenv()


class AIService:
    """Google Gemini AI Service"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY не найден в .env файле!")

        genai.configure(api_key=api_key)

        generation_config = GenerationConfig(
            response_mime_type="application/json"
        )

        
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config=generation_config
        )

    def generate_challenge_plan(self, goal: str, days: int = 7) -> dict:
        """Generates a task plan based on the goal"""

        prompt = f"""

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



            Return the response STRICTLY in JSON array format, without additional text:            
            {{
                "goal_ru": "Перевод цели на русский",
                "goal_en": "Goal translation to English",
                "tasks": [
                    {{"day": 1, "title_ru": "...", "title_en": "...", "description_ru": "...", "description_en": "..."}},
                    {{"day": 1, "title_ru": "...", "title_en": "...", "description_ru": "...", "description_en": "..."}}
                ]
            }}
            
            IMPORTANT:
            - Provide titles and descriptions in BOTH Russian and English.
            - Return ONLY the JSON array
            - No Markdown formatting
            - No ```json``` or other characters
            - Pure, valid JSON
            """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            data = json.loads(response_text)

            if not isinstance(data, dict) or "tasks" not in data:
                raise ValueError(
                    "AI вернул неверный формат (ожидался словарь с ключом 'tasks')"
                )

            return data  
        except Exception as e:
            print(f"Ошибка AI: {e}")
            raise e
        except json.JSONDecodeError as e:
            print(f"Ответ AI не является валидным JSON:")
            print(response_text)
            raise ValueError(f"AI вернул невалидный JSON: {str(e)}")

        except AttributeError as e:
            print(f"Ошибка при получении ответа от AI: {e}")
            raise Exception(f"Не удалось получить текст ответа: {str(e)}")

        except Exception as e:
            print(f"Ошибка: {e}")
            raise Exception(f"Ошибка при генерации плана: {str(e)}")

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class AIService:
    """Сервис для работы с Google Gemini AI"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY не найден в .env файле!")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-2.5-flash")

        # self.model = genai.GenerativeModel('gemini-2.0-flash')
        # self.model = genai.GenerativeModel('gemini-2.5-pro') 

    def generate_challenge_plan(self, goal: str, days: int = 7) -> list:
        """Генерирует план задач на основе цели"""

        prompt = f"""Ты помощник для создания планов достижения целей.

Создай детальный план на {days} дней для достижения следующей цели:
"{goal}"

Требования:
- На каждый день создай от 1 до 8 задач (в зависимости от сложности цели)
- Задачи должны быть конкретными и выполнимыми за день
- Учитывай контекст цели:
  * Для обучения (языки, навыки) → повторяющиеся задачи
  * Для проектов (создать что-то) → уникальные задачи  
  * Для привычек (спорт, здоровье) → постепенное увеличение нагрузки
- Задачи от простого к сложному
- Название задачи: кратко (до 100 символов)
- Описание: подробно с конкретными шагами

Верни ответ СТРОГО в формате JSON массива, без дополнительного текста:
[
  {{"day": 1, "title": "Название задачи", "description": "Подробное описание что делать"}},
  {{"day": 1, "title": "Еще одна задача дня 1", "description": "Описание"}},
  {{"day": 2, "title": "Задача дня 2", "description": "Описание"}},
  ...
]

ВАЖНО: 
- Верни ТОЛЬКО JSON массив
- Без markdown форматирования
- Без ```json``` или других символов
- Чистый валидный JSON"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            print(f"📝 Ответ AI (первые 200 символов): {response_text[:200]}")

            if "```" in response_text:
                json_match = re.search(
                    r"```(?:json)?\s*(\[.*?\])\s*```", response_text, re.DOTALL
                )
                if json_match:
                    response_text = json_match.group(1)
                else:
                    response_text = (
                        response_text.replace("```json", "").replace("```", "").strip()
                    )

            tasks = json.loads(response_text)

            if not isinstance(tasks, list):
                raise ValueError("AI вернул не список")

            if len(tasks) == 0:
                raise ValueError("AI не вернул ни одной задачи")

            for i, task in enumerate(tasks):
                
                if 'daym' in task and 'day' not in task:
                    task['day'] = task.pop('daym')

                if not all(key in task for key in ["day", "title", "description"]):
                    raise ValueError(
                        f"Задача {i+1} имеет неправильную структуру: {task}"
                    )
                if task["day"] < 1 or task["day"] > days:
                    raise ValueError(f"Неверный номер дня: {task['day']}")

            days_present = set(task["day"] for task in tasks)
            missing_days = set(range(1, days + 1)) - days_present
            if missing_days:
                print(f"⚠️ Предупреждение: нет задач для дней {missing_days}")

            print(f"✅ Успешно сгенерировано {len(tasks)} задач")
            return tasks

        except json.JSONDecodeError as e:
            print(f"❌ Ответ AI не является валидным JSON:")
            print(response_text)
            raise ValueError(f"AI вернул невалидный JSON: {str(e)}")

        except AttributeError as e:
            print(f"❌ Ошибка при получении ответа от AI: {e}")
            raise Exception(f"Не удалось получить текст ответа: {str(e)}")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            raise Exception(f"Ошибка при генерации плана: {str(e)}")

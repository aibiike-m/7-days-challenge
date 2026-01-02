from modeltranslation.translator import register, TranslationOptions
from .models import Challenge, Task


@register(Challenge)
class ChallengeTranslationOptions(TranslationOptions):
    fields = ("goal",)


@register(Task)
class TaskTranslationOptions(TranslationOptions):
    fields = ("title", "description")

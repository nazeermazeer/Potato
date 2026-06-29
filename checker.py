import language_tool_python
from dataclasses import dataclass

tool = language_tool_python.LanguageTool('en-US')
tool.picky = True


@dataclass
class CustomMatch:
    rule_id: str
    message: str
    context: str
    replacements: list[str]
    offset: int
    error_length: int
    


def check_sentence_punctuation(value: str) -> list[CustomMatch]:
    stripped = value.strip()
    if not stripped or stripped[-1] in ".!?":
        return []

    return [
        CustomMatch(
            rule_id="MISSING_SENTENCE_END_PUNCTUATION",
            message="This sentence does not end with punctuation.",
            context=value,
            replacements=[f"{stripped}."],
            offset = len(value),
            error_length = 1
        )
    ]


def enforce_sentence_punctuation(value: str) -> str:
    stripped = value.rstrip()
    if not stripped or stripped[-1] in ".!?":
        return value

    return f"{stripped}."

class Checker:
    def checkText(self, input):
        text = input
        matches = tool.check(text) + check_sentence_punctuation(text)
        return matches

    def getCorrectedText(self, text):
        correctedText = enforce_sentence_punctuation(tool.correct(text))
        return correctedText

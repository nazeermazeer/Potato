import language_tool_python
from dataclasses import dataclass
import emoji

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
    


def checkPunctuation(value: str) -> list[CustomMatch]:
    stripped = value.strip()
    if not stripped or stripped[-1] in ".!?":
        return []

    return [
        CustomMatch(
            rule_id="MISSING_SENTENCE_END_PUNCTUATION",
            message="This sentence does not end with punctuation.",
            context=value,
            replacements=[f"{stripped}."],
            offset=len(value),
            error_length=1
        )
    ]


def checkEmojis(value: str) -> list[CustomMatch]:
    return [
        CustomMatch(
            rule_id="NO_EMOJIS",
            message="Using emojis in formal academic writing is considered non-professional.",
            context=value,
            replacements=[""],
            offset=match["match_start"],
            error_length=match["match_end"] - match["match_start"]
        )
        for match in emoji.emoji_list(value)
    ]


def enforcePunctuation(value: str) -> str:
    stripped = value.rstrip()
    if not stripped or stripped[-1] in ".!?":
        return value

    return f"{stripped}."


def enforceNoEmojis(value: str) -> str:
    return emoji.replace_emoji(value, replace="")


class Checker:
    def checkText(self, input):
        text = input
        matches = tool.check(text) + checkPunctuation(text) + checkEmojis(text)
        return matches

    def getCorrectedText(self, text):
        correctedText = enforcePunctuation(enforceNoEmojis(tool.correct(text)))
        return correctedText

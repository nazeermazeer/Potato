from dataclasses import dataclass

import emoji
import requests

LANGUAGETOOL_API_URL = "https://api.languagetool.org/v2/check"


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
            message="Using emojis in formal academic writing is unprofessional.",
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
    def _checkLanguageTool(self, text: str) -> list[CustomMatch]:
        response = requests.post(
            LANGUAGETOOL_API_URL,
            data={
                "text": text,
                "language": "en-US",
                "level": "picky",
            },
            timeout=10,
        )
        response.raise_for_status()

        return [
            CustomMatch(
                rule_id=match["rule"]["id"],
                message=match["message"],
                context=match["context"],
                replacements=[replacement["value"] for replacement in match["replacements"]],
                offset=match["offset"],
                error_length=match["length"],
            )
            for match in response.json()["matches"]
        ]

    def checkText(self, input: str) -> list[CustomMatch]:
        matches = self._checkLanguageTool(input)
        return matches + checkPunctuation(input) + checkEmojis(input)

    def getCorrectedText(self, text: str) -> str:
        matches = self._checkLanguageTool(text)
        corrected_text = text
        for match in reversed(matches):
            if match.replacements:
                corrected_text = (
                    corrected_text[:match.offset]
                    + match.replacements[0]
                    + corrected_text[match.offset + match.error_length:]
                )

        correctedText = enforcePunctuation(enforceNoEmojis(corrected_text))
        return correctedText

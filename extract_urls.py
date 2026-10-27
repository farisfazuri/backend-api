
import re

TLD = (
    r"com|org|net|edu|gov|mil|int|"
    r"co\.uk|org\.uk|ac\.uk|uk|"
    r"com\.my|org\.my|net\.my|my|"
    r"io|ai|app|info|biz|mobi|"
    r"sg|in|au|ca|de|jp"
)

# Explicit URLs: http://, https://, and www.
explicit_pattern = re.compile(
    r"""(?i)(?:https?://|www\.)[^\s<>"']+"""
)

# Bare domains must start at a word boundary

bare_pattern = re.compile(
    r"(?i)(?<![\w@.-])"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"(?:" + TLD + r")"
    r"(?:/[^\s]+)?"
)



def extract_urls(text):
    if not isinstance(text, str) or not text.strip():
        return []

    matches = []

    # Collect explicit URLs first
    for match in explicit_pattern.finditer(text):
        url = match.group(0).rstrip(".,!?;:)")
        if url:
            matches.append((match.start(), match.end(), url))

    # Collect bare domains only if they don't overlap explicit URLs
    for match in bare_pattern.finditer(text):
        overlaps = any(
            match.start() < end and match.end() > start
            for start, end, _ in matches
        )

        if not overlaps:
            url = match.group(0).rstrip(".,!?;:)")
            if url:
                matches.append((match.start(), match.end(), url))

    matches.sort(key=lambda item: item[0])

    result = []
    for _, _, url in matches:
        if url not in result:
            result.append(url)

    return result

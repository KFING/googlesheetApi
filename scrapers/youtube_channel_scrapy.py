import re


def extract_nickname(input_string):
    pattern = r"(?:https:\/\/www\.instagram\.com\/)?([^\/?]+)"
    match = re.search(pattern, input_string)

    if match:
        return match.group(1)
    else:
        return None


# Примеры входных данных
inputs = [
    "https://www.instagram.com/b3r3zko?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==",
    "b3r3zko"
]

for input_str in inputs:
    nickname = extract_nickname(input_str)
    print(f"Input: {input_str} -> Nickname: {nickname}")
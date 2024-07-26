import re

def identify_instagram_input(input_str):
    # Регулярные выражения для проверки URL поста
    post_pattern = re.compile(r'^https?://(www\.)?instagram\.com/p/[\w-]+/?(\?[\w=&]+)?$')

    if post_pattern.match(input_str):
        return 'post'
    elif re.match(r'^[\w-]+$', input_str):
        return 'profile'
    else:
        return 'unknown'

# Примеры использования
inputs = [
    'https://www.instagram.com/p/B0QTtXKi3u_/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA=='
]

for input_str in inputs:
    print(f'Input: {input_str} - Type: {identify_instagram_input(input_str)}')
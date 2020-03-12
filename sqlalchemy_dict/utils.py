import re


def to_camel_case(text):
    return re.sub("(_\w)", lambda x: x.group(1)[1:].upper(), text)

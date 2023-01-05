
from json import dumps


def print_dict(text):
    print(dumps(text, indent=4))


def enforce_options(options):
    user_input = input(f'Please enter one of {options}:\n')
    while user_input not in options:
        user_input = input(f'Please enter one of {options}:\n')
    return user_input


def user_allows(question: str = None):
    print(question)
    return 'y' == enforce_options(['y', 'n'])
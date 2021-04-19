import re

def get_invalid_keys():
    use_case = [
        re.compile(r'main-sidebar|emailRejected|masterMcWrap'), re.compile(r'pay-wall')
    ]

    return use_case
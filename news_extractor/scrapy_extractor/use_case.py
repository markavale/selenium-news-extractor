import re

def div_class_use_case():
    use_case = [
        re.compile(r'main-sidebar'), re.compile(r'pay-wall')
    ]

    return use_case
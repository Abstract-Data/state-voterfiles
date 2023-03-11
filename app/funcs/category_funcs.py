from typing import Dict


def category_iterator(state: Dict):
    return iter(
        [
            state['FILE-FILER-DETAILS'],
            state['FILE-CONTRIBUTOR-DETAILS'],
            state['FILE-VENDOR-PAYMENT-DETAILS']
        ]
    )


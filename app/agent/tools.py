BUSINESS_INFO = {
    "name": "Your Company",
    "services": [
        "Website Design",
        "Web Development",
        "AI Agent Development",
    ],
    "target_audience": [
        "Small Businesses",
        "Startups",
        "Growing Companies",
    ],
    "value_proposition": (
        "We help businesses grow through "
        "professional websites and AI automation."
    ),
}


def get_business_info() -> dict:
    """
    Return the company's business information.
    """
    return BUSINESS_INFO
import re

def is_valid_email(email):
    """
    Performs a basic check to see if an email address has a valid format.
    """
    if not email:
        return False
    # A simple regex for email validation
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def is_valid_phone(phone):
    """
    Performs a basic check for a phone number (allows numbers, dashes, parens).
    Adjust regex as needed for international formats.
    """
    if not phone:
        return False
    # Matches formats like 555-123-4567, (555)123-4567, 5551234567
    regex = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
    return re.match(regex, phone) is not None


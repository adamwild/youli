def key_to_number(key):
    """Convert 'a'-'z' to 10-35"""
    if key.isdigit():
        return int(key)
    if key.isalpha() and len(key) == 1:
        return ord(key.lower()) - ord('a') + 10

def number_to_key(number):
    """Convert 10-35 to 'a'-'z'"""
    if 10 <= number <= 35:
        return chr(number - 10 + ord('a'))
    else:
        return str(number)

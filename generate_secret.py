import random
import string

def generate_secret_key(length=50):
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length))

print(generate_secret_key())
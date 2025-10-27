import random


def generateVerificationId(length=6):
    characters = "abcdefghijklmnopqrstuvxyz".upper()
    numbers = "1234567890"

    verificationCode = ""
    for i in range(0, length):
        if random.randint(0, 1) == 1:  # Choose from numbers
            verificationCode += numbers[random.randint(0, len(numbers) - 1)]
        else:
            verificationCode += characters[random.randint(0, len(characters) - 1)]
    return verificationCode

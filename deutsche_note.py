note = float(input("Iranische Note eingeben: "))

if note < 10 or note > 20:
    print("Ungültige Note")
else:
    deutsch = 1 + 3 * ((20 - note) / (20 - 10))
    deutsch = round(deutsch, 2)

    print("Deutsche Note:", deutsch)

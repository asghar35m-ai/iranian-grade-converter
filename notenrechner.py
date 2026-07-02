iranische_note = float(input("Gib deine iranische Note ein: "))

deutsche_note = 1 + 3 * ((20 - iranische_note) / 10)

print("Deutsche Note:", round(deutsche_note, 2))
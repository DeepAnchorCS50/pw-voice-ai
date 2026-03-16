import json
import os

conv_dir = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\conversations"

short = []
for f in os.listdir(conv_dir):
    with open(os.path.join(conv_dir, f)) as file:
        conv = json.load(file)
    count = len(conv.get("messages", []))
    if count < 14:
        short.append((f, count))

short.sort(key=lambda x: x[1])

print("Conversations with fewer than 14 messages:")
for name, count in short:
    print("  {} — {} messages".format(name, count))
print("\nTotal short: {} out of 100".format(len(short)))
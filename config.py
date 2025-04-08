'''Provies loaded data , info , help , messages'''
import json
git_hub = "https://gith"+"ub.com/" + "happyharsh-codes"
with open("data.json", "r") as f:
    data = json.load(f)
with open("info.json", "r") as f:
    info = json.load(f)
with open("help.json", "r") as f:
    helps = json.load(f)
with open("messages.json", "r") as f:
    message = json.load(f)
with open("server.json", "r") as f:
    server = json.load(f)

print("__init__ was runned")
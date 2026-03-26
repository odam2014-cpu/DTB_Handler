import requests
import json


header = {'Authorization': "f9LHodD0cOKohL7lQquapFyV_lmJ38kH0_XwhyuQ7JFz0oyu4FYXsmD3NavHHk_rQ8RR62uLXYqB2_sh2Q1H"}
url    = "https://platform-api.max.ru/messages"

params = {
    "chat_id": "233194361"
    }

req = requests.get(url = url, params=params, headers=header)
with open("mess.json", 'w', encoding='utf-8') as f:

    f.write(req.text)
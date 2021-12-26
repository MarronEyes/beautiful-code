import base64
import io

import commentjson
import requests
from PIL import Image

with open("../src/assets/imgs/default-image.json", "r") as json:
    args = commentjson.load(json)
    args["code"] = '''
print("hello world!")
'''
    request = requests.post("http://127.0.0.1:8080/code/", json=args)
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        error = request.json()
        print(error)
    elif content_type == "image/png;base64":
        try:
            with io.BytesIO(base64.b64decode(request.content)) as file:
                img = Image.open(file)
                img.show()

        except Exception as e:
            print(e)

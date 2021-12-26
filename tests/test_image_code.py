import commentjson

from src.image_code import ImageCode

with open("../src/assets/imgs/default-image.json", "r") as json:
    args = commentjson.load(json)
    args["code"] = '''
print("hello world!")
'''
ImageCode(args).generate("image.png")

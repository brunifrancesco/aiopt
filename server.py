import muffin
from aiohttp import web
from fn.monad import Option
import random
import os
import PIL
from PIL import Image
import json

app = muffin.Application('photogallery')


def resize_images(image):
    img = Image.open(image)
    img.thumbnail((img.size[0]*0.8, img.size[1]*0.8), PIL.Image.ANTIALIAS)
    img.save(image, "JPEG")


def get_all_images():
    return filter(lambda item: not item == ".DS_Store", os.listdir("uploaded"))


@app.register('/')
def index(request):
    r = web.Response(text=json.dumps([dict(src="../uploaded/"+value) for value in get_all_images()]), content_type="application/json")
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r


@app.register('/addphoto')
def addphoto(request):

    def save_content(content):
        path = os.path.join("uploaded", str(random.random()) + ".jpeg")
        with open(path, "wb" ) as output:
            output.write(content)
        return path

    data = yield from request.post()

    Option(data.get("file", None))\
        .map(lambda item: getattr(item, "file"))\
        .map(lambda item: save_content(item.read()))\
        .map(lambda item: resize_images(item))\
        .map(lambda item: get_all_images())\
        .get_or([])

    r = web.Response(text=json.dumps([dict(src="../uploaded/"+value) for value in get_all_images()]), content_type="application/json")
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r

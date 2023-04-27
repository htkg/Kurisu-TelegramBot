
import io
import base64
from PIL import Image
from io import BytesIO
import json
from pyrogram.types import InputMediaPhoto

def process_response_raw(res):
    imgs = []
    for i, i_b64 in enumerate(res['images']):
        image = Image.open(io.BytesIO(
            base64.b64decode(i_b64.split(",", 1)[0])))
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        imgs.append(InputMediaPhoto(buf))

    return imgs
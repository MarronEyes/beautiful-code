import base64

import bottle as bt
import commentjson

from src.image_code import ImageCode


def error(reason: str):
    return {"success": False, "reason": reason}


@bt.get("/")
def html():
    """The main page."""
    return bt.template("views/index.html")


@bt.post("/code/")
def get_image():
    """
    Generate an image with options from ImageCode's arguments.

    Parameters:
    ----------
    :param dict args: A json config that will be loaded to pass to ImageCode constructor as a dict.
    :param str code: The actual code.

    :return An image.
    """
    if bt.request.json is None:
        return error("Json content not found")

    try:
        args = bt.request.json
        if "args" in args:
            code = args.get("code")
            args = commentjson.loads(args.get("args"))
            args["code"] = code
    except Exception as e:
        return error(f"Error during json parsing : {e}")

    try:
        img = ImageCode(args).generate(img_format="png")
    except Exception as e:
        return error(f"Error when generating the image : {e}")

    img.seek(0)
    bt.response.set_header("Content-type", "image/png;base64")
    b64_img = base64.b64encode(img.read())
    img.close()
    return b64_img


@bt.route('/assets/<filepath:path>')
def assets(filepath):
    """Gets a file in the assets directory."""
    return bt.static_file(filepath, root="assets/")

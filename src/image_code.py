import os
import requests
from io import BytesIO
from validators import url as is_url
from matplotlib.colors import is_color_like
from requests.exceptions import RequestException
from PIL import Image, ImageDraw, ImageFont, ImageFilter
# WARNING: pygments does not support loading ttf fonts from files. (See https://github.com/pygments/pygments/pull/1960)
# To have this functionality, you have to either wait for a new release of pygments with this feature
# or install pygments from this fork https://github.com/MarronEyes/pygments.git. (Install from branch img-font)
from pygments import highlight
from pygments.formatters.img import ImageFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers import guess_lexer
from pygments.styles import get_style_by_name


class ResourceNotFoundError(Exception):
    """Exception raised when a resource (with ImageCode.get()) is not found."""


class ImageCode:
    """
    Class used for generating images of codes.

    Check __init__ docstring for the different options.
    """
    assets_dir = "assets/"

    # A dict that contains the max values of each parameter.
    LIMIT = {
        "w": 1920,
        "h": 1080,
        "bar_h": 60,
        "tab_font_size": 60,
        # Here is the max number of characters allowed in the name.
        "tab_name": 30,
        # Here too.
        "code": 1000,
        "blur_radius": 15,
        "tab_line_width": 10,
        "icon_size": (64, 64),
        "spacing": 30,
        "margins": 40,
        "code_font_size": 60,
        "code_line_padding": 40,
        # And here is the max number of data (in octet) that can be downloaded from a link.
        # (To download a font or an icon for example)
        "content-length": 5 * 1024 ** 2
    }

    # A dict that represents the default values of each option.
    DEFAULT = {
        "w": 800,
        "h": 480,
        "bg_color": "white",
        "bar_h": 40,
        "bar_color": "black",
        "tab_color": "white",
        "tab_text_color": "black",
        "tab_font": "fonts/consolas-italic.ttf",
        "tab_font_size": 14,
        "show_blur": False,
        "blur_color": "black",
        "blur_radius": 10,
        "show_tab_line": False,
        "tab_line_color": "black",
        "tab_line_width": 3,
        # Here, the default value is the programming language icon if found in assets/icons folder.
        "language_icon": "icons/{language}.png",
        "close_icon": "icons/close.png",
        "icon_size": (25, 25),
        "spacing": 10,
        "margins": 20,
        "code_font": "fonts/consolas.ttf",
        "code_font_size": 14,
        "code_line_padding": 10,
        "code_style": "default"
    }

    def __init__(self, args: dict):
        """
        Parameters
        ----------
        (Check ImageCode.DEFAULT dict for default values of parameters and ImageCode.LIMIT for their max values.)
        :param int w: Width of image.
        :param int h: Height of image.
        :param Union[str, tuple, list] bg_color: Background color of image.

        :param int bar_h: Height of bar.
        :param Union[str, tuple, list] bar_color: Color of bar.

        :param int tab_font_size: Size of font used in text of tab.
        :param str tab_font: Url of font used for text inside tab.
        :param str tab_name: Name of tab.
        :param Union[str, tuple, list] tab_color: Color of tab.
        :param Union[str, tuple, list] tab_text_color: Color of text inside tab.

        :param str code: The actual code.
        :param str language: The programming language used in the code.

        :param bool show_blur: Verify if we should render the dropshadow or not.
        :param int blur_radius: Radius of the blur of dropshadow.
        :param Union[str, tuple, list] blur_color: Color of dropshadow.

        :param bool show_tab_line: Verify if we should render the line or not.
        :param int tab_line_width: Width of the underline of tab.
        :param Union[str, tuple, list] tab_line_color: Color of the underline of tab.

        :param str language_icon: Url of icon used for representing the programming language used in the code.
        :param str close_icon: Url of icon used for representing the close button.
        :param Union[tuple, list] icon_size: Size of language icon and close_icon.

        :param int spacing: Spacing between the icons and the text of tab.
        :param int margins: Margins between the icons and rectangle of tab.

        :param str code_font: Url of font used in the code.
        :param int code_font_size: Size of font used in the code
        :param int code_line_padding: The spacing between each line of text
        :param str code_style: Style of code (in pygments's styles).
        """
        default = self.DEFAULT
        limit = self.LIMIT
        language = args.get("language")

        # Image properties
        # ----------
        w = args.get("w", default["w"])
        if not 400 <= w <= limit["w"]:
            raise ValueError(f"Width is negative, inferior to 400 or exceeds the limit. ({limit['w']})")

        h = args.get("h", default["h"])
        if not 240 <= h <= limit["h"]:
            raise ValueError(f"Height is negative, inferior to 240 or exceeds the limit. ({limit['h']})")

        self.bg_color = args.get("bg_color", default["bg_color"])
        if not self.check_color(self.bg_color):
            raise ValueError("bg_color is not a valid color.")

        # ------------------------------

        # DropShadow properties
        # ------------------------------
        self.blur_color = args.get("blur_color", default["blur_color"])
        if not self.check_color(self.blur_color):
            raise ValueError("blur_color is not a valid color.")

        self.blur_radius = args.get("blur_radius", default["blur_radius"])
        if not 0 < self.blur_radius <= limit["blur_radius"]:
            raise ValueError(f"blur_radius is negative or exceeds the limit. ({limit['blur_radius']})")

        self.show_blur = args.get("show_blur", default["show_blur"])

        # ------------------------------

        # Bar properties
        # ------------------------------
        self.bar_size = (w, args.get("bar_h", default["bar_h"]))
        if not 0 < self.bar_size[1] <= limit["bar_h"]:
            raise ValueError(f"bar_h is negative or exceeds the limit. ({limit['bar_h']})")

        self.bar_color = args.get("bar_color", default["bar_color"])
        if not self.check_color(self.bar_color):
            raise ValueError("bar_color is not a valid color.")

        # ------------------------------

        # Tab properties
        # ------------------------------
        icon_size = args.get("icon_size", default["icon_size"])
        if not 0 < sum(icon_size) <= sum(limit["icon_size"]):
            raise ValueError(f"sum of icon_size is negative or exceeds the limit. ({limit['icon_size']})")

        # Getting the close icon here
        icon = self.get(args.get("close_icon", default["close_icon"]))
        if not icon:
            raise ResourceNotFoundError(f"Can't find {args.get('close_icon')}.")

        self.close_icon = Image.open(icon) \
            .convert("RGBA") \
            .resize(icon_size)

        icon = self.get(args.get("language_icon", default["language_icon"].format(language=language)))
        if not icon:
            raise ResourceNotFoundError(f"Can't find {args.get('language_icon')}.")

        self.language_icon = Image.open(icon).convert("RGBA").resize(icon_size)

        self.spacing = args.get("spacing", default["spacing"])
        if not 0 < self.spacing <= limit["spacing"]:
            raise ValueError(f"spacing is negative or exceeds the limit. ({limit['spacing']})")

        self.margins = args.get("margins", default["margins"])
        if not 0 < self.margins <= limit["margins"]:
            raise ValueError(f"margins is negative or exceeds the limit. ({limit['margins']})")

        self.tab_color = args.get("tab_color", default["tab_color"])
        if not self.check_color(self.tab_color):
            raise ValueError("tab_color is not a valid color.")

        self.tab_text_color = args.get("tab_text_color", default["tab_text_color"])
        if not self.check_color(self.tab_text_color):
            raise ValueError("tab_text_color is not a valid color.")

        self.tab_line_color = args.get("tab_line_color", default["tab_line_color"])
        if not self.check_color(self.tab_line_color):
            raise ValueError("tab_line_color is not a valid color.")

        self.tab_line_width = args.get("tab_line_width", default["tab_line_width"])
        if not 0 < self.tab_line_width <= limit["tab_line_width"]:
            raise ValueError(f"tab_line_width is negative or exceeds the limit. ({limit['tab_line_width']})")

        self.show_tab_line = args.get("show_tab_line", default["show_tab_line"])
        tab_font = self.get(args.get("tab_font", default["tab_font"]))
        if tab_font is None:
            raise ResourceNotFoundError(f"Can't find {args.get('tab_font')}.")

        tab_font_size = args.get("tab_font_size", default["tab_font_size"])
        if not 6 < tab_font_size <= limit["tab_font_size"]:
            raise ValueError(f"tab_font_size is negative, inferior to 6 or exceeds the limit. ({limit['tab_font_size']})")

        self.tab_font = ImageFont.truetype(tab_font, tab_font_size)
        self.tab_name = args.get("tab_name", "")
        if not self.tab_name or not 0 < len(self.tab_name) <= limit["tab_name"]:
            raise ValueError(f"tab_name is empty or his length exceeds the limit. ({limit['tab_name']})")

        # ------------------------------

        # Code properties
        # ------------------------------
        self.code = args.get("code", "")
        if not self.code or not 0 < len(self.code) <= limit["code"]:
            raise ValueError(f"code is empty or his length exceeds the limit. ({limit['code']})")

        self.code_font = self.get(args.get("code_font", default["code_font"]), False)
        if self.code_font is None:
            raise ResourceNotFoundError(f"Can't find {args.get('code_font')}.")

        self.code_font_size = args.get("code_font_size", default["code_font_size"])
        if not 6 < self.code_font_size <= limit["code_font_size"]:
            raise ValueError(f"code_font_size is negative, inferior to 6 or exceeds the limit. "
                             f"({limit['code_font_size']})")

        self.code_line_pad = args.get("code_line_padding", default["code_line_padding"])
        if not 5 < self.code_line_pad <= limit["code_line_padding"]:
            raise ValueError(f"code_line_padding is negative, inferior to 5 or exceeds the limit. "
                             f"({limit['code_line_padding']})")

        self.code_style = get_style_by_name(args.get("code_style", default["code_style"]))

        self.formatter = ImageFormatter(font_name=self.code_font, font_size=self.code_font_size,
                                        line_number_bg=self.bg_color, line_pad=self.code_line_pad,
                                        style=self.code_style)
        self.formatter.background_color = self.bg_color

        self.lexer = guess_lexer(self.code) if not language else get_lexer_by_name(language)

        # ------------------------------

        self.image = Image.new("RGB", (w, h), self.bg_color)
        self.renderer = ImageDraw.Draw(self.image)

    def get(self, url_or_path: str, verif: bool = True):
        """
        Gets content with a GET request if url_or_path parameter is a valid url or opens a file stored in a directory.

        Parameters
        ----------
        :param str url_or_path: The url to make a GET request or a path that refers to a file stored in the filesystem.
        :param bool verif: A bool that says if we should return url_or_path even if the verifications are false.
        It is used for font_name argument of ImageFormatter class when url_or_path can be a font name stored in
        registry.

        :return A file-like object, None or the parameter if verif is False.
        """
        path = f"{self.assets_dir}{url_or_path}"
        if os.path.isfile(path):
            return open(path, "rb")
        elif not is_url(url_or_path):
            return url_or_path if not verif else None

        try:
            with requests.get(url_or_path, stream=True) as request:
                if request.status_code != 200 or int(request.headers.get("Content-Length")) > self.LIMIT["content-length"]:
                    return None

                return BytesIO(request.content)
        except RequestException:
            return None

    def draw_bar(self):
        """
        Draws the bar and the dropshadow if allowed in the image.
        """
        if self.show_blur:
            with Image.new("RGBA", self.image.size, (0, 0, 0, 0)) as black_img:
                if isinstance(self.blur_color, list):
                    self.blur_color = tuple(self.blur_color)

                ImageDraw.Draw(black_img).rectangle(((0, 0), self.bar_size), fill=self.blur_color)
                black_img = black_img.filter(ImageFilter.GaussianBlur(self.blur_radius))
                self.image.paste(black_img, (0, 0), black_img)

        self.renderer.rectangle(((0, 0), self.bar_size), fill=self.bar_color)

    def draw_tab(self):
        """
        Draws the tab with the language icon, the close icon and the name of tab in the image.
        """
        text_size = self.renderer.textsize(self.tab_name, font=self.tab_font)

        tab_size = (
            (text_size[0] + self.close_icon.size[0] + self.language_icon.size[0] + self.spacing * 2 + self.margins),
            self.bar_size[1]
        )
        tab_pos = (0, 0)
        tab_text_pos = ((tab_size[0] - text_size[0]) // 2, (tab_size[1] - text_size[1]) // 2)
        tab_rect = (tab_pos, tab_size)

        close_icon_pos = (tab_text_pos[0] + text_size[0] + self.spacing, tab_text_pos[1])
        language_icon_pos = (
            tab_text_pos[0] - self.language_icon.size[0] - self.spacing,
            tab_text_pos[1] - tab_text_pos[1] // 2
        )

        if isinstance(self.tab_color, list):
            self.tab_color = tuple(self.tab_color)

        self.renderer.rectangle(tab_rect, fill=self.tab_color)
        self.renderer.text(tab_text_pos, self.tab_name, font=self.tab_font, fill=self.tab_text_color)
        if self.show_tab_line:
            if isinstance(self.tab_line_color, list):
                self.tab_line_color = tuple(self.tab_line_color)

            self.renderer.line(((0, tab_size[1]), tab_size), fill=self.tab_line_color, width=self.tab_line_width)

        self.image.paste(self.close_icon, close_icon_pos, self.close_icon)
        self.image.paste(self.language_icon, language_icon_pos, self.language_icon)

    def draw_code(self):
        """
        Draws the code in the image.
        The highlighted code is generated in an another image with pygments, and pasted into the main image.
        """
        code_pos = (0, self.bar_size[1] + self.blur_radius * 2)

        with BytesIO(highlight(self.code, self.lexer, self.formatter)) as out:
            with Image.open(out) as code_image:
                self.image.paste(code_image, code_pos)

    def check_color(self, color) -> bool:
        """
        Function to check if color argument is a valid color value.
        It relies on the matplotlib.colors.is_color_like function.

        :param color: A color value.
        :return: True if color is a valid color value else False.
        """
        if type(color) in (list, tuple) and len(color) >= 3:
            color = [color[i] / 255 for i in range(3)]
            if len(color) >= 4:
                color[3] /= 255

        return is_color_like(color)

    def generate(self, path=None, img_format=None):
        """
        Function that calls all the drawing functions to generate the image.

        :param str path: Directory of image.
        :param img_format: Format of image.

        :return: The path or an io.BytesIO object if path is None.
        """
        self.draw_bar()
        self.draw_tab()
        self.draw_code()

        fp = path if path else BytesIO()
        self.image.save(fp, format=img_format)
        self.close()
        return fp

    def close(self):
        self.image.close()
        self.language_icon.close()
        self.close_icon.close()

# Add support for command-line usage later.

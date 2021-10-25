from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pygments import highlight
from pygments.formatters.img import ImageFormatter
from pygments.lexers import get_lexer_by_name


class ImageCode:

    def __init__(
            self,
            size: list,
            bg_color: str,
            bar_height: int, bar_color: str,
            tab_color: str, tab_text_color: str, tab_font: str, tab_name: str,
            code_path: str, language: str,
            blur_color: str, show_blur: bool, blur_radius: int,
            tab_line_color: str, tab_line_width: int, show_tab_line: bool,
            language_icon_path: str, close_icon_path: str = "assets/close.png",
            spacing: int = 10, margins: int = 20, tab_font_size: int = 14,
            code_font: str = "consolas", code_font_size: int = 14, code_line_padding: int = 10,
            code_style: str = "default",
    ):
        self.bg_color = bg_color

        # Blur propreties
        self.blur_color = blur_color
        self.blur_radius = blur_radius
        self.show_blur = show_blur

        # Bar propreties
        self.bar_size = (size[0], bar_height)
        self.bar_color = bar_color

        # Tab propreties
        icon_size = (26, 26)
        self.close_icon = Image.open(close_icon_path).convert("RGBA").resize(icon_size)
        self.language_icon = Image.open(language_icon_path).convert("RGBA").resize(icon_size)

        self.spacing = spacing
        self.margins = margins

        self.tab_color = tab_color
        self.tab_text_color = tab_text_color
        self.tab_line_color = tab_line_color
        self.tab_line_width = tab_line_width
        self.show_tab_line = show_tab_line
        self.tab_font = ImageFont.truetype(tab_font, tab_font_size)
        self.tab_name = tab_name

        # Code propreties
        self.code_path = code_path
        self.code_font = code_font
        self.code_font_size = code_font_size
        self.code_line_pad = code_line_padding
        self.code_style = code_style
        self.formatter = ImageFormatter(font_name=self.code_font, font_size=self.code_font_size,
                                        line_number_bg=self.bg_color, line_pad=self.code_line_pad,
                                        style=self.code_style)
        self.formatter.background_color = self.bg_color

        self.lexer = get_lexer_by_name(language)

        self.image = Image.new("RGB", size, bg_color)
        self.renderer = ImageDraw.Draw(self.image)

    def draw_bar(self):
        if self.show_blur:
            with Image.new("RGBA", self.image.size, (0, 0, 0, 0)) as black_img:
                ImageDraw.Draw(black_img).rectangle(((0, 0), self.bar_size), fill=self.blur_color)
                black_img = black_img.filter(ImageFilter.GaussianBlur(self.blur_radius))
                self.image.paste(black_img, (0, 0), black_img)

        self.renderer.rectangle(((0, 0), self.bar_size), fill=self.bar_color)

    def draw_tab(self):
        text_size = self.renderer.textsize(self.tab_name, font=self.tab_font)

        tab_size = (
            (text_size[0] + self.close_icon.size[0] + self.language_icon.size[0] + self.spacing * 2 + self.margins),
            self.bar_size[1])
        tab_pos = (0, 0)
        tab_text_pos = ((tab_size[0] - text_size[0]) // 2, (tab_size[1] - text_size[1]) // 2)
        tab_rect = (tab_pos, tab_size)

        close_icon_pos = (tab_text_pos[0] + text_size[0] + self.spacing, tab_text_pos[1])
        language_icon_pos = (
            tab_text_pos[0] - self.language_icon.size[0] - self.spacing, tab_text_pos[1] - tab_text_pos[1] // 2)

        self.renderer.rectangle(tab_rect, fill=self.tab_color)
        self.renderer.text(tab_text_pos, self.tab_name, font=self.tab_font, fill=self.tab_text_color)
        if self.show_tab_line:
            self.renderer.line(((0, tab_size[1]), tab_size), fill=self.tab_line_color, width=self.tab_line_width)

        self.image.paste(self.close_icon, close_icon_pos, self.close_icon)
        self.image.paste(self.language_icon, language_icon_pos, self.language_icon)

    def draw_code(self):
        code_pos = (0, self.bar_size[1] + self.blur_radius * 2)

        with open(self.code_path, "r") as code:
            with BytesIO(highlight(code.read(), self.lexer, self.formatter)) as out:
                with Image.open(out) as code_image:
                    self.image.paste(code_image, code_pos)

    def generate(self):
        self.draw_bar()
        self.draw_tab()
        self.draw_code()

        self.image.save("image.png")
        self.close()

    def close(self):
        self.image.close()
        self.language_icon.close()
        self.close_icon.close()

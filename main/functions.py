import io
import uuid
from zipfile import ZipFile

from PIL import ImageFont, ImageDraw


def place_field_on_image(template_img, top_left_corner, bottom_right_corner, my_text):
    draw = ImageDraw.Draw(template_img)
    top_left_corner = tuple(top_left_corner)
    bottom_right_corner = tuple(bottom_right_corner)
    print("field = ", my_text, "top_left_corner = ", top_left_corner, " bottom_right_corner = ", bottom_right_corner)
    box_width, box_height = (bottom_right_corner[0] - top_left_corner[0], bottom_right_corner[1] - top_left_corner[1])
    text_size = box_height
    font = ImageFont.truetype("fonts/ComicShannsMonoNerdFontMono-Regular.otf", text_size)
    # draw.rectangle((top_left_corner, bottom_right_corner), fill= "Black")
    text_width, text_height = font.getbbox(my_text)[2:]
    while text_width > box_width or text_height > box_height:
        text_size -= 1
        font = ImageFont.truetype("fonts/ComicShannsMonoNerdFontMono-Regular.otf", size= text_size)
        text_width, text_height = font.getbbox(my_text)[2:]
    start_co_ordinate = ((top_left_corner[0] + ((box_width - text_width) / 2)), (top_left_corner[1] + ((box_height - text_height) / 2)))
    draw.text(start_co_ordinate, my_text, font=font, fill="Black")
    return template_img

def process_images(images):
    for image_dict in images:
        buffer_obj = io.BytesIO()
        image_dict["object"].save(buffer_obj, format= "JPEG")
        image_dict["object"].close()
        del image_dict["object"]
        image_dict["buffer"] = buffer_obj
    return images

def create_zip_file(images, user):
    images = process_images(images)
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_file:
        for image_dict in images:
            zip_file.writestr(image_dict["file_name"], image_dict["buffer"].getvalue())
    zip_file_path = "/home/phenom/PycharmProjects/Certificate Generator/media/"
    user_id = user.id
    print("user_id = ",user_id)
    file_name = f"{user_id}-" + str(uuid.uuid4().hex) + ".zip"
    zip_file_path = zip_file_path + file_name
    with open(zip_file_path, "wb") as my_zip_file:
        my_zip_file.write(zip_buffer.getvalue())
    return file_name

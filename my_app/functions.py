import io
import os
import uuid
from zipfile import ZipFile

from PIL import ImageFont, ImageDraw, Image

from certificate_generator.settings import BASE_DIR

def place_field_on_image(template_img, field_info_list, my_text, font_name, text_color= "Black"):
    draw = ImageDraw.Draw(template_img)
    fit_text = ""
    text_to_place = my_text
    for field_info in field_info_list:
        top_left_corner = tuple(field_info['top_left_corner'])
        bottom_right_corner = tuple(field_info['bottom_right_corner'])
        alignment = field_info["alignment"].lower()
        anchor = None
        box_width, box_height = (bottom_right_corner[0] - top_left_corner[0], bottom_right_corner[1] - top_left_corner[1])
        text_size = box_height
        font = ImageFont.truetype(font_name, text_size)
        for word in text_to_place.split(" "):
            text_width, text_height = font.getbbox(fit_text)[2:]
            if len(field_info_list) == 1:
                while text_width > box_width:
                    text_size -= 1
                    font = ImageFont.truetype(font_name, text_size)
                    text_width, text_height = font.getbbox(fit_text)[2:]

                start_co_ordinate = None
                if alignment == "left":
                    start_co_ordinate = ((top_left_corner[0] + bottom_right_corner[0])/2, bottom_right_corner[1])
                    anchor = "lb"
                elif alignment == "right":
                    start_co_ordinate = bottom_right_corner
                    anchor = "rb"
                elif alignment == "center":
                    start_co_ordinate = ((top_left_corner[0] + bottom_right_corner[0])/2, top_left_corner[1])
                    anchor = "mb"
                draw.text(start_co_ordinate, w, text_color, font=font)



    print(field_info_list)
    if len(field_info_list) == 1:
        top_left_corner = tuple(field_info_list[0]["top_left_corner"])
        bottom_right_corner = tuple(field_info_list[0]["bottom_right_corner"])
        alignment = field_info_list[0]["alignment"].lower()
        anchor = None
        if alignment == "left":
            anchor = "lb"
        elif alignment == "right":
            anchor = "rb"
        elif alignment == "center":
            anchor = "mb"
        (box_width, box_height) = (bottom_right_corner[0] - top_left_corner[0], bottom_right_corner[1] - top_left_corner[1])
        text_size = box_height
        font = ImageFont.truetype(font_name, text_size)
        text_width, text_height = font.getbbox(my_text)[2:]
        while text_width > box_width or text_height > box_height:
            text_size -= 1
            font = ImageFont.truetype(font_name, text_size)
            text_width, text_height = font.getbbox(my_text)[2:]
        start_co_ordinate = ((top_left_corner[0] + bottom_right_corner[0])/2, bottom_right_corner[1])
        # draw.point(start_co_ordinate, fill="Red")
        if alignment == "left":
            start_co_ordinate = (top_left_corner[0], bottom_right_corner[1])
        elif alignment == "right":
            start_co_ordinate = bottom_right_corner
        elif alignment == "center":
            start_co_ordinate = ((top_left_corner[0] + bottom_right_corner[0]) / 2, bottom_right_corner[1])
        draw.text(start_co_ordinate, my_text, fill= text_color, font=font, anchor= anchor)
        return template_img
    else:
        for field_info_dict in field_info_list:
            top_left_corner = tuple(field_info_dict['top_left_corner'])
            bottom_right_corner = tuple(field_info_dict['bottom_right_corner'])
            alignment = field_info_dict['alignment']
            box_width, box_height = (
            bottom_right_corner[0] - top_left_corner[0], bottom_right_corner[1] - top_left_corner[1])
            text_size = box_height
            font = ImageFont.truetype(font_name, text_size)
            text_width, text_height = font.getbbox(my_text)[2:]
            if text_width < box_width:
                pass
            else:
                if fit_text and text_to_place.startswith(fit_text):
                    text_to_place = my_text.replace(fit_text, "")
                for text in text_to_place.split(" "):
                    if abs(text_width - box_width) < 10:
                        start_co_ordinate = (top_left_corner[0], top_left_corner[1])
                        # draw.rectangle((top_left_corner, bottom_right_corner), fill= "Black")
                        draw.text(start_co_ordinate, fit_text, fill= text_color, font=font)
                        break
                    fit_text += text + " "
                    text_width, text_height = font.getbbox(fit_text)[2:]
                text_to_place = my_text.replace(fit_text, "")
                fit_text = ""
    return template_img

def process_images(images):
    for image_dict in images:
        print(f"{image_dict}?????????????????????")
        buffer_obj = io.BytesIO()
        image_dict["object"].save(buffer_obj, format= "JPEG")
        image_dict["object"].close()
        del image_dict["object"]
        image_dict["buffer"] = buffer_obj
    return images

def create_zip_file(images, user):
    images = process_images(images)
    zip_buffer = io.BytesIO()
    last_image = None
    with ZipFile(zip_buffer, "w") as zip_file:
        for image_dict in images:
            zip_file.writestr(image_dict["file_name"], image_dict["buffer"].getvalue())
        last_image = Image.open(io.BytesIO(image_dict["buffer"].getvalue()))
    user_id = user.id
    if not os.path.exists(f"{BASE_DIR}/media/zips/id-{user_id}/"):
        os.makedirs("media" + "/" + "zips" + "/" + f"id-{user_id}")
    zip_file_path = os.path.join(BASE_DIR, "media", "zips", f"id-{user_id}", f"{user_id}-")
    unique_id = str(uuid.uuid4().hex)
    file_name= f"{user_id}-" + unique_id
    file_path = f"/zips/id-{user_id}/" + f"{user_id}-" + unique_id + ".zip"
    zip_file_path = zip_file_path + unique_id + ".zip"
    with open(zip_file_path, "wb") as my_zip_file:
        my_zip_file.write(zip_buffer.getvalue())

    return file_path, file_name, last_image


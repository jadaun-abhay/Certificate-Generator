import io
import os
import uuid
from zipfile import ZipFile

from PIL import ImageFont, ImageDraw

from certificate_generator.settings import BASE_DIR

def place_field_on_image(template_img, field_info_list, my_text, text_color= "Black"):
    draw = ImageDraw.Draw(template_img)
    fit_text = ""
    text_to_place = my_text
    if len(field_info_list) == 1:
        top_left_corner = tuple(field_info_list[0]["top_left_corner"])
        bottom_right_corner = tuple(field_info_list[0]["bottom_right_corner"])
        alignment = field_info_list[0]["alignment"]
        (box_width, box_height) = (bottom_right_corner[0] - top_left_corner[0], bottom_right_corner[1] - top_left_corner[1])
        text_size = box_height
        font = ImageFont.truetype("fonts/TinosNerdFont-Italic.ttf", text_size)
        text_width, text_height = font.getbbox(my_text)[2:]
        while text_width > box_width or text_height > box_height:
            text_size -= 1
            font = ImageFont.truetype("fonts/TinosNerdFont-Italic.ttf", text_size)
            text_width, text_height = font.getbbox(my_text)[2:]
        start_co_ordinate = ((top_left_corner[0] + ((box_width - text_width) / 2)), (top_left_corner[1] + (box_height - text_height)))
        draw.text(start_co_ordinate, my_text, fill= text_color, font=font)
        return template_img
    else:
        print("Another Certificate")
        for field_info_dict in field_info_list:
            top_left_corner = tuple(field_info_dict['top_left_corner'])
            bottom_right_corner = tuple(field_info_dict['bottom_right_corner'])
            alignment = field_info_dict['alignment']
            box_width, box_height = (
            bottom_right_corner[0] - top_left_corner[0], bottom_right_corner[1] - top_left_corner[1])
            text_size = box_height
            font = ImageFont.truetype("fonts/TinosNerdFont-Italic.ttf", text_size)
            text_width, text_height = font.getbbox(my_text)[2:]
            if text_width < box_width:
                pass
                # start_co_ordinate = ((top_left_corner[0] + ((box_width - text_width) / 2)), (top_left_corner[1] + (box_height - text_height)))
                # draw.text(start_co_ordinate, my_text, fill= text_color, font=font)
                # return template_img
            else:
                print("#################")
                print("text_to_place = = ", text_to_place, "fit_text = = ", fit_text)
                if fit_text and text_to_place.startswith(fit_text):
                    text_to_place = my_text.replace(fit_text, "")
                for text in text_to_place.split(" "):
                    if abs(text_width - box_width) < 10 or abs(text_width - box_width) < 50:
                        start_co_ordinate = (top_left_corner[0], top_left_corner[1])
                        draw.rectangle((top_left_corner, bottom_right_corner), fill= "Black")
                        draw.text(start_co_ordinate, fit_text, fill= text_color, font=font)
                        print("text : ", text)
                        print("text_to_place:", text_to_place)
                        text_to_place = my_text.replace(text_to_place, "")
                        print("new text: " + text_to_place)
                        # fit_text = " "
                        break
                    fit_text += text + " "
                    text_width, text_height = font.getbbox(fit_text)[2:]
                    print("fit_text =", fit_text)
                    print("text_to_place =", text_to_place)
                text_to_place = my_text.replace(fit_text, "")
                fit_text = ""
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
    user_id = user.id
    if not os.path.exists(f"{BASE_DIR}/media/zips/id-{user_id}/"):
        os.makedirs("media" + "/" + "zips" + "/" + f"id-{user_id}")
    zip_file_path = os.path.join(BASE_DIR, "media", "zips", f"id-{user_id}", f"{user_id}-")
    unique_id = str(uuid.uuid4().hex)
    file_path = f"/zips/id-{user_id}/" + f"{user_id}-" + unique_id + ".zip"
    zip_file_path = zip_file_path + unique_id + ".zip"
    with open(zip_file_path, "wb") as my_zip_file:
        my_zip_file.write(zip_buffer.getvalue())

    return file_path


import csv
import datetime
import json
import os
import re
import openpyxl

from PIL import Image
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.db.models import F
from django.http import JsonResponse, QueryDict

from certificate_generator.settings import BASE_DIR
from my_app.functions import place_field_on_image, create_zip_file
from my_app.models import User, BaseModel, UserZips, UserTemplates, UserUploads, UserFolderStructure

Status = BaseModel.Status

# Create your views here.

def register(request):
    if request.method == "POST":
        data = request.POST
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        middle_name = data.get("middle_name")
        email = data.get("email")
        password = data.get("password")
        if not (first_name and email and password):
            res = {"error": "All fields are required"}
            return JsonResponse(res, status=400)
        first_name = first_name.capitalize()
        if not re.match(r'\b[a-z|A-Z]{2,25}', first_name):
            res = {"error": "Invalid first name. First name must be of characters"}
            return JsonResponse(res, status= 400)
        elif not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email):
            res = {"error": "Invalid email"}
            return JsonResponse(res, status= 400)
        elif not re.match(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$", password):
            res = {"error": "Password must contain at least 8 characters with at least 1 uppercase, 1 lowercase, 1 number, and 1 special character"}
            return JsonResponse(res, status= 400)
        if middle_name:
            middle_name = middle_name.capitalize()
            if not re.match(r"\b[a-z|A-Z]{2,25}", middle_name):
                res = {"error": "Invalid middle_name. Middle_name must be of characters"}
                return JsonResponse(res, status= 400)
        else:
            middle_name = ""
        if last_name:
            last_name = last_name.capitalize()
            print(last_name)
            if not re.match(r"\b[a-z|A-Z]{2,25}", last_name):
                res = {"error": "Invalid last_name. Last name must be of characters"}
                return JsonResponse(res, status= 400)
        else:
            last_name = ""
        password = make_password(password)
        user, status = User.objects.exclude(status= Status.DELETED).get_or_create(email= email, defaults= {"first_name": first_name, "middle_name": middle_name, "last_name": last_name, "status": Status.CREATED, "password": password})
        if not status:
            res = {"error": f"User {user.email} already exists"}
            return JsonResponse(res, status= 400)
        else:
            res = {"message": f"User {user.email} created successfully"}
            return JsonResponse(res, status= 201)
    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)

def login_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        if not email:
            res = {"error": "Email is required !!!"}
            return JsonResponse(res, status=400)
        elif not password:
            res = {"error": "Password is required !!!"}
            return JsonResponse(res, status=400)
        elif not (email and password):
            res = {"error": "All fields are required !!!"}
            return JsonResponse(res, status= 400)
        else:
            if not bool(re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email)):
                res = {"error": "Email is invalid. Must be like 'abc@example.com'"}
                return JsonResponse(res, status= 400)
            elif not bool(re.match(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$', password)):
                res = {"error": "Password must be at least 8 characters long and must contain at least a special and uppercase character"}
                return JsonResponse(res, status= 400)
            else:
                user = User.objects.filter(email= email).exclude(status= Status.DELETED)
                if not user.exists():
                    res = {"error": "Email is not registered"}
                    return JsonResponse(res, status= 400)
                user = authenticate(email= email, password= password)
                if user:
                    login(request, user)
                    res = {"message": "Login is successful"}
                    return JsonResponse(res, status= 200)
                else:
                    res = {"error": "Incorrect password"}
                    return JsonResponse(res, status= 400)
    elif request.method == "GET":
        if request.user.is_authenticated:
            res = {"message": 'Login is successful'}
            return JsonResponse(res, status= 200)
        else:
            res = {"error": "Login is required !!!"}
            return JsonResponse(res, status= 400)
    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)

def logout_user(request):
    if not request.user.is_authenticated:
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    if request.method == "POST":
        logout(request)
        res = {"message": "Logout is successful"}
        return JsonResponse(res, status= 200)
    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)

def drive_structure(request, command= None):
    if not request.user.is_authenticated:
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    if request.method == "POST":
        data = request.POST
        attached_file = request.FILES
        name = data.get("name")
        is_file = data.get("is_file")
        parent_folder_id = data.get("parent_id")
        file = attached_file.get("file")
        if is_file:
            if not file:
                res = {"error": "File is required !!!"}
                return JsonResponse(res, status= 400)
            parent_folder_instance = None
            if not parent_folder_id:
                parent_folder_instance, status = UserFolderStructure.objects.get_or_create(name= "home", parent= None, defaults= {"user_id": request.user.id})
            else:
                parent_folder_instance = UserFolderStructure.objects.filter(id= parent_folder_id)
                if not parent_folder_instance.exists():
                    res = {"error": "Parent folder does not exist !!!"}
                    return JsonResponse(res, status= 404)
            file_instance = UserUploads(user= request.user, uploaded_file_path= file.name, parent_directory= parent_folder_instance, uploded_file_name= file.name)
            res = {"message": "Upload is successful"}
            return JsonResponse(res, status= 201)
        home_directory = None
        if not parent_folder_id:
            home_directory, presence = UserFolderStructure.objects.filter(user_id= request.user.id, parent= None).exclude(status= Status.DELETED).get_or_create(user_id= request.user.id, name= "home", parent= None, defaults= {"status": Status.CREATED})
            new_directory, status = UserFolderStructure.objects.get_or_create(user_id= request.user.id, name= name, parent= home_directory, defaults= {"status": Status.CREATED})
            if not status:
                res = {"error": "Directory with same name already exists !!!"}
                return JsonResponse(res, status= 409)
            else:
                res = {"message": "Directory created successfully !!!"}
                return JsonResponse(res, status= 201)
        else:
            parent_folder_instance = UserFolderStructure.objects.filter(user= request.user.id, id= parent_folder_id).exclude(status= Status.DELETED)
            if not parent_folder_instance.exists():
                res = {"error": "Parent folder does not exist !!!"}
                return JsonResponse(res, status= 404)
            parent_folder_instance = parent_folder_instance.first()
            new_directory, presence = UserFolderStructure.objects.get_or_create(user_id= request.user.id, name= name, parent= parent_folder_instance, defaults= {"status": Status.CREATED})
            if not presence:
                res = {"error": "Directory with same name already exists !!!"}
                return JsonResponse(res, status= 409)
            res = {"message": "Directory created successfully !!!"}
            return JsonResponse(res, status= 201)
    elif request.method == "GET":
        directory_id = request.GET.get("id")
        if not directory_id:
            directories = list(UserFolderStructure.objects.filter(user_id= request.user.id, parent__name= "home").exclude(status= Status.DELETED).values(child_directory_id= F("id"), child_directory_name= F("name")))
            path = "home/"
            uploaded_files = list(UserUploads.objects.filter(parent_directory__name= "home", user_id= request.user.id).exclude(status= Status.DELETED).values(file_id= F("id"), file_path= F("uploaded_file_path"), file_name= F("uploaded_file_name")))
            templates = list(UserTemplates.objects.filter(user_id= request.user.id, parent_directory__name= "home").exclude(status= Status.DELETED).values(template_id= F("id"), template_file_name= F("template_name"), template_file_path= F("template_file")))
            zips = list(UserZips.objects.filter(user_id= request.user.id, parent_directory__name= "home").exclude(status= Status.DELETED).values(zip_id= F("id"), zip_file_name= F("zip_name"), zip_file_path= F("zip_file")))
            previous_directory_id = None
            res = {"message": "success", "path": path, "previous_directory_id": previous_directory_id, "child_directories": directories, "uploaded_files": uploaded_files, "templates": templates, "zips": zips}
            return JsonResponse(res, status= 200)
        directory_instance = UserFolderStructure.objects.filter(id= directory_id).exclude(status= Status.DELETED)
        if not directory_instance.exists():
            res = {"error": "Directory does not exist !!!"}
            return JsonResponse(res, status= 404)
        directory_instance = directory_instance.first()
        child_directories = list(UserFolderStructure.objects.filter(user_id= request.user.id, parent__id= directory_id).exclude(status= Status.DELETED).values(child_directory_id= F("id"), child_directory_name= F("name")))
        path_info = directory_instance.get_directory_path()
        print(path_info)
        uploaded_files = list(UserUploads.objects.filter(parent_directory= directory_instance, user_id= request.user.id).exclude(status= Status.DELETED).values(file_id= F("id"), file_path= F("uploaded_file_path"), file_name= F("uploaded_file_name")))
        templates = list(UserTemplates.objects.filter(user_id= request.user.id, parent_directory= directory_instance).exclude(status= Status.DELETED).values(template_id= F("id"), template_file_name= F("template_name"), template_file_path= F("template_file")))
        zips = list(UserZips.objects.filter(user_id= request.user.id, parent_directory= directory_instance).exclude(status= Status.DELETED).values(zip_id= F("id"), zip_file_name= F("zip_name"), zip_file_path= F("zip_file")))
        res = {"message": "success", "path_info": path_info, "child_directories": child_directories, "uploaded_files": uploaded_files, "templates": templates, "zips": zips}
        return JsonResponse(res, status= 200)
    elif request.method == "PATCH":
        data = json.loads(request.body)
        print(data)
        file_id = data.get("id")
        folder_id = data.get("folder_id")
        source_folder_id = data.get("parent_id")
        name = data.get("name")
        destination_folder_id = data.get("destination_folder_id")
        if command.lower() == "rename":
            if folder_id:
                if not name:
                    res = {"error": "New name for directory is not given !!!"}
                    return JsonResponse(res, status= 400)
                print(name)
                check = UserFolderStructure.objects.filter(user_id= request.user.id, id= folder_id).exclude(status= Status.DELETED).update(status= Status.UPDATED, updation_timestamp= datetime.datetime.now(), name= name)
                if not check:
                    res = {"error": "Updation failed"}
                    return JsonResponse(res, status= 409)
                res = {"message": "Directory renamed successfully !!!"}
                return JsonResponse(res, status= 200)
            elif file_id:
                if not name:
                    res = {"error": "New name for file is not given !!!"}
                    return JsonResponse(res, status= 400)
                pass
            res = {"error": "File_id or Folder_id is not given"}
            return JsonResponse(res, status= 404)
        elif command.lower() == "move":
            if folder_id:
                if not source_folder_id and not destination_folder_id:
                    res = {"error": "source and destination for folder is not provided !!!"}
                    return JsonResponse(res, status= 400)
                folder = UserFolderStructure.objects.filter(user_id= request.user.id, parent_id= source_folder_id).exclude(status= Status.DELETED)
                if not folder.exists():
                    res = {"error": "Folder does not exists in the source directory !!!"}
                    return JsonResponse(res, status= 404)
                folder_instance = folder.first()
                check_duplicate = UserFolderStructure.objects.filter(user_id= request.user.id, parent_id= destination_folder_id, name= folder_instance.name).exclude(status= Status.DELETED)
                if check_duplicate.exists():
                    res = {"error": "A directory with the same name already exists in destination directory !!!"}
                    return JsonResponse(res, status= 409)
                folder.update(status= Status.CREATED, updation_timestamp= datetime.datetime.now(), parent_id= destination_folder_id)
                res = {"message": "Directory moved successfully !!!"}
                return JsonResponse(res, status= 200)
            elif file_id:
                pass
            res = {"error": "File_id or Folder_id is not given !!!"}
            return JsonResponse(res, status= 400)
        elif command.lower() == "copy":
            pass
        res = {"error": "Invalid command !!!"}
        return JsonResponse(res, status= 400)
    elif request.method == "DELETE":
        data = QueryDict(request.body)
        directory_id = data.get("id")
        directory = UserFolderStructure.objects.filter(id= directory_id).exclude(status= Status.DELETED)
        if not directory.exists():
            res = {"error": "Directory does not exist !!!"}
            return JsonResponse(res, status= 404)
        directory.update(status= Status.DELETED, deletion_timestamp= datetime.datetime.now())
        res = {"message": "Directory deleted successfully !!!"}
        return JsonResponse(res, status= 200)

    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)

def zipify(request):
    if not request.user.is_authenticated:
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    if request.method == "POST":
        post_data = request.POST
        attached_files = request.FILES
        text_color = post_data.get("color")
        str_data = post_data.get("data")
        data = json.loads(str_data)
        box_info = data.get("data")
        if not box_info:
            res = {"error": "Data is required !!!"}
            return JsonResponse(res, status= 400)
        elif not attached_files:
            res = {"error": "No attached files"}
            return JsonResponse(res, status= 400)
        elif len(attached_files) != 2:
            res = {"error": "2 files are required"}
            return JsonResponse(res, status= 400)
        else:
            text_color = text_color[1:]
            if not text_color:
                text_color = "Black"
            else:
                text_color = tuple(int(text_color[i:i+2], 16) for i in (0, 2, 4))
            if not isinstance(box_info, list):
                res = {"error": "Field format data must be a list"}
                return JsonResponse(res, status= 400)
            field_set = {field_info["field_name"] for field_info in box_info}
            template = attached_files.get("template")
            if not template:
                res = {"error": "Template is required"}
                return JsonResponse(res, status= 400)
            certificate_file = attached_files.get("data_file")
            template_extension = None
            if template:
                template_extension = template.name.split(".")[-1]
                template_extension = template_extension.lower()
                content_type = template.content_type
                if template_extension not in settings.WHITELISTED_IMAGE_TYPES.keys():
                    res = {"error": "Invalid extension for template file"}
                    return JsonResponse(res, status= 400)
                elif content_type not in settings.WHITELISTED_IMAGE_TYPES.values():
                    res = {"error": "Invalid content type for template file"}
                    return JsonResponse(res, status= 400)
                template_path = f"{BASE_DIR}/media/templates/id-{request.user.id}/{template.name}"
                if not os.path.exists(template_path):
                    template_file = UserTemplates(user_id= request.user.id, template_file= template, status= Status.CREATED)
                    template_file.save()
            if certificate_file:
                extension = certificate_file.name.split(".")[-1]
                extension = extension.lower()
                content_type = certificate_file.content_type
                if extension not in settings.WHITELISTED_FILE_TYPES.keys():
                    res = {"error": "Invalid extension for data file"}
                    return JsonResponse(res, status= 400)
                elif content_type not in settings.WHITELISTED_FILE_TYPES.values():
                    res = {"error": "Invalid content type for data file"}
                    return JsonResponse(res, status= 400)
                else:
                    if extension == "json":
                        with certificate_file.open("rb") as json_file:
                            json_data = json.load(json_file)
                        certificate_list = json_data.get("data")
                        result = list()
                        i = 0
                        for certificate in certificate_list:
                            i += 1
                            template_path = os.path.join(BASE_DIR, "media", "templates", f"id-{request.user.id}", template.name)
                            template_img = Image.open(template_path).convert("RGB")
                            is_present = True
                            for field in certificate:
                                if not field in field_set:
                                    continue
                                invalid_field = [info_dict.get("field_name") for info_dict in box_info if info_dict.get("field_name") not in certificate]
                                if invalid_field:
                                    res = {"error": f"Invalid field [{invalid_field[0]}]"}
                                    return JsonResponse(res, status= 400)
                                field_info = [info_dict for info_dict in box_info if info_dict.get("field_name") == field]
                                template_img = place_field_on_image(template_img, field_info, certificate[field], text_color)

                                # for field_info in box_info:
                                #     if not field_info["field_name"] in certificate:
                                #         res = {"error": f"Invalid field_name [{field_info["field_name"]}]"}
                                #         return JsonResponse(res, status= 400)
                                #     if field == field_info["field_name"]:
                                #         is_present = True
                                #         print(f"{field} is placed")
                                #         bottom_right_corner = field_info["bottom_right_corner"]
                                #         top_left_corner = field_info["top_left_corner"]
                                #         template_img = place_field_on_image(template_img, top_left_corner, bottom_right_corner, certificate[field], text_color)
                            result.append({"file_name": f"image{i}.{template_extension}", "object": template_img, "extension": template_extension})
                        file_name = create_zip_file(result, request.user)
                        file = UserZips.objects.create(zip_file= file_name, user=request.user, status= Status.CREATED)
                        res = {"message": "Zip file created successfully", "file_id": file.id, "file_path": file_name}
                        return JsonResponse(res, status= 201)
                    elif extension == "csv":
                        with open(certificate_file.name, "r") as file:
                            csv_file = csv.DictReader(file)
                            result = list()
                            i = -1
                            for certificate in csv_file:
                                i += 1
                                template_path = os.path.join(BASE_DIR, "media", "template", f"id-{request.user.id}", template.name)
                                template_img = Image.open(template_path).convert("RGB")
                                for field in certificate:
                                    for field_info in data:
                                        if not field_info["field_name"] in certificate:
                                            res = {"error": f"Invalid field_name [{field_info["field_name"]}]"}
                                            return JsonResponse(res, status=400)
                                        if field == field_info["field_name"]:
                                            bottom_right_corner = field_info["bottom_right_corner"]
                                            top_left_corner = field_info["top_left_corner"]
                                            template_img = place_field_on_image(template_img, top_left_corner, bottom_right_corner, certificate[field], text_color)
                                        else:
                                            continue
                                result.append({"file_name": f"image{i}.{template_extension}", "object": template_img, "extension": template_extension})
                            file_name = create_zip_file(result, request.user)
                            file = UserZips.objects.create(zip_path= file_name, user=request.user, status= Status.CREATED)
                            res = {"message": "Zip file created successfully", "file_id": file.id, "file_path": file_name}
                            return JsonResponse(res, status= 201)
                    elif extension == "excel":
                        with open(certificate_file.name, "r") as file:
                            wb = openpyxl.load_workbook(file.name)
                            ws = wb.active
                            print('Total number of rows: ' + str(ws.max_row) + '. And total number of columns: ' + str(ws.max_column))
                    else:
                        res = {"error": "Invalid extension for data file"}
                        return JsonResponse(res, status= 400)
            else:
                res = {"error": "No attached files"}
                return JsonResponse(res, status= 400)
    elif request.method == "GET":
        res = {"file_data": list(UserZips.objects.filter(user= request.user).exclude(status= Status.DELETED).values("id", "zip_file"))}
        return JsonResponse(res, status= 200)
    elif request.method == "PATCH":
        data = json.loads(request.body)
        file_id = data.get("file_id")
        file_name = data.get("new_name") + ".zip"
        old_name = data.get("old_name") + ".zip"
        source = os.path.join(BASE_DIR, "media", old_name)
        dest = os.path.join(BASE_DIR, "media", file_name)
        os.rename(source, dest)
        UserZips.objects.filter(id= file_id).update(status = Status.UPDATED, updation_timestamp= datetime.datetime.now(), zip_path= file_name + ".zip")
        res = {"message": "File updated successfully", "file_id": file_id}
        return JsonResponse(res, status= 200)
    elif request.method == "DELETE":
        data = json.loads(request.body)
        file_id = data.get("file_id")
        UserZips.objects.filter(id= file_id).update(status = Status.DELETED, deletion_timestamp= datetime.datetime.now())
        res = {"message": "File deleted successfully", "file_id": file_id}
        return JsonResponse(res, status= 200)
    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)

def user_templates(request):
    if not request.user.is_authenticated:
        res = {"error": "Login required"}
        return JsonResponse(res, status= 401)
    if request.method == "GET":
        templates = list(UserTemplates.objects.filter(user= request.user).exclude(status= Status.DELETED).values(template_id= F("id"), template_path= F("template_file")))
        res = {"templates": templates}
        return JsonResponse(res, status= 200)
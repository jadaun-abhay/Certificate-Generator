import csv
import datetime
import json
import os
import re
import shutil

import openpyxl
from PIL import Image
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.db.models import F
from django.http import JsonResponse, HttpResponse

from config.settings import BASE_DIR
from my_app.functions import place_field_on_image, create_zip_file
from my_app.models import User, BaseModel, UserZips, UserTemplates, UserUploads, UserFolderStructure, Trash, Fonts

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
        confirm_password = data.get("confirm_password")
        if not first_name:
            res = {"error": "First name is required"}
            return JsonResponse(res, status= 400)
        elif not email:
            res = {"error": "Email is required"}
            return JsonResponse(res, status= 400)
        elif not password:
            res = {"error": "Password is required"}
            return JsonResponse(res, status= 400)
        elif not confirm_password:
            res = {"error": "Please confirm password"}
            return JsonResponse(res, status= 400)
        first_name = first_name.capitalize()
        if not re.match(r'\b[a-z|A-Z]{2,25}', first_name):
            res = {"error": "Invalid first name. First name must be minimum of two characters"}
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
        res = {"message": f"User {user.email} created successfully"}
        return JsonResponse(res, status= 201)
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
        if not bool(re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email)):
            res = {"error": "Email is invalid. Must be like 'abc@example.com'"}
            return JsonResponse(res, status= 400)
        elif not bool(re.match(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$', password)):
            res = {"error": "Password must be at least 8 characters long and must contain at least a special and uppercase character"}
            return JsonResponse(res, status= 400)
        user = User.objects.filter(email= email).exclude(status= Status.DELETED)
        if not user.exists():
            res = {"error": "Email is not registered"}
            return JsonResponse(res, status= 400)
        user = authenticate(email= email, password= password)
        if user:
            login(request, user)
            res = {"message": "Login is successful"}
            return JsonResponse(res, status= 200)
        res = {"error": "Incorrect password"}
        return JsonResponse(res, status= 400)
    elif request.method == "GET":
        if request.user.is_authenticated:
            user = request.user
            user = User.objects.get(id= user.id)
            email= user.email
            first_name = user.first_name
            last_name = user.last_name
            middle_name = user.middle_name
            res = {"message": 'Login is successful', "user_info": {"email": email, "middle_name": middle_name, "first_name": first_name, "last_name": last_name}}
            return JsonResponse(res, status= 200)
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    res = {"error": "Invalid request method"}
    return JsonResponse(res, status= 405)

def logout_user(request):
    if not request.user.is_authenticated:
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    if request.method == "POST":
        shutil.rmtree(f"media/preview/id-{request.user.id}/")
        logout(request)
        res = {"message": "Logout is successful"}
        return JsonResponse(res, status= 200)
    res = {"error": "Invalid request method"}
    return JsonResponse(res, status= 405)

def drive_structure(request, command= None):
    if not request.user.is_authenticated:
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    if request.method == "POST":
        data = request.POST
        attached_files = request.FILES
        name = data.get("name")
        parent_directory_id = data.get("parent_id")
        if not attached_files:
            if not name:
                res = {"error": "Name of the directory is required"}
                return JsonResponse(res, status= 400)
            if not bool(re.match(r"^[A-Z][a-z]{1, 20}$", name)):
                res = {"error": "Invalid name of directory !!!"}
                return JsonResponse(res, status= 400)
            if not parent_directory_id:
                home_directory, presence = UserFolderStructure.objects.get_or_create(name= "home", parent= None, user_id= request.user.id, status= Status.CREATED)
                directory, presence = UserFolderStructure.objects.get_or_create(user_id= request.user.id, name= name, parent_id= home_directory.id, defaults= {"status": Status.CREATED})
                if presence:
                    res = {"error": f"Directory with name {name} already exists in home directory !!!"}
                    return JsonResponse(res, status= 409)
                res = {"message": f"{name} directory created successfully"}
                return JsonResponse(res, status= 200)
            parent_directory = UserFolderStructure.objects.filter(user_id= request.user.id, id= parent_directory_id).exclude(status= Status.DELETED).first()
            if not parent_directory:
                res = {"error": f"Parent directory with id-{parent_directory_id} does not exist"}
                return JsonResponse(res, status= 400)
            directory, presence = UserFolderStructure. objects.filter(user_id= request.user.id, parent_id= parent_directory.id).exclude(status= Status.DELETED).get_or_create(name= name, user_id= request.user.id, parent_id= parent_directory.id, defaults= {"status": Status.CREATED})
            if presence:
                res = {"error": f"Directory with name {name} already exists in {parent_directory.name} directory !!!"}
                return JsonResponse(res, status= 409)
            res = {"message": f"{name} directory created successfully"}
            return JsonResponse(res, status= 200)
        for key, file_obj in attached_files:
            filename = file_obj.name
            extension = filename.split(".")[-1].lower()
            content_type = file_obj.content_type
            if not extension in settings.WHITELISTED_FILE_TYPES.keys():
                res = {"error": f"{extension} for {filename} is not supported !!!"}
                return JsonResponse(res, status= 400)
            elif content_type not in settings.WHITELISTED_FILE_TYPES.values():
                res = {"error": f"{content_type} is not supported !!!"}
                return JsonResponse(res, status= 400)
            uploaded_file_path = "/".join(["/uploads", f"id-{request.user.id}", filename])
            if not parent_directory_id:
                home_directory, presence = UserFolderStructure.objects.get_or_create(name= "home", parent= None, user_id= request.user.id, status= Status.CREATED)

                (file_upload, presence) = UserUploads.objects.filter(user_id= request.user.id, parent_directory_id= home_directory.id).exclude(status= Status.DELETED).get_or_create(user_id= request.user.id, parent_directory_id= home_directory.id, uploaded_file_path= uploaded_file_path, uploaded_file_name= filename, defaults= {"status": Status.CREATED})
                if presence:
                    res = {"error": f"File with name {filename} already exists in {home_directory.name} directory !!!"}
                    return JsonResponse(res, status= 409)
            parent_directory = UserFolderStructure.objects.filter(user_id= request.user.id, name= name).exclude(status= Status.DELETED).first()
            if not parent_directory:
                res = {"error": f"Parent directory with id-{parent_directory_id} does not exist !!!"}
                return JsonResponse(res, status= 409)
            file_upload, presence = UserUploads.objects.filter(user_id= request.user.id, parent_direectory_id= parent_directory.id).exclude(status= Status.DELETED).get_or_create(user_id= request.user.id, parent_directory_id= parent_directory.id, uploaded_file_path= uploaded_file_path, uploaded_file_name= filename, defaults= {"status": Status.CREATED})
            if presence:
                res = {"error": f"File with name {filename} already exists in {parent_directory.name} directory !!!"}
                return JsonResponse(res, status= 409)
        res = {"message": "Given file/s are uploaded successfully"}
        return JsonResponse(res, status= 201)
    elif request.method == "GET":
        directory_id = request.GET.get("id")
        if not directory_id:
            child_directories = list(UserFolderStructure.objects.filter(user_id= request.user.id, parent__name= "home").exclude(status= Status.DELETED).values(c_dir_id= F("id"), c_dir_name= F("name"), created_at= F("creation_timestamp")))
            path = "home/"
            uploaded_files = list(UserUploads.objects.filter(parent_directory__name= "home", user_id= request.user.id).exclude(status= Status.DELETED).values(f_id= F("id"), f_path= F("uploaded_file_path"), f_name= F("uploaded_file_name"), created_at= F("creation_timestamp")))
            templates = list(UserTemplates.objects.filter(user_id= request.user.id, parent_directory__name= "home").exclude(status= Status.DELETED).values(t_id= F("id"), t_name= F("template_name"), t_path= F("template_file"), created_at= F("creation_timestamp")))
            zips = list(UserZips.objects.filter(user_id= request.user.id, parent_directory__name= "home").exclude(status= Status.DELETED).values(z_id= F("id"), z_name= F("zip_name"), z_path= F("zip_file"), created_at= F("creation_timestamp")))
            res = {"message": "success", "path": path, "child_directories": child_directories, "uploaded_files": uploaded_files, "templates": templates, "zips": zips}
            return JsonResponse(res, status= 200)
        directory = UserFolderStructure.objects.filter(user_id= request.user.id, id= directory_id).exclude(status= Status.DELETED).first()
        if not directory:
            res = {"error": "Directory does not exist !!!"}
            return JsonResponse(res, status= 404)
        child_directories = list(UserFolderStructure.objects.filter(user_id= request.user.id, parent__id= directory_id).exclude(status= Status.DELETED).values(c_dir_id= F("id"), c_dir_name= F("name"), created_at= F("creation_timestamp")))
        path_info = directory.get_directory_path()
        uploaded_files = list(UserUploads.objects.filter(parent_directory= directory, user_id= request.user.id).exclude(status= Status.DELETED).values(f_id= F("id"), f_path= F("uploaded_file_path"), f_name= F("uploaded_file_name"), created_at= F("creation_timestamp")))
        templates = list(UserTemplates.objects.filter(user_id= request.user.id, parent_directory= directory).exclude(status= Status.DELETED).values(t_id= F("id"), t_name= F("template_name"), t_path= F("template_file"), created_at= F("creation_timestamp")))
        zips = list(UserZips.objects.filter(user_id= request.user.id, parent_directory= directory).exclude(status= Status.DELETED).values(z_id= F("id"), z_name= F("zip_name"), z_path= F("zip_file"), created_at= F("creation_timestamp")))
        res = {"message": "success", "path_info": path_info, "child_directories": child_directories, "uploaded_files": uploaded_files, "templates": templates, "zips": zips}
        return JsonResponse(res, status= 200)
    elif request.method == "PATCH":
        data = json.loads(request.body)
        file_id = data.get("f_id")
        directory_id = data.get("dir_id")
        new_name = data.get("name")
        destination_directory_id = data.get("destination_id")
        if command.lower() == "rename":
            if file_id:
                if not new_name:
                    res = {"error": "New name for file is not given !!!"}
                    return JsonResponse(res, status= 400)
                file = UserUploads.objects.filter(user_id= request.user.id, id= file_id).exclude(status= Status.DELETED).first()
                if not file:
                    res = {"error": "File does not exists !!!"}
                    return JsonResponse(res, status= 409)
                path = str(file.uploaded_file_path)
                filename = file.uploaded_file_name
                source_path = "/".join([f"{BASE_DIR}", "media", path[1:]])
                destination_path = "/".join([f"{BASE_DIR}", "media", path.replace(filename, new_name)[1:]])
                file.uploaded_file_path = destination_path
                file.status = Status.UPDATED
                file.updation_timestamp = datetime.datetime.now()
                file.save()
                os.rename(source_path, destination_path)
                res = {"message": "File is renamed successfully"}
                return JsonResponse(res, status= 200)
            elif directory_id:
                if not new_name:
                    res = {"error": "New name for directory is not given !!!"}
                    return JsonResponse(res, status= 400)
                directory = UserFolderStructure.objects.filter(user_id= request.user.id, id= directory_id).exclude(status= Status.DELETED).first()
                if not directory:
                    res = {"error": "Directory does not exist !!!"}
                    return JsonResponse(res, status= 400)
                directory.name = new_name
                directory.status = Status.UPDATED
                directory.save()
                res = {"message": "Directory is renamed successfully"}
                return JsonResponse(res, status= 200)
        elif command.lower() == "move":
            if directory_id:
                if not destination_directory_id:
                    res = {"error": "source and destination for folder is not provided !!!"}
                    return JsonResponse(res, status= 400)
                folder = UserFolderStructure.objects.filter(user_id= request.user.id, id= directory_id).exclude(status= Status.DELETED)
                if not folder.exists():
                    res = {"error": "Folder does not exists in the source directory !!!"}
                    return JsonResponse(res, status= 404)
                folder_instance = folder.first()
                check_duplicate = UserFolderStructure.objects.filter(user_id= request.user.id, parent_id= destination_directory_id, name= folder_instance.name).exclude(status= Status.DELETED)
                if check_duplicate.exists():
                    res = {"error": "directory with the same name already exists in destination directory !!!"}
                    return JsonResponse(res, status= 409)
                folder.update(status= Status.CREATED, updation_timestamp= datetime.datetime.now(), parent_id= destination_directory_id, name= new_name)
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
        data = json.loads(request.body)
        directory_id = data.get("id")
        directory = UserFolderStructure.objects.filter(user= request.user, id= directory_id).exclude(status= Status.DELETED)
        print(directory.first().id, directory_id)
        if not directory.exists():
            res = {"error": "Directory does not exist !!!"}
            return JsonResponse(res, status= 404)
        directory.update(status= Status.DELETED, deletion_timestamp= datetime.datetime.now())
        Trash.objects.create(directory_id= directory_id, show= True, user= request.user)
        res = {"message": "Directory deleted successfully !!!"}
        return JsonResponse(res, status= 200)
    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)

def zipify(request, command= None):
    if not request.user.is_authenticated:
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    if request.method == "POST":
        post_data = request.POST
        attached_files = request.FILES
        print("files ============", attached_files)
        text_color = post_data.get("color")
        font_id = post_data.get("font_id")
        font_id = 1
        if not font_id:
            res = {"error": "Font is not provided !!!"}
            return JsonResponse(res, status= 400)
        str_data = post_data.get("data")
        data = json.loads(str_data)
        print("data =", data)
        box_info = data.get("data")
        if not box_info:
            res = {"error": "Data is required !!!"}
            return JsonResponse(res, status= 400)
        elif not attached_files:
            res = {"error": "No attached files"}
            return JsonResponse(res, status= 400)
        elif len(attached_files) < 2:
            res = {"error": "Required files are not attached !!!"}
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
                    template_file = UserTemplates(user_id= request.user.id, template_file= template, status= Status.CREATED, template_name= template.name)
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
                    font = Fonts.objects.filter(id= font_id).exclude(status= Status.DELETED)
                    if not font.exists():
                        res = {"error": "Font is not found !!!"}
                        return JsonResponse(res, status= 204)
                    font = "media/" + str(font.first().font_path)
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
                                template_img = place_field_on_image(template_img, field_info, certificate[field], text_color= text_color, font_name= font)
                            result.append({"file_name": f"image{i}.{template_extension}", "object": template_img, "extension": template_extension})
                        file_path, file_name, preview = create_zip_file(result, request.user)
                        user_preview_path = os.path.exists(f"{BASE_DIR}/media/preview/id-{request.user.id}")
                        if not user_preview_path:
                            os.makedirs(f"{BASE_DIR}/media/preview/id-{request.user.id}/")
                        preview_name = file_name + ".jpeg"
                        preview.save(f"media/preview/id-{request.user.id}/{preview_name}")
                        file = UserZips.objects.create(zip_file= file_path, zip_name= file_name +".zip", user=request.user, status= Status.CREATED)
                        res = {"message": "Zip file created successfully", "file_id": file.id, "file_path": file_path, "file_name": file_name, "preview_name": f"/preview/id-{request.user.id}/" + preview_name}
                        return JsonResponse(res, status= 201)
                    elif extension == "csv":
                        # if extension == "excel":
                        #     res = {"error": "Excel file not supported !!!"}
                        #     return JsonResponse(res, status= 400)
                        #     excel_file = certificate_file.name
                        #     xls_file = pd.read_excel(excel_file)
                        #     certificate_file = certificate_file.name.replace(".xlsx", ".csv")
                        #     xls_file.to_csv(certificate_file, index= None, header= True)
                        with open(certificate_file.name, "r") as file:
                            csv_file = csv.DictReader(file)
                            result = list()
                            i = -1
                            for certificate in csv_file:
                                i += 1
                                template_path = os.path.join(BASE_DIR, "media", "template", f"id-{request.user.id}", template.name)
                                template_img = Image.open(template_path).convert("RGB")
                                for field in certificate:
                                    if not field in field_set:
                                        continue
                                    invalid_field = [info_dict.get("field_name") for info_dict in box_info if
                                                     info_dict.get("field_name") not in certificate]
                                    if invalid_field:
                                        res = {"error": f"Invalid field [{invalid_field[0]}]"}
                                        return JsonResponse(res, status=400)
                                    field_info = [info_dict for info_dict in box_info if info_dict.get("field_name") == field]
                                    template_img = place_field_on_image(template_img, field_info, certificate[field], text_color= text_color, font_name= font)
                                result.append({"file_name": f"image{i}.{template_extension}", "object": template_img, "extension": template_extension})
                            file_path, file_name, preview = create_zip_file(result, request.user)
                            file = UserZips.objects.create(zip_path= file_path, zip_name= file_name + ".zip", user=request.user, status= Status.CREATED)
                            res = {"message": "Zip file created successfully", "file_id": file.id, "file_path": file_path, "file_name": file_name}
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
        res = {"file_data": list(UserZips.objects.filter(user= request.user, parent_directory_id= None).exclude(status= Status.DELETED).values(zip_id= F("id"), zip_file_path= F("zip_file"), zip_file_name= F("zip_name"), created_at= F("creation_timestamp")))}
        return JsonResponse(res, status= 200)
    elif request.method == "PATCH":
        data = json.loads(request.body)
        file_id = data.get("file_id")
        if command == "rename":
            if not data.get("new_name"):
                res = {"error": "No new name is given !!!"}
                return JsonResponse(res, status= 400)
            file = UserZips.objects.filter(id=file_id, user= request.user).exclude(status= Status.DELETED)
            if not file.exists():
                res = {"error": "No such file exists !!!"}
                return JsonResponse(res, status= 400)
            old_file_name= file.first().zip_name
            old_file_path = file.first().zip_file
            file_name = data.get("new_name") + ".zip"
            print("old_file_path: ", type(old_file_path))
            source = "/".join([f"{BASE_DIR}", "media", old_file_path])
            print("source= ", source)
            dest = "/".join([f"{BASE_DIR}", "media", "zips", f"id-{request.user.id}", file_name])
            print("dest= ", dest)
            os.rename(source, dest)
            zipp = UserZips.objects.filter(id= file_id, user= request.user).exclude(status= Status.DELETED)
            if not zipp.exists():
                res = {"error": "No such file exists !!!"}
                return JsonResponse(res, status= 400)
            zipp.update(status = Status.UPDATED, updation_timestamp= datetime.datetime.now(), zip_file= "/".join(["/zips", f"id-{request.user.id}", file_name]), zip_name= file_name)
            res = {"message": "File updated successfully", "file_id": file_id}
            return JsonResponse(res, status= 200)
        elif command.lower() == "move":
            file_id = file_id[0]
            destination_directory_id = data.get("destination_id")
            if not destination_directory_id:
                res = {"error": "No destination directory or source directory id"}
                return JsonResponse(res, status= 400)
            zipp = UserZips.objects.filter(user_id= request.user.id, id= file_id).exclude(status= Status.DELETED)
            if not zipp.exists():
                res = {"error": "No such file exists in parent directory!!!"}
                return JsonResponse(res, status= 400)
            if zipp.first().parent_directory_id == destination_directory_id:
                res = {"error": "File can not be moved to the same directory"}
                return JsonResponse(res, status= 409)
            check = UserZips.objects.filter(zip_name= zipp.first().zip_name, parent_directory__id= destination_directory_id).exclude(status= Status.DELETED)
            if check.exists():
                res = {"error": "File exists in destination directory with same name !!!"}
                return JsonResponse(res, status= 400)
            zipp.update(status= Status.UPDATED, parent_directory= destination_directory_id)
            res = {"message": "File moved successfully"}
            return JsonResponse(res, status= 200)
        res = {"error": "Invalid command"}
        return JsonResponse(res, status= 400)
    elif request.method == "DELETE":
        data = json.loads(request.body)
        file_id = data.get("file_id")
        if not file_id:
            res = {"error": "file_id is not given !!!"}
            return JsonResponse(res, status= 400)
        zip_file = UserZips.objects.filter(id= file_id).exclude(status= Status.DELETED)
        if not zip_file.exists():
            res = {"error": "No such file exists !!!"}
            return JsonResponse(res, status= 400)
        zip_file.update(status = Status.DELETED, deletion_timestamp= datetime.datetime.now())
        res = {"message": "File deleted successfully", "file_id": file_id}
        Trash.objects.create(user_id= request.user.id, zip_id= file_id, show= True)
        return JsonResponse(res, status= 200)
    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)

def user_templates(request, command= None):
    if not request.user.is_authenticated:
        res = {"error": "Login required"}
        return JsonResponse(res, status= 401)
    if request.method == "GET":
        templates = list(UserTemplates.objects.filter(user_id= request.user.id).exclude(status= Status.DELETED).values(template_id= F("id"), template_path= F("template_file"), tempplate_name= F("template_name"), created_at= F("creation_timestamp")))
        res = {"templates": templates}
        return JsonResponse(res, status= 200)

def trash(request):
    if not request.user.is_authenticated:
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    if request.method == "GET":
        trash_list = list(Trash.objects.filter(user_id= request.user.id).exclude(show= False).values("id", directory_name= F("directory__name"), template_name= F("template__template_name"), zip_name= F("zip__zip_name")))
        res = {"message": "success", "data": trash_list}
        return JsonResponse(res, status= 200)
    elif request.method == "PATCH":
        data = json.loads(request.body)
        id = data.get("id")
        if not id:
            res = {"error": "id is not given !!!"}
            return JsonResponse(res, status= 400)
        trash_item = Trash.objects.filter(id= id).exclude(show= False)
        if not trash_item.exists():
            res = {"error": "Item does not exists !!!"}
            return JsonResponse(res, status= 400)
        trash_item_instance = trash_item.first()
        if trash_item_instance.directory:
            directory_id= trash_item_instance.directory
            Trash.objects.filter(user= request.user, id= id).update(show= False)
            directory = UserFolderStructure.objects.filter(user_id= request.user.id, id= directory_id.id, status= Status.DELETED, permanent_deletion_status= False)
            if not directory.exists():
                res = {"error": "Directory does not exist !!!"}
                return JsonResponse(res, status= 400)
            directory.update(status= Status.UPDATED, updation_timestamp= datetime.datetime.now())
            res = {"message": "Directory restored successfully"}
            return JsonResponse(res, status= 200)
        elif trash_item_instance.zip:
            zip_id = trash_item_instance.zip
            Trash.objects.filter(user= request.user, id= id).update(show= False)
            zip = UserZips.objects.filter(user_id= request.user.id, id= zip_id.id, status= Status.DELETED)
            print(zip)
            if not zip.exists():
                res= {"error": "Zip does not exist !!!"}
                return JsonResponse(res, status= 400)
            zip.update(status= Status.UPDATED, deletion_timestamp= datetime.datetime.now())
            res = {"message": "Zip restored successfully"}
            return JsonResponse(res, status= 200)
    elif request.method == "DELETE":
        data = json.loads(request.body)
        item_id = data.get("id")
        if not item_id:
            res = {"error": "id is not given !!!"}
            return JsonResponse(res, status= 400)
        Trash.objects.filter(user= request.user, id= item_id).update(show= False)
        res = {"message": "Item deleted successfully"}
        return JsonResponse(res, status= 200)
    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)

def fonts(request):
    if not request.user.is_authenticated:
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    if request.method == "POST":
        font_file = request.FILES.get("font_file")
        if not font_file:
            res = {"error": "Font is not given !!!"}
            return JsonResponse(res, status= 400)
        extension = font_file.name.split(".")[-1]
        font_name = font_file.name.replace(f".{extension}", "")
        font_path = "fonts/" + font_file.name
        new_font, presence = Fonts.objects.filter(font_path= font_path).exclude(status= Status.DELETED).get_or_create(font_name= font_name, defaults= {"user_id": request.user, "status": Status.CREATED, "font_path": font_file})
        if not presence:
            res = {"message": "Font already exists !!!"}
            return JsonResponse(res, status= 409)
        res = {"message": "Font created successfully"}
        return JsonResponse(res, status= 200)
    elif request.method == "GET":
        font_list = list(Fonts.objects.exclude(status= Status.DELETED).values("id", "font_name"))
        res = {"font_list": font_list}
        return JsonResponse(res, status= 200)
    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)


import csv
import datetime
import json
import os
import re

from PIL import Image
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

from certificate_generator.settings import BASE_DIR
from main.functions import place_field_on_image, create_zip_file
from main.models import User, BaseModel, UserDocuments

Status = BaseModel.Status

# Create your views here.

def index(request):
    res = {"message": "demo"}
    return JsonResponse(res, status= 200)

def login_user(request):
    if request.method == "POST":
        data = request.POST
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

def certify_document(request):
    if not request.user.is_authenticated:
        res = {"error": "Login is required !!!"}
        return JsonResponse(res, status= 401)
    if request.method == "POST":
        data = request.POST
        attached_files = request.FILES
        field_format = data.get("data")
        if not field_format:
            res = {"error": "Data is required !!!"}
            return JsonResponse(res, status= 400)
        elif not attached_files:
            res = {"error": "No attached files"}
            return JsonResponse(res, status= 400)
        elif len(attached_files) != 2:
            res = {"error": "2 files are required"}
            return JsonResponse(res, status= 400)
        else:
            json_data = json.loads(field_format)
            data = json_data.get("data")
            print(data)
            if not isinstance(data, list):
                res = {"error": "Data is not a list"}
                return JsonResponse(res, status= 400)
            template = attached_files.get("template")
            data_file = attached_files.get("data_file")
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
            if data_file:
                extension = data_file.name.split(".")[-1]
                extension = extension.lower()
                content_type = data_file.content_type
                if extension not in settings.WHITELISTED_FILE_TYPES.keys():
                    res = {"error": "Invalid extension for data file"}
                    return JsonResponse(res, status= 400)
                elif content_type not in settings.WHITELISTED_FILE_TYPES.values():
                    res = {"error": "Invalid content type for data file"}
                    return JsonResponse(res, status= 400)
                else:
                    if extension == "json":
                        with open(data_file.name, "r") as json_file:
                            json_data = json.load(json_file)
                        data_list = json_data.get("data")
                        result = list()
                        i = -1
                        for certificate in data_list:
                            i += 1
                            template_img = Image.open(template.name).convert("RGB")
                            for field in certificate:
                                for field_info in data:
                                    print("field = ", field, ", field_name in file = ", field_info["field_name"])
                                    if field == field_info["field_name"]:
                                        bottom_right_corner = field_info["bottom_right_corner"]
                                        top_left_corner = field_info["top_left_corner"]
                                        print("field = ", field, "field_value =", certificate[field], "top_left_corner = ", top_left_corner, " bottom_right_corner = ", bottom_right_corner)
                                        template_img = place_field_on_image(template_img, top_left_corner, bottom_right_corner, certificate[field])
                                    else:
                                        continue
                            result.append({"file_name": f"image{i}.{template_extension}", "object": template_img, "extension": template_extension})
                        file_name = create_zip_file(result, request.user)
                        file = UserDocuments.objects.create(zip_path= file_name, user=request.user, status= Status.CREATED)
                        res = {"message": "Zip file created successfully", "file_id": file.id}
                        return JsonResponse(res, status= 201)
                    elif extension == "csv":
                        with open(data_file.name, "r") as file:
                            csv_file = csv.DictReader(file)
                            result = list()
                            i = -1
                            for certificate in csv_file:
                                i += 1
                                template_img = Image.open(template.name).convert("RGB")
                                for field in certificate:
                                    for field_info in data:
                                        if field == field_info["field_name"]:
                                            bottom_right_corner = field_info["bottom_right_corner"]
                                            top_left_corner = field_info["top_left_corner"]
                                            template_img = place_field_on_image(template_img, top_left_corner, bottom_right_corner, certificate[field])
                                        else:
                                            continue
                                result.append({"file_name": f"image{i}.{template_extension}", "object": template_img, "extension": template_extension})
                            file_name = create_zip_file(result, request.user)
                            file = UserDocuments.objects.create(zip_path= file_name, user=request.user, status= Status.CREATED)
                            res = {"message": "Zip file created successfully", "file_id": file.id}
                            return JsonResponse(res, status= 201)
                    else:
                        res = {"error": "Invalid extension for data file"}
                        return JsonResponse(res, status= 400)
            else:
                res = {"error": "No attached files"}
                return JsonResponse(res, status= 400)
    elif request.method == "GET":
        res = {"file_data": list(UserDocuments.objects.filter(user= request.user).exclude(status= Status.DELETED).values("id", "zip_path"))}
        return JsonResponse(res, status= 200)
    elif request.method == "PATCH":
        data = json.loads(request.body)
        file_id = data.get("file_id")
        file_name = data.get("new_name") + ".zip"
        old_name = data.get("old_name") + ".zip"
        source = os.path.join(BASE_DIR, "media", old_name)
        dest = os.path.join(BASE_DIR, "media", file_name)
        os.rename(source, dest)
        UserDocuments.objects.filter(id= file_id).update(status = Status.UPDATED, updation_timestamp= datetime.datetime.now(), zip_path= file_name + ".zip")
        res = {"message": "File updated successfully", "file_id": file_id}
        return JsonResponse(res, status= 200)
    elif request.method == "DELETE":
        data = json.loads(request.body)
        file_id = data.get("file_id")
        UserDocuments.objects.filter(id= file_id).update(status = Status.DELETED, deletion_timestamp= datetime.datetime.now())
        res = {"message": "File deleted successfully", "file_id": file_id}
        return JsonResponse(res, status= 200)
    else:
        res = {"error": "Invalid request method"}
        return JsonResponse(res, status= 405)

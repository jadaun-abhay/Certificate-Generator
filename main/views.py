import json
import re

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

from main.models import User, BaseModel

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
                user = User.objects.filter(email= email, password= password).exclude(status= Status.DELETED)
                if user.exists():
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

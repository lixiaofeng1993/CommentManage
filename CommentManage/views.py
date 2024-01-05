#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Author: Bruce·li
# @File: views.py
# @Time: 2023-05-25 18:41
# @Version：V 0.1
# @Describe:
import re
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth  # django认证系统
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from comment.response import JsonResponse
from comment.public import handle_json


def login(request):
    if request.method == "GET":
        return render(request, "login/login.html")
    elif request.method == "POST":
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        username = body.get('username', '')
        password = body.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is None:
            return JsonResponse.CheckException(message="用户名或者密码错误.")
        auth.login(request, user)
        user = User.objects.get(username=username)
        login_from = request.session.get("login_from")
        result = {
            "id": user.id,
            "username": username,
            "login_from": login_from
        }
        return JsonResponse.OK(data=result)


def change(request):
    if request.method == "GET":
        return render(request, "login/change.html")
    elif request.method == "POST":
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        username = body.get('username', '')
        password = body.get('password', '')
        confirm = body.get('confirm', '')
        new_password = body.get('new_password', '')
        user = auth.authenticate(username=username, password=password)
        if user is None:
            return JsonResponse.CheckException(message="原密码错误.")
        if password == new_password:
            return JsonResponse.RepeatException(message="修改密码和旧密码相同.")
        if new_password != confirm:
            return JsonResponse.EqualException(message="新密码和确认密码不一致.")
        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse.UserException()
        try:
            user.set_password(new_password)
            user.save()
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        return JsonResponse.OK()


@login_required
def logout(request):
    response = HttpResponseRedirect('/login/action/')
    auth.logout(request)  # 退出登录
    return response


def register(request):
    if request.method == "GET":
        return render(request, "login/register.html")
    elif request.method == "POST":
        body = handle_json(request)
        if not body:
            return JsonResponse.JsonException()
        username = body.get('username', '')
        password = body.get('password', '')
        confirm = body.get('confirm', '')
        if password != confirm:
            return JsonResponse.EqualException(message="两次输入的密码不一致.")
        user = User.objects.filter(username=username).exists()
        if user:
            return JsonResponse.RepeatException(message="用户已存在.")
        try:
            User.objects.create_user(username=username, password=password)
        except Exception as error:
            return JsonResponse.DatabaseException(data=str(error))
        return JsonResponse.OK()


def page_not_found(request, exception, template_name='home/404.html'):
    return render(request, template_name)


def server_error(exception, template_name='home/500.html'):
    return render(exception, template_name)

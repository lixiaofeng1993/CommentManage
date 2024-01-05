#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Author: Bruce·li
# @File: response.py
# @Time: 2023-05-20 15:20
# @Version：V 0.1
# @Describe:
import json
from django.http import HttpResponse


class JsonResponse(HttpResponse):
    def __init__(self, code=200, message="ok", data=None):
        response = dict()
        response["code"] = code
        response["message"] = message
        response["data"] = data
        self.headers = {}
        super(JsonResponse, self).__init__(json.dumps(response, ensure_ascii=False), content_type="application/json", )

    @staticmethod
    def OK(message="ok", data=None):
        response = JsonResponse(200, message, data)
        return response

    @staticmethod
    def BadRequest(message="请求出现异常.", data=None):
        response = JsonResponse(400, message, data)
        return response

    @staticmethod
    def MethodNotAllowed(message="请求方式错误.", data=None):
        return JsonResponse(405, message, data)

    @staticmethod
    def ServerError(message="系统异常.", data=None):
        return JsonResponse(500, message, data)

    @staticmethod
    def JsonException(message="传参类型错误.", data=None):
        return JsonResponse(1003, message, data)

    @staticmethod
    def DatabaseException(message="操作数据库出现错误.", data=None):
        return JsonResponse(1004, message, data)

    @staticmethod
    def CheckException(message="检查字段存在异常.", data=None):
        return JsonResponse(1002, message, data)

    @staticmethod
    def RepeatException(message="数据重复异常.", data=None):
        return JsonResponse(1005, message, data)

    @staticmethod
    def EqualException(message="数据不相等异常.", data=None):
        return JsonResponse(1007, message, data)

    @staticmethod
    def UserException(message="用户不存在.", data=None):
        return JsonResponse(1011, message, data)

#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Author: Bruce·li
# @File: urls.py
# @Time: 2023-05-20 13:35
# @Version：V 0.1
# @Describe:
from django.urls import path

from comment import views

urlpatterns = [
    path("", views.home, name="home"),
    path("comment/", views.comment_list, name="comment"),
    path("comment/look/<int:vid>/", views.comment_look, name="comment_look"),
    path("comment/load/<int:vid>/<int:number>/", views.comment_load, name="comment_load"),
    path("comment/del/<int:comment_id>/", views.comment_del, name="comment_del"),
    path("user/", views.user_list, name="user"),
    path("user/del/<int:uid>/", views.user_del, name="user_del"),
    path("video/", views.video_list, name="video"),
    path("video/del/<int:vid>/", views.video_del, name="video_del"),
    path("total", views.total, name="total"),
    path("warning_user", views.warning_user, name="warning_user"),
    path("warning_video", views.warning_video, name="warning_video"),
    path("create/comment/<int:number>/", views.create_comment, name="create_comment"),

]

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from comment.public import *
from comment.response import JsonResponse


@login_required
def home(request):
    return render(request, "home/home.html")


@login_required
def comment_list(request):
    if request.method == "GET":
        model = Comment.objects.all()
        info = paging_data(request, model, 12)
        vid = info["search_name"]
        if info["total_number"]:
            if vid.isdigit():
                total_number = Comment.objects.filter(vid=vid).values("vid").distinct().count()
                obj_list = Comment.objects.filter(vid=vid).values("vid").distinct()[info["start"]:info["end"]]
            else:
                total_number = Comment.objects.all().values("vid").distinct().count()
                obj_list = Comment.objects.all().values("vid").distinct()[info["start"]:info["end"]]
        else:
            obj_list = []
            total_number = 0
        obj_list = add_negative_comment(list(obj_list), flag=4)
        total_pages = total_number // 12  # 总页数
        if total_number % 12 > 0:
            total_pages = total_pages + 1
        if info["page"] < 1:
            info["page"] = 1
        if info["page"] > total_pages:
            info["page"] = total_pages
        info["total_pages"] = total_pages
        info["is_paginated"] = True if total_number > 12 else False  # 是否需要分页
        info = pagination_data(info)
        info.update({
            "object_list": obj_list,
        })
        return render(request, "home/commnet/comment.html", info)


@login_required
def comment_look(request, vid):
    if request.method == "GET":
        info = request_get_search(request)
        video = Video.objects.get(vid=vid)
        com = Comment.objects.filter(vid=vid).order_by("dt")
        for data in com:
            user = User.objects.get(uid=data.uid)
            data.dt = data.dt.strftime("%Y-%m-%d %H:%M:%S")
            label_list = 0 if not data.label else range(data.label)
            setattr(data, "user", user)
            setattr(data, "label", label_list)
        info.update({
            "video": video,
            "obj": com,
            "number": len(com),
        })
        return render(request, 'home/commnet/look_comment.html', info)


@login_required
def comment_load(request, vid, number):
    if request.method == "POST":
        com = Comment.objects.filter(vid=vid).order_by("dt")
        com_list = list()
        for data in com:
            user = User.objects.get(uid=data.uid)
            com_list.append({
                "vid": data.vid,
                "uid": data.uid,
                "barrage": data.barrage,
                "username": user.name,
                "dt": data.dt.strftime("%Y-%m-%d %H:%M:%S"),
                "label": data.label,
            })
        info = {
            "com": com_list[number:],
            "number": len(com),
        } if len(com) > number else {"com": ""}
        return JsonResponse.OK(data=info)


def comment_del(request, comment_id):
    if request.method == "POST":
        comm = Comment.objects.get(id=comment_id)
        comm.delete()
        obj_list = Comment.objects.all()
        info = request_get_search(request)
        info = delete_jump(info, obj_list)
        return JsonResponse.OK(data=info)


@login_required
def user_list(request):
    if request.method == "GET":
        model = User.objects.all()
        info = paging_data(request, model, 10)
        if info["total_number"]:
            obj_list = model[info["start"]:info["end"]]
        else:
            obj_list = []
        obj_list = add_negative_comment(list(obj_list))
        info = pagination_data(info)
        info.update({
            "object_list": obj_list,
        })
        return render(request, "home/user/user.html", info)


def user_del(request, uid):
    if request.method == "POST":
        if Comment.objects.filter(uid=uid).exists():
            return JsonResponse.CheckException(message="请先删除用户评论.")
        user = User.objects.get(uid=uid)
        user.delete()
        obj_list = User.objects.all()
        info = request_get_search(request)
        info = delete_jump(info, obj_list)
        return JsonResponse.OK(data=info)


@login_required
def video_list(request):
    if request.method == "GET":
        model = Video.objects.all()
        info = paging_data(request, model, 10)
        if info["total_number"]:
            obj_list = model[info["start"]:info["end"]]
        else:
            obj_list = []
        obj_list = add_negative_comment(list(obj_list), flag=1)
        info = pagination_data(info)
        info.update({
            "object_list": obj_list,
        })
        return render(request, "home/video/video.html", info)


def video_del(request, vid):
    if request.method == "POST":
        if Comment.objects.filter(vid=vid).exists():
            return JsonResponse.CheckException(message="请先删除视频评论.")
        video = Video.objects.get(vid=vid)
        video.delete()
        obj_list = Video.objects.all()
        info = request_get_search(request)
        info = delete_jump(info, obj_list)
        return JsonResponse.OK(data=info)


def total(request):
    if request.method == "POST":
        info = request_get_search(request)
        comment_number = Comment.objects.all().count()
        user_number = User.objects.all().count()
        video_number = Video.objects.all().count()
        info.update({
            "comment_number": comment_number,
            "user_number": user_number,
            "video_number": video_number,
        })
        return JsonResponse.OK(data=info)


def warning_user(request):
    if request.method == "POST":
        obj_list = Comment.objects.values("uid", "label").filter(label=0)[:1000].annotate(
            label_number=Count("label"))
        data = add_negative_comment(list(obj_list), flag=2)
        data.sort(key=lambda x: x["label_number"], reverse=True)
        return JsonResponse.OK(data=data[:10])


def warning_video(request):
    if request.method == "POST":
        obj_list = Comment.objects.values("vid", "label").filter(label=0)[:1000].annotate(
            label_number=Count("label"))
        total_number = Comment.objects.filter(label=0).count()
        data = add_negative_comment(list(obj_list), flag=3, total_number=total_number)
        data.sort(key=lambda x: x["label_number"], reverse=True)
        return JsonResponse.OK(data=data[:10])


def create_comment(request, number):
    if request.method == "GET":
        load_csv(number)
        return JsonResponse.OK()

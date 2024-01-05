#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Author: Bruce·li
# @File: public.py
# @Time: 2023-05-20 14:23
# @Version：V 0.1
# @Describe:
import json
import csv
import io
import os
import re
# from faker import Faker
from random import randint
from typing import Dict, List, Union, Any, Optional
from django.db.models import Q  # 与或非 查询
from django.conf import settings

from comment.models import *


def filter_emoji(desstr, restr=''):
    # 过滤表情
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


def load_csv(number: int = 1000):
    file_path = os.path.join(settings.BASE_DIR, "tools", "data")
    dir_list = os.listdir(file_path)
    uid_list = list(User.objects.all().values("uid"))
    vid_list = list(Video.objects.all().values("vid"))
    data_list = list()
    i = 0
    flag = False
    # fake = Faker("zh_CN")
    # comm_list = list()
    for file in dir_list:
        dir_path = os.path.join(file_path, file)
        if os.path.isdir(dir_path):
            csv_list = os.listdir(dir_path)
            for f in csv_list:
                csv_path = os.path.join(dir_path, f)
                if os.path.splitext(csv_path)[-1] == ".csv":
                    with io.open(csv_path, encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for value in reader:
                            vid = vid_list[randint(0, len(vid_list) - 1)]
                            uid = uid_list[randint(0, len(uid_list) - 1)]
                            # comm = Comment(
                            #     vid=vid["vid"],
                            #     barrage=filter_emoji(value["弹幕"]),
                            #     label=randint(0, 5),
                            #     dt=fake.date_time(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S"),
                            #     uid=uid["uid"],
                            # )
                            # comm_list.append(comm)
                            data_list.append({
                                "序号": i,
                                "vid": vid["vid"],
                                "uid": uid["uid"],
                                "弹幕": filter_emoji(value["弹幕"]),
                            })
                            i += 1
                            if i > number:
                                flag = True
                                break
                if flag:
                    break
        if flag:
            break
    # Comment.objects.bulk_create(comm_list)
    data_path = os.path.join(file_path, "barrage_classification.csv")
    head = ["序号", "vid", "uid", "弹幕"]
    with io.open(data_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=head)
        writer.writeheader()
        writer.writerows(data_list)


def paging_data(request, model, NumberOfPages: int):
    """
    处理分页数据
    """
    request.session["login_from"] = request.get_full_path()
    info = request_get_search(request)
    total_number = model.count()  # 总条数
    page = info["page"]
    # 列表序号
    page_flag = (page - 1) * NumberOfPages
    total_pages = total_number // NumberOfPages  # 总页数
    if total_number % NumberOfPages > 0:
        total_pages = total_pages + 1
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    start = (page - 1) * NumberOfPages  # 起
    end = page * NumberOfPages  # 始
    is_paginated = True if total_number > NumberOfPages else False  # 是否需要分页
    info.update({
        "page_flag": page_flag,
        "page": page,
        "is_paginated": is_paginated,
        "total_pages": total_pages,
        "total_number": total_number,
        "start": start,
        "end": end,
    })
    return info


def request_get_search(request) -> Dict:
    """
    封装获取get请求公共参数
    :param request:
    :return:
    """
    page = request.GET.get('page', '1')
    search_name = request.GET.get('search-input', '')
    page = int(page) if page.isdigit() else 1
    info = {
        "page": page,
        "search_name": search_name,
    }
    return info


def handle_json(request) -> Optional[Any]:
    """
    转化js json传参为dict
    """
    try:
        body = request.body.decode()
        body_dict = json.loads(body)
        return body_dict
    except json.JSONDecodeError as error:
        return


def add_negative_comment(obj_list: list, flag: int = 0, total_number: int = 0) -> list:
    data_list = list()
    if isinstance(obj_list, list):
        for data in obj_list:
            if flag == 1:
                comm = Comment.objects.all()
                total_number = comm.count()
                label_number = comm.filter(Q(vid=data.vid) & Q(label=0)).count()
                setattr(data, "label_number", round(label_number / total_number * 100, 2))
                data_list.append(data)
            elif flag == 2 and data["label"] == 0:
                user = User.objects.get(uid=data["uid"])
                if data["label_number"]:
                    data_list.append({
                        "uid": data["uid"],
                        "name": user.name,
                        "label_number": data["label_number"],
                    })
            elif flag == 3 and data["label"] == 0:
                video = Video.objects.get(vid=data["vid"])
                if data["label_number"]:
                    data_list.append({
                        "vid": data["vid"],
                        "name": video.title,
                        "label_number": round(data["label_number"] / total_number * 100, 2),
                    })
            elif flag == 4:
                video = Video.objects.get(vid=data["vid"])
                data_list.append({
                    "vid": data["vid"],
                    "name": video.title,
                    "favorite": video.favorite,
                    "video_share": video.video_share,
                    "video_like": video.video_like,
                    "tag_names": video.tag_names,
                    "description": video.description,
                })
            else:
                comm = Comment.objects.all()
                total_number = comm.count()
                label_number = comm.filter(Q(uid=data.uid) & Q(label=0)).count()
                setattr(data, "label_number", round(label_number / total_number * 100, 2))
                data_list.append(data)
    return data_list


def delete_jump(info, obj_list):
    """
    删除跳转
    """
    _page = int(info["page"])
    number = len(obj_list) % 10
    if number == 0 and len(obj_list) >= 10 and _page != 1:
        info["page"] = _page - 1
    return info


def pagination_data(info) -> Dict:
    """
    牛掰的分页
    """
    # 获得分页后的总页数
    # 获得用户当前请求的页码号
    total_pages, page_number, is_paginated = info["total_pages"], info["page"], info["is_paginated"]
    if not is_paginated:
        # 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
        return info

    # 当前页左边连续的页码号，初始值为空
    left = []

    # 当前页右边连续的页码号，初始值为空
    right = []

    # 标示第 1 页页码后是否需要显示省略号
    left_has_more = False

    # 标示最后一页页码前是否需要显示省略号
    right_has_more = False

    # 标示是否需要显示第 1 页的页码号。
    # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
    # 其它情况下第一页的页码是始终需要显示的。
    # 初始值为 False
    first = False

    # 标示是否需要显示最后一页的页码号。
    # 需要此指示变量的理由和上面相同。
    last = False

    # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
    page_range = range(1, total_pages + 1)

    if page_number == 1:
        # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
        # 此时只要获取当前页右边的连续页码号，
        # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
        # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
        right = page_range[page_number:page_number + 2]

        # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
        # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
        if right[-1] < total_pages - 1:
            right_has_more = True

        # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
        # 所以需要显示最后一页的页码号，通过 last 来指示
        if right[-1] < total_pages:
            last = True

    elif page_number == total_pages:
        # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
        # 此时只要获取当前页左边的连续页码号。
        # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
        # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
        left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

        # 如果最左边的页码号比第 2 页页码号还大，
        # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
        if left[0] > 2:
            left_has_more = True

        # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
        # 所以需要显示第一页的页码号，通过 first 来指示
        if left[0] > 1:
            first = True
    else:
        # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
        # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
        left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
        right = page_range[page_number:page_number + 2]

        # 是否需要显示最后一页和最后一页前的省略号
        if right[-1] < total_pages - 1:
            right_has_more = True
        if right[-1] < total_pages:
            last = True

        # 是否需要显示第 1 页和第 1 页后的省略号
        if left[0] > 2:
            left_has_more = True
        if left[0] > 1:
            first = True

    info.update({
        "left": left,
        "right": right,
        "left_has_more": left_has_more,
        "right_has_more": right_has_more,
        "first": first,
        "last": last,
    })
    return info

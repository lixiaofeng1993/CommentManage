from django.db import models


class User(models.Model):
    uid = models.IntegerField(default=0, primary_key=True, help_text="用户编号")
    level = models.IntegerField(default=0, help_text="用户等级")
    following = models.IntegerField(default=0, help_text="用户粉丝数")
    name = models.CharField(max_length=100, null=True, help_text="用户名称")
    sign = models.CharField(max_length=1000, null=True, help_text="用户简介")

    class Meta:
        db_table = "user"


class Video(models.Model):
    vid = models.IntegerField(default=0, help_text="视频编号", primary_key=True)
    favorite = models.IntegerField(default=0, help_text="点赞数")
    video_share = models.IntegerField(default=0, help_text="分享数")
    video_like = models.IntegerField(default=0, help_text="喜爱数")
    tag_names = models.CharField(max_length=500, null=True, help_text="视频标签")
    title = models.CharField(max_length=500, null=True, help_text="视频名称")
    description = models.CharField(max_length=500, null=True, help_text="视频简介")
    reply = models.IntegerField(default=0, help_text="")

    class Meta:
        db_table = "video"


class Comment(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    # vid = models.IntegerField(default=0, help_text="视频编号")
    vid = models.ForeignKey(Video, on_delete=models.CASCADE, default="", null=True, help_text="视频ID")
    barrage = models.CharField(max_length=1000, null=True, help_text="评论内容")
    label = models.IntegerField(default=None, null=True, help_text="评论情感")
    dt = models.DateTimeField("评论时间", null=True, auto_now_add=True)
    # uid = models.IntegerField(default=None, null=True, help_text="用户编号")
    uid = models.ForeignKey(User, on_delete=models.CASCADE, default="", null=True, help_text="用户ID")

    class Meta:
        db_table = "barrage_classification"

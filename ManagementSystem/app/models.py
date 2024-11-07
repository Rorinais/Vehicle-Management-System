import uuid
from datetime import datetime

from django.db import models

from django.utils import timezone

timezone.now()


# python manage.py makemigrations
# python manage.py migrate


class Vehicle(models.Model):
    LicensePlate = models.CharField(verbose_name="车牌号", max_length=20)
    Name = models.CharField(verbose_name="姓名", max_length=20)
    phone = models.CharField(verbose_name="电话", max_length=20)
    VehicleColor = models.CharField(verbose_name="车牌颜色", max_length=20)

    def __str__(self):
        return self.LicensePlate


class User(models.Model):
    phone = models.CharField(verbose_name="电话", max_length=32)
    Account = models.CharField(verbose_name="账号", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=128)
    gender_choices = (
        (1, "男"),
        (2, "女"),
        (3, "保密"),
    )
    Sex = models.SmallIntegerField(verbose_name="性别", choices=gender_choices, default=1)


class Admin(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=32)
    gender_choices = (
        (1, "男"),
        (2, "女"),
        (3, "保密"),
    )
    sex = models.SmallIntegerField(verbose_name="性别", choices=gender_choices, default=1)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    admin_choices = (
        (0, "否"),
        (1, "是"),
    )

    admin = models.SmallIntegerField(verbose_name="是否为管理员", choices=admin_choices, default=0)


class Plate(models.Model):
    LicensePlate = models.CharField(verbose_name="车牌号", max_length=30)
    created_in = models.DateTimeField(auto_now_add=True, verbose_name="进入时间")

    created_out = models.DateTimeField(auto_now_add=False, verbose_name="外出时间", null=True, blank=True)
    user = models.ForeignKey(Admin, on_delete=models.SET_NULL, verbose_name="用户", null=True)


class Order(models.Model):
    order_number = models.CharField(verbose_name="订单号", max_length=30)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True, verbose_name="支付时间")
    plate = models.ForeignKey(Plate, on_delete=models.SET_NULL, null=True, verbose_name="车牌号")

    status_choices = (
        (0, "否"),
        (1, "是"),
    )

    status = models.SmallIntegerField(verbose_name="是否已支付", choices=status_choices, default=0)



# CREATE TABLE vehicle (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     LicensePlate VARCHAR(20) NOT NULL,
#     Name VARCHAR(20) NOT NULL,
#     phone VARCHAR(20) NOT NULL,
#     VehicleColor VARCHAR(20) NOT NULL
# );
#
# CREATE TABLE user (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     phone VARCHAR(32) NOT NULL,
#     Account VARCHAR(32) NOT NULL,
#     password VARCHAR(128) NOT NULL,
#     Sex SMALLINT NOT NULL DEFAULT 1
# );
#
# CREATE TABLE datetimefield (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     LicensePlate VARCHAR(30) NOT NULL,
#     created_in DATETIME DEFAULT CURRENT_TIMESTAMP,
#     created_out DATETIME DEFAULT CURRENT_TIMESTAMP
# );
#
# CREATE TABLE admin (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     username VARCHAR(32) NOT NULL,
#     password VARCHAR(32) NOT NULL
# );

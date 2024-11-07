import datetime
import random
import time
from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators import gzip
import OpenCV
from app import models

import pytz

MAX_ATTEMPTS = 1000  # 最大尝试次数


def check_duplicate_order_number(order_number):
    # 假设订单号存储在名为orders的数据库表中，order_number字段为订单号字段
    existing_order = models.Order.objects.filter(order_number=order_number).first()
    if existing_order:
        return True  # 订单号已存在
    return False  # 订单号不存在


def generate_order_number(attempts=0):
    if attempts >= MAX_ATTEMPTS:
        raise Exception("无法生成不重复的订单号")  # 达到最大尝试次数，抛出异常或进行其他处理

    timestamp = str(int(time.time()))[-5:]  # 获取当前时间的时间戳，并转换为字符串
    random_number = str(random.randint(1000, 9999))
    number = timestamp + random_number

    if check_duplicate_order_number(number):
        return generate_order_number(attempts + 1)
    return number


def create_order(plate):
    order_number = generate_order_number()
    print(order_number)
    last_record = models.Plate.objects.filter(LicensePlate=plate).order_by(
        '-id').first()
    if last_record:
        time_now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

        # 将最后一条记录的 created_out 转换为带有时区信息的 datetime.datetime 对象
        last_created_out = last_record.created_out.astimezone(pytz.timezone('Asia/Shanghai'))

        time_difference = time_now - last_created_out
        amount = time_difference.total_seconds() * 10
        print(amount)
        amount = Decimal(str(amount))
        rounded_amount = amount.quantize(Decimal('0.00'))
        print(amount)

        # 创建订单
        models.Order.objects.create(
            order_number=order_number,
            amount=rounded_amount,
            plate=last_record,
            status=0
        )


@gzip.gzip_page
def video(request):
    return StreamingHttpResponse(OpenCV.read_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


def video_out(request):
    return StreamingHttpResponse(OpenCV.read_out(), content_type='multipart/x-mixed-replace; boundary=frame')


car_in = []


def get_txt(request):
    data = OpenCV.read_txt()
    # 把{'frame_list': [['京AHK666', 0.81118625, 0, [261, 28, 366, 65]]],
    #  'time': datetime.datetime(2023, 11, 6, 7, 19, 25, 878208)}变成字典

    f_list = data[0]
    time = datetime.datetime.now()

    if f_list[0]:
        if f_list[0] not in car_in:
            car_in.append(f_list[0])
            print(f"{f_list[0]} 进入了停车场")
            models.Plate.objects.create(LicensePlate=f_list[0])

    data = {
        "v": f_list[0],
        "time": time
    }
    return JsonResponse(data)


def get_out(request):
    data = OpenCV.read_txtout()

    if data:
        f_list = data[0]
        data_list = data[0][0]
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if f_list[0]:
            if f_list[0] in car_in:

                print(f"{f_list[0]} 离开了停车场")
                last_data = models.Plate.objects.filter(LicensePlate=f_list[0], created_out__isnull=True).order_by(
                    '-id').first()
                if last_data:
                    last_data.created_out = time
                    last_data.save()
                    car_in.remove(f_list[0])
                    create_order(f_list[0])

        data = {
            "v": data_list,
            "time": time
        }
        return JsonResponse(data)
    return HttpResponse("操作失败")


def show_video(request):
    return render(request, "show_video.html")


def show_out(request):
    return render(request, "show_out.html")

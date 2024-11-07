import random
import time

from django.shortcuts import render, redirect
from app import models
from app.custom.page import Page
from django import forms
from app.custom.encrypt import md5
from django.core.exceptions import ValidationError
import datetime


# 管理员信息编辑
class AdminModelFrom(forms.ModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput
    )

    class Meta:
        model = models.Admin
        fields = ["username", "password", "confirm_password"]
        widgets = {
            "password": forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return pwd

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("confirm_password")
        if confirm != pwd:
            raise ValidationError("密码不一致，请重新输入")
        return confirm


class AdminEditModelFrom(forms.ModelForm):
    class Meta:
        model = models.Admin
        fields = ["username", "password", "sex"]
        widgets = {
            "password": forms.PasswordInput(render_value=True)
        }


class AdminResetModelFrom(forms.ModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput
    )

    class Meta:
        model = models.Admin
        fields = ["username"]

    def clean_password(self):
        pwd = self.cleaned_data.get("password")

        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise ValidationError("密码不一致，请重新输入")
        return confirm


def admin_list(request):
    info_dict = request.session["info"]

    queryset = models.Admin.objects.all()

    page_object = Page(request, queryset)
    page_queryset = page_object.page_queryset
    page_string = page_object.html()

    context = {
        "queryset": page_queryset,
        "page_string": page_string
    }

    return render(request, "admin_list.html", context)


def admin_add(request):
    title = "新建"
    if request.method == "GET":
        form = AdminModelFrom()
        return render(request, "change.html", {"form": form, "title": title})

    form = AdminModelFrom(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {"form": form, "title": title})


def admin_edit(request, nid):
    title = "编辑"
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect("/admin/list/")
    if request.method == "GET":
        form = AdminEditModelFrom(instance=row_object)
        return render(request, "change.html", {"form": form, "title": title})
    form = AdminEditModelFrom(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {"form": form, "title": title})


def admin_delete(request, nid):
    models.Admin.objects.filter(id=nid).delete()
    return redirect("/admin/list/")


def admin_reset(request, nid):
    row_object = models.Admin.objects.filter(id=nid).fist()
    if not row_object:
        return redirect("/admin/list/")
    title = "重置密码-{}".format(row_object.username)

    if request.method == "GET":
        form = AdminResetModelFrom()
        return render(request, "change.html", {"form": form, "title": title})

    form = AdminResetModelFrom(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {"form": form, "title": title})


def admin_time(request):
    from app.custom.page import Page

    data_dict = {}
    search_data = request.GET.get("q", "")
    if search_data:
        data_dict["Name__contains"] = search_data

    queryset = models.Plate.objects.all()
    page_object = Page(request, queryset)
    page_queryset = page_object.page_queryset
    page_string = page_object.html()

    context = {"queryset": page_queryset,
               "search_data": search_data,
               "page_string": page_string}

    return render(request, "admin_plate.html", context)


def admin_time_delete(request, nid):
    models.Plate.objects.filter(id=nid).delete()
    return redirect("/admin/time/")


def admin_pay_delete(request, nid):
    models.Order.objects.filter(id=nid).delete()
    return redirect("/admin/pay/list/")


def admin_pay_list(request):
    from app.custom.page import Page
    # for i in range(300):
    # created_in = datetime.datetime.now()
    #
    # models.DateTimeField.objects.create(LicensePlate="京A0000", created_in=created_in)
    # if created_in:
    #     models.DateTimeField.objects.filter(LicensePlate="京A0000").update(created_out=created_in)
    page_str_list = []
    data_dict = {}
    search_data = request.GET.get("q", "")
    if search_data:
        data_dict["Name__contains"] = search_data

    # queryset = models.User.objects.filter(**data_dict).order_by("Name")
    queryset = models.Order.objects.all()
    page_object = Page(request, queryset)
    page_queryset = page_object.page_queryset
    page_string = page_object.html()

    context = {"queryset": page_queryset,
               "search_data": search_data,
               "page_string": page_string,
               }

    return render(request, "admin_order.html", context)

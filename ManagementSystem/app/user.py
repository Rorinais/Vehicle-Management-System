import json
from decimal import Decimal
from app import models
from django import forms
from app.custom.encrypt import md5
from django.core.exceptions import ValidationError
import datetime
from django.shortcuts import render, redirect, HttpResponse
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import decodebytes, encodebytes
from urllib.parse import quote_plus


class AdminUserModelFrom(forms.ModelForm):
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

        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise ValidationError("密码不一致，请重新输入")
        return confirm


def user_list(request):
    from app.custom.page import Page
    # for i in range(300):
    # models.User.objects.create(phone="1", Account="123366", password="123456", Sex="1")
    page_str_list = []
    data_dict = {}
    search_data = request.GET.get("q", "")
    if search_data:
        data_dict["Name__contains"] = search_data

    # queryset = models.User.objects.filter(**data_dict).order_by("Name")

    id = request.session["info"]["id"]
    queryset = models.Admin.objects.filter(id=id).all()

    page_object = Page(request, queryset)
    page_queryset = page_object.page_queryset
    page_string = page_object.html()

    context = {"queryset": page_queryset,
               "search_data": search_data,
               "page_string": page_string}

    return render(request, "user_list.html", context)


def admin_user_add(request):
    title = "新建用户"
    if request.method == "GET":
        form = AdminUserModelFrom
        return render(request, "change.html", {"form": form, "title": title})

    form = AdminUserModelFrom(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/admin/user/list/")
    return render(request, "change.html", {"form": form, "title": title})


def admin_user_delete(request, nid):
    models.User.objects.filter(id=nid).delete()
    return redirect("/admin/user/list/")


def admin_edit(request, nid):
    title = "编辑"
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect("/admin/list/")
    if request.method == "GET":
        form = AdminUserModelFrom(instance=row_object)
        return render(request, "change.html", {"form": form, "title": title})
    form = AdminUserModelFrom(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {"form": form, "title": title})


def user_time(request):
    from app.custom.page import Page

    data_dict = {}
    search_data = request.GET.get("q", "")
    if search_data:
        data_dict["Name__contains"] = search_data

    id = request.session["info"]["id"]
    queryset = models.Plate.objects.filter(user_id=id).all()

    page_object = Page(request, queryset)
    page_queryset = page_object.page_queryset
    page_string = page_object.html()

    context = {"queryset": page_queryset,
               "search_data": search_data,
               "page_string": page_string}

    return render(request, "user_plate.html", context)


def user_pay_list(request):
    _object = models.Order.objects.filter(order_number="019021495").first()
    _object.status = 1
    _object.save()

    from app.custom.page import Page

    id = request.session["info"]["id"]

    data_dict = {}
    search_data = request.GET.get("q", "")
    if search_data:
        data_dict["Name__contains"] = search_data

    user = models.Order.objects.all()

    queryset = models.Order.objects.filter(plate__user=id).all()

    page_object = Page(request, queryset)
    page_queryset = page_object.page_queryset
    page_string = page_object.html()

    context = {"queryset": page_queryset,
               "search_data": search_data,
               "page_string": page_string}

    return render(request, "user_order.html", context)


def user_pay(request, nid):
    order = models.Order.objects.get(id=nid)

    amount = float(order.amount)

    if order.status == 0:
        params = {
            'app_id': '9021000132696123',
            'method': 'alipay.trade.page.pay',
            'format': 'JSON',
            'return_url': 'http://127.0.0.1:8000/user/pay/notify/',
            'notify_url': 'http://127.0.0.1:8000/user/pay/notify/',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'version': '1.0',
            'biz_content': json.dumps({
                'out_trade_no': order.order_number,
                'trade_no': order.order_number,
                'product_code': 'FAST_INSTANT_TRADE_PAY',
                'total_amount': amount,
                # 'refund_amount': 1.0,
                'subject': "停车费用"
            }, separators=(',', ':'))
        }
        unsigned_string = "&".join(["{0}={1}".format(k, params[k]) for k in sorted(params)])

        private_key = RSA.importKey(open("files/应用私钥RSA2048.txt").read())
        signer = PKCS1_v1_5.new(private_key)
        signature = signer.sign(SHA256.new(unsigned_string.encode("utf-8")))

        sign_string = encodebytes(signature).decode("utf8").replace('\n', '')

        result = "&".join(["{0}={1}".format(k, quote_plus(params[k])) for k in sorted(params)])
        result = result + "&sign=" + quote_plus(sign_string)

        gateway = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
        pay_url = "{}?{}".format(gateway, result)
        _object = models.Order.objects.filter(order_number=order.order_number).first()
        _object.status = 1
        _object.save()
        return redirect(pay_url)
    return HttpResponse("您已经支付")


def user_pay_notify(request):
    if request.method == "GET":
        pass

    else:
        from urllib.parse import parse_qs
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)
        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]
        sign = post_dict.pop('sign', None)
        out_trade_no = post_dict["out_trade_no"]
        _object = models.Order.objects.filter(order_number=out_trade_no).first()
        _object.status = 1
        _object.save()

    return HttpResponse("您已交付")


def process_data(request):
    if request.method == 'POST':
        received_data = request.POST.get('data')
        print(received_data)

        id = request.session["info"]["id"]
        queryset = models.Plate.objects.filter(LicensePlate=received_data).all()
        if queryset:
            for i in queryset:
                i.user_id = id
                i.save()

        return redirect('/user/list/')

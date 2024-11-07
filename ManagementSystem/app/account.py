from django.shortcuts import render, redirect, HttpResponse
from django import forms
from app import models
from app.custom.encrypt import md5
from app.custom.image import check_code
from io import BytesIO
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={"class": "form-control"}, render_value=True),
        required=True
    )
    code = forms.CharField(
        label='验证码',
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True
    )

    def cleaned_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

    # def clean_confirm_password(self):
    #     pwd = self.cleaned_data.get("password")
    #     confirm = md5(self.cleaned_data.get("confirm_password"))
    #     if confirm != pwd:
    #         raise ValidationError("密码不一致")
    #     return confirm


def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user_input_code = form.cleaned_data.pop("code")
        code = request.session.get("image_code", "")
        # 验证码验证
        if code.upper() != user_input_code.upper():
            form.add_error("code", "验证码错误")
            return render(request, "login.html", {"form": form})
        # 账号密码验证
        admin_object = models.Admin.objects.filter(**form.cleaned_data).first()
        if not admin_object:
            form.add_error("password", "用户名或密码错误")
            return render(request, "login.html", {"form": form})

        request.session["info"] = {"id": admin_object.id, "name": admin_object.username}
        request.session.set_expiry(60 * 60 * 24 * 7)
        # 管理员用户角色判断
        username = form.cleaned_data['username']
        user = models.Admin.objects.filter(username=username)
        if user.exists():
            admin_user = user.first()
            if admin_user.admin == 1:
                return redirect("/admin/list/")

        return redirect("/user/list/")
    return render(request, "login.html", {"form": form})


def logout(request):
    request.session.clear()
    return redirect("login")


def image_code(request):
    img, code_string = check_code()
    request.session["image_code"] = code_string
    request.session.set_expiry(60)
    stream = BytesIO()
    img.save(stream, "png")
    return HttpResponse(stream.getvalue())


class AdminModelFrom(forms.ModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput
    )

    class Meta:
        model = models.Admin
        fields = ["username", "password", "confirm_password"]
        widget = {
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


def register(request):
    title = "注册"
    if request.method == "GET":
        form = AdminModelFrom()
        return render(request, "register.html", {"form": form, "title": title})

    form = AdminModelFrom(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/login/")
    return render(request, "register.html", {"form": form, "title": title})

# def forgot_Pwd(request):
#     title = "修改密码"
#     Account = request.GET.get('Account')
#     row_object = models.User.objects.filter(Account=Account).fist()
#     if not row_object:
#         return redirect("login/")
#     if request.method == "GET":
#         form = UserEditModelFrom(instance=row_object)
#         return render(request, "change.html", {"form": form, "title": title})
#     form = UserEditModelFrom(data=request.POST, instance=row_object)
#     if form.is_valid():
#         form.save()
#         return redirect("login/")
#     return render(request, "change.html", {"form": form, "title": title})

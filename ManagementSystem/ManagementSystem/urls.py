"""
URL configuration for ManagementSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from app import views, admin, account, user
from django.urls import path, include

urlpatterns = [
    # 通用部分
    # 注册
    path('register/', account.register, name="register"),  # 管理员账号无法注册
    # 登录
    path('login/', account.login, name="login"),
    # 登录忘记密码
    # path('forgotPwd/', account.forgot_Pwd, name="forgotPwd"),    # 管理员账号的密码无法修改，只能联系更高层的管理者
    # 图片验证码
    path("image/code/", account.image_code),
    # 注销
    path('logout/', account.logout),

    # 管理员模式
    # 主页面
    path('admin/list/', admin.admin_list),
    # 增删改查
    path('admin/add/', admin.admin_add),
    path('admin/<int:nid>/delete/', admin.admin_delete),
    path('admin/<int:nid>/edit/', admin.admin_edit),
    # 重置
    path('admin/<int:nid>/reset/', admin.admin_reset),
    # # 管理员管理的用户表
    path('user/list/', user.user_list, name='user_list'),
    # path('admin/user/add/', admin.admin_user_add),
    # path('admin/user/<int:nid>/delete/', admin.admin_user_delete),
    # path('admin/user/<int:nid>/reset/', admin.admin_plate_reset),
    # # 管理员管理的车牌信息表
    # path('admin/plate/', admin.admin_plate),
    # path('admin/plate/add/', admin.admin_plate_add),
    # path('admin/plate/<int:nid>/reset/', admin.admin_plate_reset),
    # path('admin/plate/<int:nid>/delete/', admin.admin_plate_delete),
    # 进出时间表
    path('admin/time/', admin.admin_time),
    path('admin/<int:nid>/time/', admin.admin_time_delete),
    path('admin/<int:nid>/pay/', admin.admin_pay_delete),

    path('user/time/', user.user_time),
    # 车牌识别
    path('video/', views.video, name="video"),
    path('get/txt/', views.get_txt),
    path('show/video/', views.show_video),

    path('video_out/', views.video_out, name="out"),
    path('get/out/', views.get_out),
    path('show/out/', views.show_out),

    path('admin/pay/list/', admin.admin_pay_list),
    path('user/pay/list/', user.user_pay_list),

    path('user/<int:nid>/pay/', user.user_pay),
    path('user/pay/notify/', user.user_pay_notify),
    path('processData/', user.process_data, name='process_data'),
]

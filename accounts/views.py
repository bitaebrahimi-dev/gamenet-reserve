from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import  login, logout
from .forms import RegisterForm, LoginForm
from .services import register_user



def register(request):
    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            print("FORM VALID")

            register_user(form)

            messages.success(
                request,
                'ثبت‌نام با موفقیت انجام شد.'
            )

            return redirect('login')

        else:
            print(form.errors)

    else:
        form = RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


def login_view(request):
    if request.method == 'POST':

        form = LoginForm(
            request=request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()

            login(request, user)

            messages.success(
                request,
                'ورود با موفقیت انجام شد.'
            )

            return redirect('device_list')

    else:

        form = LoginForm(request=request)

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )


def logout_view(request):
    logout(request)

    messages.success(
        request,
        'با موفقیت از حساب کاربری خارج شدید.'
    )

    return redirect('login')

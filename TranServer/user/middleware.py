from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone


class UpdateLastActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Update last_active if user is authenticated
        if request.user.is_authenticated:
            user = request.user
            user.last_active = timezone.now()
            user.save()

        return response


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            exceptions = [
                reverse("login"),
                reverse("signup"),
            ]
            if request.path not in exceptions:
                return redirect(settings.LOGIN_URL)

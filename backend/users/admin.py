from django.contrib import admin
from .models import User, EmailLoginLink, EmailOTP, ResetPasswordLink

admin.site.register([User, EmailOTP, EmailLoginLink, ResetPasswordLink])

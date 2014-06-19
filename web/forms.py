from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _

class LoginForm(AuthenticationForm):
    error_css_class = "has-warning"
    required_css_class = ""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _

from web.models import Character

class LoginForm(AuthenticationForm):
    error_css_class = "has-warning"
    required_css_class = ""

class CharacterCreateForm(forms.Form):
    class Meta:
        model = Character
        fields = ['name','character_class','character_race']
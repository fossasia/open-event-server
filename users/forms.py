from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import ModelForm
from .models import CustomUser, Exhibitor


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("name",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

class ExhibitorCreationForm(ModelForm):
    class Meta:
        model = Exhibitor
        fields = ['description', 'website']

class ExhibitorChangeForm(ModelForm):
    class Meta:
        model = Exhibitor
        fields = ['description', 'website']
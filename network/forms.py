from django import forms
from .models import Person, City, Company

class SearchForm(forms.Form):
    querry = forms.CharField(label='Search', max_length=50)

class AlumniForm(forms.ModelForm):
    data = forms.CharField(widget=forms.Textarea(), label='Please tell us a little about yourself')
    image = forms.URLField(label="Please provide a URL for a photograph of yourself")

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'batch', 'company', 'city', 'facebook_profile', 'linkedin_profile', 'instagram_profile']


class StudentForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'year', 'branch']

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'branch', 'rollNo']

class CityForm(forms.ModelForm):

    class Meta:
        model = City
        fields = ['name']

class CompanyForm(forms.ModelForm):
    data = forms.CharField(widget=forms.Textarea(), label='Please tell us a little background about the company, like where is the headquarters located, and the primary area of focus of the company')

    class Meta:
        model = Company
        fields = ['name']

class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Person
        fields = ['rollNo']

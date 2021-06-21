#Overriding the authentiaction backend for email addresses
from django.contrib.auth.backends import BaseBackend
from .models import Person

class authBackend(BaseBackend):
    def authenticate(self, request, username, password):
        try:
            user = Person.objects.get(email=username)
            success = user.check_password(password)
            if success:
                return user
        except Person.DoesNotExist:
            user = None
        return user

    def get_user(self, uid):
        try:
            return Person.objects.get(pk=uid)
        except:
            return None

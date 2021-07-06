from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinLengthValidator

class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, rollNo, password=None):
        if not email:
            raise ValueError("Users must have an email")
        if not rollNo:
            raise ValueError("Users must have a roll number")
        if not first_name:
            raise ValueError("Users must have a first name")
        if not last_name:
            raise ValueError("Users must have a last name")

        user = self.model(
                first_name=first_name,
                last_name=last_name,
                email=self.normalize_email(email),
                rollNo=rollNo
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, is_current, password):
        user = self.model(
                is_current=is_current,
                first_name=first_name,
                last_name=last_name,
                email=self.normalize_email(email),
                password=password
            )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class Company(models.Model):
    name = models.CharField(max_length=50, default="NAME")
    people = models.ManyToManyField('Person', default=None, related_name='employes', null=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=50, default="NAME")
    companies = models.ManyToManyField(Company, default=None, related_name='located_at', null=True)
    people = models.ManyToManyField('Person', default=None, related_name='residents', null=True)

    def __str__(self):
        return self.name


class Person(AbstractBaseUser):
    first_name = models.CharField(max_length=15, default="NAME", null=False, blank=False)
    last_name = models.CharField(max_length=15, default="NAME", null=False, blank=False)
    email = models.EmailField(unique=True, default="NAME", null=False, blank=False)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    date_joined = models.DateTimeField(verbose_name='date_joined', auto_now_add=True, null=True, blank=True)
    last_login = models.DateTimeField(verbose_name='last_login', auto_now_add=True, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_current = models.BooleanField(default=True)
    batch = models.IntegerField(null=True, blank=False)
    facebook_profile = models.URLField(null=True, blank=True)
    instagram_profile = models.URLField(null=True, blank=True)
    linkedin_profile = models.URLField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, default=None, null=True, blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=None, null=True, blank=False)
    first = 1
    second = 2
    third = 3
    fourth = 4
    YEAR_CHOICES = (
        (first, 'first'),
        (second, 'second'),
        (third, 'third'),
        (fourth, 'fourth')
    )
    year = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    CSE = 'CSE'
    ECE = 'ECE'
    IT = 'IT'
    Branch_CHOICES = (
        (CSE, 'CSE'),
        (ECE, 'ECE'),
        (IT, 'IT')
    )
    branch = models.CharField(max_length=3, choices=Branch_CHOICES, default="CSE", null=True, blank=True)
    rollNo = models.CharField(validators=[MinLengthValidator(5)], max_length=5, blank=True)

    image = models.URLField(blank=True, null=True)
    #content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['is_current', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.rollNo

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

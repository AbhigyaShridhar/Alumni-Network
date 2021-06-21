from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
import markdown2
import re
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.contrib.auth import authenticate
from django.contrib.auth import login, logout

from . import util
from .models import Person, City, Company
from .forms import AlumniForm, RegisterForm, SearchForm, StudentForm, CityForm, CompanyForm, LoginForm

@login_required
def index(request):
    if not request.user.is_authenticated:
        return render(request, "network/login.html", {
            "form": LoginForm(),
            "search_form": SearchForm()
        })
    else:
        return render(request, "network/index.html", {
            "entries": util.list_entries("companies"),
            "type": 'companies',
            "search_form": SearchForm()
        })

class login_view(View):
    template = "network/login.html"
    success_url = "network:index"

    def get(self, request):
        form = LoginForm()
        return render(request, self.template, {
            'form': form,
            'message': "Welcome to IIIT Una's Alumni Network  \nPlease Login to get access",
            "search_form": SearchForm()
        })

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            rollNo = form.cleaned_data["rollNo"]
            email = rollNo + '@iiitu.ac.in'
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse_lazy(self.success_url))
            else:
                return render(request, self.template, {
                    'form': LoginForm(),
                    'message': "Invalid Roll Number or password",
                    "search_form": SearchForm()
                })
        else:
            return render(request, self.template, {
                'form': LoginForm(),
                'message': "Please Enter all fields",
                "search_form": SearchForm()
            })

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))

class Register(View):
    template = 'network/register.html'

    def get(self, request):
        form = RegisterForm()
        return render(request, self.template, {
            'form': form,
            'message': 'Please Enter Your Complete Five digit Roll Number',
            "search_form": SearchForm()
        })

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            rollNo = form.cleaned_data["rollNo"]
            email = rollNo + '@iiitu.ac.in'
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            p1 = form.cleaned_data["password"]
            p2 = form.cleaned_data["confirm_password"]
            if not p1 == p2:
                return render(request, self.template, {
                    'form': RegisterForm(),
                    'message': "Passwords don't match",
                    "search_form": SearchForm()
                })
            try:
                user = Person.objects.create_user(first_name, last_name, email, rollNo, p1)
                user.set_password(p1)
                user.is_active = False
                user.save()

            except IntegrityError:
                return render(request, self.template, {
                    'form': RegisterForm(),
                    'message': "An Account With This Roll Number Already Exists",
                    "search_form": SearchForm()
                })

            current_site = get_current_site(request)
            mail_subject = 'Welcome To IIITU Alumni Network'
            to_email = email
            ctx = {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            }
            message = render_to_string('network/email.html', ctx)
            mail = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            mail.content_subtype = "html"
            mail.send()
            return HttpResponse("A confirmation Email has been sent to your Institute email address. Please Confirm Your email to complete your registration")

@login_required
def profile(request):
    if request.user.is_current:
        form = StudentForm(initial={'first_name': request.user.first_name, 'last_name': request.user.last_name, 'year': request.user.year, 'branch': request.user.branch})
        return render(request, 'network/profile.html', {
            'form': form,
            "search_form": SearchForm()
        })
    else:
        form = AlumniForm(initial={'first_name': request.user.first_name, 'last_name': request.user.last_name, 'company': request.user.company, 'city': request.user.city, 'facebook_profile': request.user.facebook_profile, 'linkedin_profile': request.user.linkedin_profile, 'instagram_profile': request.user.instagram_profile, 'image': request.user.image})
        return render(request, 'network/profile.html', {
            'form': form,
            "search_form": SearchForm()
        })

@login_required
def make_alum(request):
    user = Person.objects.get(id=request.user.id)
    user.is_current = False
    user.save()
    return HttpResponseRedirect(reverse_lazy('network:profile'))

@login_required
def entry(request, type, name):
    if type == 'people':
        user = Person.objects.get(rollNo=name)
        url = user.image
        heading = user.first_name + ' ' + user.last_name
        entry = util.get_entry(name, type)
        if not entry is None:
            md = markdown2.Markdown()
            entry = md.convert(entry)
        return render(request, "network/entry.html", {
            "entry": entry,
            "heading": heading,
            "url": url,
            "type": 'people',
            "search_form": SearchForm()
        })
    elif type == 'companies':
        company = Company.objects.get(name=name)
        entry = util.get_entry(name, type)
        md = markdown2.Markdown()
        entry = md.convert(entry)
        entries = company.people.all()
        return render(request, "network/entry.html", {
            "entry": entry,
            "search_form": SearchForm(),
            "heading": name,
            "entries": entries,
            "type": type,
        })
    elif type == 'cities':
        city = City.objects.get(name=name)
        people = city.people.all()
        companies = city.companies.all()
        return render(request, "network/entry.html", {
            "heading": name,
            "people": people,
            "companies": companies,
            "type": type,
            "search_form": SearchForm()
        })
    else:
        return HttpResponse("Invalid URL")

@login_required
def update(request):
    user = Person.objects.get(id=request.user.id)
    if user.is_current:
        form = StudentForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            year = form.cleaned_data['year']
            branch = form.cleaned_data['branch']
            user.first_name = first_name
            user.last_name = last_name
            user.branch = branch
            user.year = year
            user.save()
            return HttpResponseRedirect(reverse_lazy('network:profile'))
        else:
            return render(request, 'network/profile.html', {
                'message': "You entered some invalid entries in the form please check and submit again",
                'form': StudentForm(initial={'first_name': user.first_name, 'last_name': user.last_name, 'year': user.year, 'branch': user.branch}),
                "search_form": SearchForm()
            })

    else:
        form = AlumniForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            batch = form.cleaned_data['batch']
            company = form.cleaned_data['company']
            city = form.cleaned_data['city']
            facebook_profile = form.cleaned_data['facebook_profile']
            linkedin_profile = form.cleaned_data['linkedin_profile']
            instagram_profile = form.cleaned_data['instagram_profile']
            data = form.cleaned_data['data']
            image = form.cleaned_data['image']

            user.first_name = first_name
            user.last_name = last_name
            user.company = company
            user.city = city
            user.facebook_profile = facebook_profile
            user.linkedin_profile = linkedin_profile
            user.instagram_profile = instagram_profile
            user.batch = batch
            user.image = image
            user.save()

            app_city = City.objects.get(name=city.name)
            if not company in app_city.companies.all():
                app_city.companies.add(company)
                app_city.save()

            if not user in app_city.people.all():
                app_city.people.add(user)
                app_city.save()

            if not user in company.people.all():
                company.people.add(user)
                company.save()

            c = company.name
            branch = request.user.branch

            text = '#' + first_name + ' ' + last_name + ' ' + branch + '(' + str(batch) + ')' + '\n' + '**Works at**: [' + c + '](/alum/companies/' + c.lower() + ')([' + city.name.lower() + '](/alum/cities/' + city.name.lower() + '))  \n  \n'
            text = text + 'Connect with ' + first_name + ' on [Linkedin](' + linkedin_profile + '), [Instagram](' + instagram_profile + ') or [Facebook](' + facebook_profile + ')  \n  \n'
            text = text + data
            util.save_entry(user.rollNo, text, 'people')


            return HttpResponseRedirect(reverse_lazy('network:entry', kwargs={'type': 'people', 'name': user.rollNo}))
        else:
            form = AlumniForm(initial={'first_name': user.first_name, 'last_name': user.last_name, 'company': user.company, 'city': user.city, 'facebook_profile': user.facebook_profile, 'linkedin_profile': user.linkedin_profile, 'instagram_profile': user.instagram_profile, 'image': user.image})
            return render(request, 'network/profile.html', {
                'form': form,
                'message': "Please enter valid details in the form",
                "search_form": SearchForm()
            })

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Person.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Person.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)

        if request.user.is_current:
            form = StudentForm(initial={'first_name': user.first_name, 'last_name': user.last_name, 'year': user.year, 'branch': user.branch})
            return render(request, 'network/profile.html', {
                'form': form,
                "search_form": SearchForm()
            })
        else:
            form = AlumniForm(initial={'first_name': user.first_name, 'last_name': user.last_name, 'company': user.company, 'city': user.city, 'facebook_profile': user.facebook_profile, 'linkedin_profile': user.linkedin_profile, 'instagram_profile': user.instagram_profile, 'image': user.image})
            return render(request, 'network/profile.html', {
                'form': form,
                "search_form": SearchForm()
            })
    else:
        return HttpResponse('Invalid URL, Please Contact Site Administrator')

class add_company(LoginRequiredMixin, View):
    template = "network/form.html"
    success_url = 'network:profile'

    def get(self, request):
        form = CompanyForm()
        return render(request, self.template, {
            'form': form,
            "search_form": SearchForm()
        })

    def post(self, request):
        form = CompanyForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            name = name.lower()
            data = form.cleaned_data["data"]
        else:
            return render(request, self.template, {
                'form': CompanyForm(),
                "search_form": SearchForm()
            })

        try:
            company = Company.objects.create(name=name)
            company.save()
        except IntegrityError:
            return render(request, self.template, {
                'form': CompanyForm(),
                'message': "Company with this name already exists in the database",
                "search_form": SearchForm()
            })
        text = '#' + name + '\n  \n'
        text = text + data
        util.save_entry(name, text, "companies")
        return HttpResponseRedirect(reverse_lazy(self.success_url))

class add_city(LoginRequiredMixin, View):
    template = 'network/form.html'
    success_url = 'network:profile'

    def get(self, request):
        form = CityForm()
        return render(request, self.template, {
            'form': form,
            "search_form": SearchForm()
        })

    def post(self, request):
        form = CityForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            name = name.lower()

        else:
            return render(request, self.template, {
                'form': CityForm(),
                'message': "Please enter a valid city name",
                "search_form": SearchForm()
            })

        try:
            city = City.objects.create(name=name)
            city.save()
        except IntegrityError:
            return render(request, self.template, {
                'form': CityForm(),
                'message': "A city with this name already exists",
                "search_form": SearchForm()
            })

        return HttpResponseRedirect(reverse_lazy(self.success_url))

def companies(request):
    return render(request, "network/index.html", {
            "entries": Company.objects.all(),
            "type": 'companies',
            "search_form": SearchForm()
        })

@login_required
def people(request):
    return render(request, "network/index.html", {
        "entries": Person.objects.filter(is_current=False),
        "type": 'people',
        "search_form": SearchForm()
    })

def cities(request):
    list = City.objects.all()
    return render(request, "network/index.html", {
        "entries": list,
        "type": 'cities',
        "search_form": SearchForm()
    })

#def search(request):
#    form = SearchForm(request.GET)
#    if form.is_valid():
#        querry = form.cleaned_data["querry"]
#    entries_c = util.list_entries('companies')
#    entries_p = util.list_entries('people')
#    results = []
#    for entry in entries:
#        if entry == querry:
#            entry = util.get_entry(entry)
#            md = markdown2.Markdown()
#            entry = md.convert(entry)
#            return render(request, "network/page.html", {
#                "entry": entry
#            })
#        elif re.search(querry, entry):
#            results.append(entry)
#    if not results:
#        return render(request, "network/index.html", {
#            "entries": util.list_entries(),
#            "message": "No results found for the querry!"
#        })
#    else:
#        return render(request, "network/search.html", {
#        "entries": results
#        })



















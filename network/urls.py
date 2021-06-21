from django.urls import path
from . import views

app_name = 'network'

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/logout', views.logout_view, name="logout_view"),
    path('accounts/login/', views.login_view.as_view(), name="login_view"),
    path('accounts/register', views.Register.as_view(), name="register"),
    path('profile', views.profile, name="profile"),
    path('profile/update', views.update, name="update"),
    path('alum/<str:type>/<str:name>', views.entry, name="entry"),
    path('make_alum', views.make_alum, name="make_alum"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('add_company', views.add_company.as_view(), name="add_company"),
    path('add_city', views.add_city.as_view(), name="add_city"),
    path('cities', views.cities, name="cities"),
    path('people', views.people, name="people"),
]

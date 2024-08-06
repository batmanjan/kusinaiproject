from django.urls import path
from . import views


urlpatterns = [
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('verify/', views.verify, name='verify'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('login/', views.login, name='login'),
    path('survey/', views.survey, name='survey'),
    path('home/', views.home, name='home'),
    path('homedish/<int:dish_id>/', views.homedish, name='homedish'),
    path('saved/', views.saved, name='saved'),
    path('saveddish/<int:dish_id>/', views.saveddish, name='saveddish'),
    path('cooked/', views.cooked, name='cooked'),
    path('settings/', views.settingss, name='settings'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('logout/', views.logout, name='logout'),
    path('about/', views.about, name='about'),  # Add this line
    path('faqs/', views.faqs, name='faqs'),      # Add this line
    path('terms/', views.terms, name='terms'),
    path('forgetpass/', views.forgetpass, name='forgetpass'),# Add this line
    path('verifyforgetpass/', views.verifyforgetpass, name='verifyforgetpass'),
    path('forgetnewpass/', views.forgetnewpass, name='forgetnewpass'),
    path('resend/', views.resend_otp, name='resend_otp'),  # Add this line
    path('save_to_saved/', views.save_to_saved, name='save_to_saved'),
    
]

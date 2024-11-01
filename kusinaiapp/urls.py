from django.urls import path
from . import views


urlpatterns = [
    path('', views.onboarding, name='onboarding'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('introduction/', views.introduction_view, name='introduction'),
    path('signup/', views.signup, name='signup'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('login/', views.login, name='login'),
    path('survey/', views.survey, name='survey'),
    path('home/', views.home, name='home'),
    path('homedish/<int:dish_id>/', views.homedish, name='homedish'),
    path('saved/', views.saved, name='saved'),
    path('saveddish/<int:dish_id>/', views.saveddish, name='saveddish'),
    path('cooked/', views.cooked, name='cooked'),
    path('settings/', views.settingss, name='settings'),
    path('editprofile/', views.edit_profile, name='editprofile'),
    path('logout/', views.logout, name='logout'),
    path('about/', views.about, name='about'),  # Add this line
    path('faqs/', views.faqs, name='faqs'),      # Add this line
    path('terms/', views.terms, name='terms'),
    path('forgetpass/', views.forgetpass, name='forgetpass'),# Add this line
    path('verifyforgetpass/', views.verifyforgetpass, name='verifyforgetpass'),
    path('forgetnewpass/', views.forgetnewpass, name='forgetnewpass'),
    path('resend/', views.resend_otp, name='resend_otp'),  # Add this line
    path('save_to_saved/', views.save_to_saved, name='save_to_saved'),
    path('verify_profile/', views.verify_profile, name='verify_profile'),
    path('verify_signup/', views.verify_signup, name='verify_signup'),
    path('save_dish/', views.save_dish, name='save_dish'),
    path('addrecipe/', views.addrecipe, name='addrecipe'),
    path('check_recipe/<int:dish_id>/', views.check_recipe, name='check_recipe'),
    path('check_if_saved/<int:dish_id>/', views.check_if_saved, name='check_if_saved'),
    path('chefhome/', views.chefhome, name='chefhome'),
    path('cheflogin/', views.cheflogin, name='cheflogin'),
    path('dish/<int:dish_id>/', views.dish_detail, name='dish_detail'),
    path('approve_dish/<int:dish_id>/', views.approve_dish, name='approve_dish'),
    path('delete-dish/<int:dish_id>/', views.delete_dish, name='delete_dish'),
    
]

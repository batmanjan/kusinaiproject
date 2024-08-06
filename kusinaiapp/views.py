from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash
from .models import CookedDish, Dish
from .models import Dish, DishPlan
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException

import random
import string
import logging

from .forms import (
    SignUpForm, LoginForm, OTPForm,
    PhoneNumberForm, VerificationCodeForm, NewPasswordForm, SurveyForm
)
from .models import AppUser


logger = logging.getLogger(__name__)




def signup(request):
    
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            username = form.cleaned_data['username']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            
            if AppUser.objects.filter(phone_number=phone).exists():
                form.add_error('phone', 'A user with this phone number already exists.')
            else:
                try:
                    user = User.objects.create_user(username=username, password=password)
                    app_user = AppUser(
                        user=user,
                        name=name,
                        username=username,
                        phone_number=phone,
                        password=password,
                        family_size=1,
                        age_range=[],
                        meal_preference=[],
                        allergies=[],
                        cooking_skills=''
                    )
                    app_user.save()
                    
                    verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
                    request.session['verification_token'] = verification_token
                    request.session['phone_number'] = phone

                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
                        to=phone,
                        channel='sms'
                    )
                    
                    return redirect('verify')

                except IntegrityError:
                    form.add_error(None, 'An error occurred while processing your request.')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})


def verify(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            phone_number = request.session.get('phone_number')

            if phone_number:
                try:
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    verification_check = client.verify \
                        .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                        .verification_checks \
                        .create(to=phone_number, code=otp)
                    
                    if verification_check.status == 'approved':
                        # Update user profile with saved data
                        profile_update = request.session.get('profile_update')
                        if profile_update:
                            user = request.user
                            user_profile = AppUser.objects.get(user=user)

                            user_profile.name = profile_update['name']
                            user_profile.username = profile_update['username']
                            user_profile.phone_number = profile_update['phone']
                            if profile_update['password']:
                                user.set_password(profile_update['password'])
                                user.save()
                            user_profile.save()

                            # Clear session data
                            request.session.pop('verification_sid', None)
                            request.session.pop('profile_update', None)
                            request.session.pop('phone_number', None)

                            # Redirect to login page
                            return redirect('login')
                        else:
                            messages.error(request, 'Profile update data not found. Please try again.')
                    else:
                        form.add_error(None, 'Invalid OTP. Please try again.')
                except TwilioException as e:
                    messages.error(request, f'Error during verification: {str(e)}')
                except Exception as e:
                    messages.error(request, f'An error occurred: {str(e)}')
            else:
                form.add_error(None, 'Phone number not found. Please start the verification process again.')
    else:
        form = OTPForm()

    return render(request, 'verify.html', {'form': form})





def tutorial(request):
    return render(request, 'tutorial.html')

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                
                try:
                    app_user = AppUser.objects.get(user=user)
                    if not app_user.survey_completed:  # Check if survey is completed
                        return redirect('survey')  # Redirect to survey if not completed
                except AppUser.DoesNotExist:
                    # Redirect to survey if AppUser profile does not exist
                    return redirect('survey')
                
                return redirect('home')  # Redirect to home if survey is completed
            else:
                form.add_error(None, 'Invalid username or password')
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


@login_required
def survey(request):
    user = request.user
    
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            family_size = form.cleaned_data.get('family_size')
            age_range = form.cleaned_data.get('age_range')
            meal_preference = form.cleaned_data.get('meal_preference')
            allergies = form.cleaned_data.get('allergies')
            other_allergies = form.cleaned_data.get('other_allergies')
            cooking_skills = form.cleaned_data.get('cooking_skills')

            # Ensure we are updating an existing record
            try:
                app_user = AppUser.objects.get(user=user)
            except AppUser.DoesNotExist:
                app_user = AppUser(user=user)
                app_user.save()  # Save if the record does not exist

            # Update fields
            app_user.family_size = family_size
            app_user.age_range = age_range if age_range else []
            app_user.meal_preference = meal_preference

            # Handle allergies
            if 'None' in allergies:
                app_user.allergies = ['None']
            else:
                app_user.allergies = allergies if allergies else []
                if other_allergies:
                    other_allergy_list = [allergy.strip() for allergy in other_allergies.split(',')]
                    app_user.allergies = list(set(app_user.allergies + other_allergy_list))

            app_user.cooking_skills = cooking_skills
            app_user.survey_completed = True
            app_user.save()

            # Log out the user
            logout(request)

            # Redirect to login page
            return redirect('login')

    else:
        try:
            app_user = AppUser.objects.get(user=user)
            form = SurveyForm(initial={
                'family_size': app_user.family_size,
                'age_range': app_user.age_range,
                'meal_preference': app_user.meal_preference,
                'allergies': app_user.allergies,
                'other_allergies': ', '.join([allergy for allergy in app_user.allergies if allergy != 'None']),
                'cooking_skills': app_user.cooking_skills,
            })
        except AppUser.DoesNotExist:
            form = SurveyForm()

    return render(request, 'survey.html', {'form': form})





@login_required
def home(request):
    # Get the selected budget and meal type from GET parameters
    budget_filter = request.GET.get('budget')
    meal_type_filter = request.GET.get('meal_type')
    
    # Initialize queryset
    dishes = Dish.objects.all()
    
    # Apply budget filter if present
    if budget_filter:
        dishes = dishes.filter(cost=budget_filter)
    
    # Apply meal type filter if present
    if meal_type_filter:
        dishes = dishes.filter(meal_type=meal_type_filter)
    
    context = {
        'dishes': dishes,
        'selected_budget': budget_filter,
        'selected_meal_type': meal_type_filter,
    }
    return render(request, 'home.html', context)





def save_to_saved(request):
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        category = request.POST.get('category')

        # Get the dish object
        try:
            dish = Dish.objects.get(id=dish_id)
        except Dish.DoesNotExist:
            return HttpResponse('Dish not found', status=404)

        # Get the AppUser instance for the current user
        try:
            app_user = AppUser.objects.get(user=request.user)
        except AppUser.DoesNotExist:
            return HttpResponse('User not found', status=404)

        # Create or update the DishPlan
        DishPlan.objects.update_or_create(
            user=app_user,  # Use AppUser instance here
            dish=dish,
            defaults={'plan': category}
        )

        return redirect('saved')  # Redirect to the saved page

    return HttpResponse('Invalid request', status=400)

@login_required
def homedish(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    return render(request, 'homedish.html', {'dish': dish})

@login_required
def saved(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        dish_plan_id = request.POST.get('dish_plan_id')

        logger.debug(f"Received action: {action}, dish_plan_id: {dish_plan_id}")

        try:
            app_user = AppUser.objects.get(user=request.user)
        except AppUser.DoesNotExist:
            logger.error('AppUser not found')
            return JsonResponse({'success': False, 'error': 'AppUser not found'}, status=404)

        if action == 'delete':
            try:
                dish_plan = get_object_or_404(DishPlan, id=dish_plan_id, user=app_user)
                dish_plan.delete()
                return JsonResponse({'success': True})
            except Exception as e:
                logger.error(f"Error deleting DishPlan: {e}")
                return JsonResponse({'success': False, 'error': 'Error performing action'}, status=500)

        elif action == 'done':
            try:
                dish_plan = get_object_or_404(DishPlan, id=dish_plan_id, user=app_user)
                dish = dish_plan.dish

                if CookedDish.objects.filter(user=app_user, dish=dish).exists():
                    dish_plan.delete()  # Remove from saved dishes
                    return JsonResponse({'success': True, 'error': 'Dish already marked as cooked'})
                
                CookedDish.objects.create(user=app_user, dish=dish)
                dish_plan.delete()  # Remove from saved dishes
                return JsonResponse({'success': True})
            except Exception as e:
                logger.error(f"Error marking dish as cooked: {e}")
                return JsonResponse({'success': False, 'error': 'Error performing action'}, status=500)

        return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

    try:
        app_user = AppUser.objects.get(user=request.user)
    except AppUser.DoesNotExist:
        return HttpResponse('AppUser not found', status=404)

    saved_dishes = {
        'breakfast': DishPlan.objects.filter(user=app_user, plan='Breakfast'),
        'lunch': DishPlan.objects.filter(user=app_user, plan='Lunch'),
        'dinner': DishPlan.objects.filter(user=app_user, plan='Dinner'),
    }

    context = {'saved_dishes': saved_dishes}
    return render(request, 'saved.html', context)


@login_required
def saveddish(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    user = get_object_or_404(AppUser, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        dish_plan_id = request.POST.get('dish_plan_id')

        if not dish_plan_id:
            return JsonResponse({'success': False, 'error': 'Dish plan ID missing'}, status=400)

        try:
            dish_plan = DishPlan.objects.get(id=dish_plan_id, user=user)
        except DishPlan.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dish plan not found'}, status=404)

        if action == 'delete':
            dish_plan.delete()
            return JsonResponse({'success': True})

        elif action == 'done':
            if CookedDish.objects.filter(user=user, dish=dish).exists():
                dish_plan.delete()  # Remove from saved dishes
                return JsonResponse({'success': False, 'error': 'Dish already marked as cooked'}, status=400)

            CookedDish.objects.create(user=user, dish=dish)
            dish_plan.delete()  # Remove from saved dishes
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

    dish_plan = DishPlan.objects.filter(dish=dish, user=user).first()
    return render(request, 'saveddish.html', {'dish': dish, 'dish_plan_id': dish_plan.id if dish_plan else None})




@login_required
def cooked(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        dish_id = request.POST.get('id')
        rating = request.POST.get('rating')

        if action == 'delete':
            CookedDish.objects.filter(id=dish_id).delete()
            return JsonResponse({'success': True})

        elif action == 'rate':
            try:
                cooked_dish = CookedDish.objects.get(id=dish_id)
                cooked_dish.rating = rating
                cooked_dish.save()
                return JsonResponse({'success': True})
            except CookedDish.DoesNotExist:
                return JsonResponse({'error': 'CookedDish not found'}, status=404)

    try:
        app_user = AppUser.objects.get(user=request.user)
    except AppUser.DoesNotExist:
        return HttpResponse('AppUser not found', status=404)

    cooked_dishes = CookedDish.objects.filter(user=app_user)
    ratings = range(1, 6)

    context = {
        'cooked_dishes': cooked_dishes,
        'ratings': ratings
    }
    return render(request, 'cooked.html', context)




def about(request):
    return render(request, 'about.html')  # Make sure you have 'about.html' template

def faqs(request):
    return render(request, 'faqs.html')

def terms(request):
    return render(request, 'terms.html')

def forgetpass(request):
    print("Forgetpass view called")
    
    phone_form = PhoneNumberForm(request.POST or None)
    code_form = OTPForm()
    new_password_form = NewPasswordForm()
    show_code_form = False
    show_new_password_form = False

    if request.method == 'POST':
        print("Request method is POST")
        
        # Debug print statements to check form submission
        print("Phone form submitted")
        print("Phone form data:", request.POST)
        
        if phone_form.is_valid():
            phone = phone_form.cleaned_data['phone']
            print("Phone number from form:", phone)
            
            # Check if the phone number exists in the database
            if AppUser.objects.filter(phone_number=phone).exists():
                print("Phone number found in database")
                
                # Debug Twilio credentials
                print("Twilio Account SID:", settings.TWILIO_ACCOUNT_SID)
                print("Twilio Auth Token:", settings.TWILIO_AUTH_TOKEN[:4] + '...')  # Show only the beginning for security

                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                
                try:
                    verification = client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
                        to=phone,
                        channel='sms'
                    )
                    print("Verification sent to phone:", phone)
                    
                    # Save phone number in session to use in the verification step
                    request.session['phone'] = phone
                    return redirect('verifyforgetpass')
                except TwilioRestException as e:
                    print("TwilioRestException:", e)
                    print("Error message:", e.msg)
                    messages.error(request, 'An error occurred while sending the verification code.')
            else:
                print("Phone number not found in database")
                messages.error(request, 'Phone number not found.')
        else:
            print("Phone form errors:", phone_form.errors)
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'forgetpass.html', {
        'phone_form': phone_form,
        'code_form': code_form,
        'new_password_form': new_password_form,
        'show_code_form': show_code_form,
        'show_new_password_form': show_new_password_form
    })
def verifyforgetpass(request):
    code_form = VerificationCodeForm(request.POST or None)

    if request.method == 'POST':
        print("Request method is POST")

        if code_form.is_valid():
            print("Code form is valid")
            code = code_form.cleaned_data['code']
            phone = request.session.get('phone')
            
            print("Entered code:", code)
            print("Phone number from session:", phone)
            
            if phone:
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                try:
                    verification_check = client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
                        to=phone, code=code
                    )
                    print("Verification check response:", verification_check)

                    if verification_check.status == 'approved':
                        print("Verification successful")
                        messages.success(request, 'Verification successful. You can now set a new password.')
                        return redirect('forgetnewpass')
                    else:
                        print("Invalid verification code")
                        messages.error(request, 'Invalid verification code. Please try again.')
                except TwilioException as e:
                    print("TwilioException occurred:", str(e))
                    messages.error(request, f'An error occurred while verifying the code: {str(e)}')
                except Exception as e:
                    print("Exception occurred:", str(e))
                    messages.error(request, 'An error occurred during verification. Please try again later.')
            else:
                print("Phone number not found in session")
                messages.error(request, 'Phone number not found. Please start the verification process again.')
        else:
            print("Code form errors:", code_form.errors)
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'verifyforgetpass.html', {'code_form': code_form})



def forgetnewpass(request):
    new_password_form = NewPasswordForm()

    if request.method == 'POST':
        new_password_form = NewPasswordForm(request.POST)
        
        if new_password_form.is_valid():
            new_password = new_password_form.cleaned_data['new_password']
            phone = request.session.get('phone')

            if phone:
                try:
                    # Get the user using the Django User model
                    app_user = AppUser.objects.get(phone_number=phone)
                    user = app_user.user
                    
                    # Update the password using Django's User model
                    user.set_password(new_password)
                    user.save()

                    # Optionally update the session hash
                    update_session_auth_hash(request, user)

                    messages.success(request, 'Password changed successfully.')
                    return redirect('login')
                except AppUser.DoesNotExist:
                    messages.error(request, 'User not found.')
            else:
                messages.error(request, 'Phone number not found. Please start the verification process again.')
        else:
            messages.error(request, 'Passwords do not match or other error.')

    return render(request, 'forgetnewpass.html', {'new_password_form': new_password_form})



@login_required
def settingss(request):
    return render(request, 'settings.html')

@login_required
def editprofile(request):
    user = request.user
    user_profile = AppUser.objects.get(user=user)

    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')

        # Check if passwords match
        if password and password != repassword:
            return render(request, 'editprofile.html', {
                'user': user,
                'userprofile': user_profile,
                'error': 'Passwords do not match'
            })

        # Save the phone number in session
        request.session['phone_number'] = phone

        # Send OTP via Twilio Verify API
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        try:
            verification = client.verify \
                .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                .verifications \
                .create(to=phone, channel='sms')

            # Save verification data in session
            request.session['verification_sid'] = verification.sid
            request.session['profile_update'] = {
                'name': name,
                'username': username,
                'phone': phone,
                'password': password
            }

            # Redirect to verify.html
            return redirect('verify')
        except TwilioException as e:
            messages.error(request, f'Failed to send verification code: {str(e)}')
    
    return render(request, 'editprofile.html', {
        'user': user,
        'userprofile': user_profile
    })

def logout(request):
    auth_logout(request)
    return redirect('login')


def resend_otp(request):
    if request.method == 'POST':
        phone_number = request.session.get('phone')
        if phone_number:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            try:
                client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
                    to=phone_number,
                    channel='sms'
                )
                messages.success(request, 'Verification code sent again.')
            except Exception as e:
                logger.error(f'Failed to resend verification code: {str(e)}')
                messages.error(request, 'Failed to resend verification code.')
        else:
            messages.error(request, 'Phone number not found. Please start the verification process again.')

    return redirect('verifyforgetpass')  # Redirect to the password recovery verification page








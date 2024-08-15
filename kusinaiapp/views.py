from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash
from .models import CookedDish, Dish
from .models import Dish, DishPlan
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator


from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException

import random
import string
import logging
import time

from .forms import (
    ProfileUpdateForm, SignUpForm, LoginForm, OTPForm,
    PhoneNumberForm, VerificationCodeForm, NewPasswordForm, SurveyForm, 
)
from .models import AppUser


logger = logging.getLogger(__name__)

def introduction_view(request):
    
    return render(request, 'introduction.html')

def onboarding(request):
    return render(request, 'onboarding.html')




def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            username = form.cleaned_data['username']
            phone = '+63' + form.cleaned_data['phone']
            password = form.cleaned_data['password']
            
            if AppUser.objects.filter(phone_number=phone).exists():
                form.add_error('phone', 'A user with this phone number already exists.')
            else:
                try:
                    # Store data in session for verification
                    verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
                    request.session['signup_data'] = {
                        'name': name,
                        'username': username,
                        'phone': phone,
                        'password': password
                    }
                    request.session['verification_token'] = verification_token
                    request.session['phone_number'] = phone
                    
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
                        to=phone,
                        channel='sms'
                    )
                    
                    return redirect('verify_signup')

                except Exception as e:
                    messages.error(request, f'An error occurred: {str(e)}')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})



def verify_signup(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.get_otp()  # Use get_otp method to concatenate OTP digits
            phone_number = request.session.get('phone_number')

            if phone_number:
                try:
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    verification_check = client.verify \
                        .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                        .verification_checks \
                        .create(to=phone_number, code=otp)
                    
                    if verification_check.status == 'approved':
                        signup_data = request.session.get('signup_data')
                        if signup_data:
                            user = User.objects.create_user(username=signup_data['username'], password=signup_data['password'])
                            app_user = AppUser(
                                user=user,
                                name=signup_data['name'],
                                username=signup_data['username'],
                                phone_number=signup_data['phone'],
                                password=signup_data['password'],
                                family_size=1,
                                age_range=[],
                                meal_preference=[],
                                allergies=[],
                                cooking_skills=''
                            )
                            app_user.save()

                            request.session.flush()  # Clear all session data
                            logger.info('Signup successful, redirecting to login page.')
                            return redirect('login')
                        else:
                            messages.error(request, 'Signup data not found. Please start the signup process again.')
                    else:
                        form.add_error(None, 'Invalid OTP. Please try again.')
                except Exception as e:
                    messages.error(request, f'Error during verification: {str(e)}')
            else:
                form.add_error(None, 'Phone number not found. Please start the verification process again.')
    else:
        form = OTPForm()

    return render(request, 'verify.html', {'form': form})



@login_required
def edit_profile(request):
    user = request.user
    user_profile = AppUser.objects.get(user=user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user_profile)
        if form.is_valid():
            profile_update = form.save(commit=False)
            
            # Store profile update data in session
            request.session['profile_update'] = {
                'name': profile_update.name,
                'username': profile_update.username,
                'phone': profile_update.phone_number,
                'password': form.cleaned_data.get('password')  # Capture new password if provided
            }

            # Send OTP
            phone_number = profile_update.phone_number
            if phone_number:
                try:
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    verification = client.verify \
                        .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                        .verifications \
                        .create(to=phone_number, channel='sms')
                    
                    if verification.status == 'pending':
                        return redirect('verify_profile')
                    else:
                        messages.error(request, 'Failed to send OTP. Please try again.')
                except Exception as e:
                    messages.error(request, f'Error sending OTP: {str(e)}')
            else:
                messages.error(request, 'Phone number is not provided.')
    else:
        form = ProfileUpdateForm(instance=user_profile)

    return render(request, 'editprofile.html', {'form': form})




@login_required
def verify_profile(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.get_otp()  # Use get_otp method to concatenate OTP digits
            phone_number = request.session.get('profile_update', {}).get('phone')

            if phone_number:
                try:
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    verification_check = client.verify \
                        .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                        .verification_checks \
                        .create(to=phone_number, code=otp)
                    
                    if verification_check.status == 'approved':
                        profile_update = request.session.get('profile_update')
                        if profile_update:
                            user = request.user
                            user_profile = AppUser.objects.get(user=user)

                            user_profile.name = profile_update['name']
                            user_profile.username = profile_update['username']
                            user_profile.phone_number = profile_update['phone']
                            user_profile.save()

                            user.username = profile_update['username']
                            if profile_update['password']:
                                user.set_password(profile_update['password'])
                            user.save()

                            request.session.flush()  # Clear session data
                            logger.info('Profile update successful, redirecting to login page.')
                            return redirect('login')
                        else:
                            messages.error(request, 'Profile update data not found. Please try again.')
                    else:
                        form.add_error(None, 'Invalid OTP. Please try again.')
                except Exception as e:
                    messages.error(request, f'Error during verification: {str(e)}')
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
    total_steps = 5
    current_step = int(request.session.get('survey_step', 1))

    if request.method == 'POST':
        form = SurveyForm(request.POST, prefix=f'step_{current_step}')
        
        if form.is_valid():
            step_data = form.cleaned_data
            app_user, created = AppUser.objects.get_or_create(user=user)

            # Print debug information
            print("Step Data:", step_data)
            print("User Selected Allergies:", step_data.get('allergies', []))  # Debug print for selected allergies

            # Update fields based on the current step
            update_app_user(app_user, step_data, current_step)

            # Print debug information
            print("Updated AppUser:", {
                'family_size': app_user.family_size,
                'age_range': app_user.age_range,
                'meal_preference': app_user.meal_preference,
                'allergies': app_user.allergies,
                'cooking_skills': app_user.cooking_skills,
                'survey_completed': app_user.survey_completed,
            })

            app_user.save()

            if current_step < total_steps:
                # Move to the next step
                request.session['survey_step'] = current_step + 1
                return redirect('survey')
            else:
                # Final step handling
                logout(request)
                return redirect('login')
        else:
            # Log or handle form errors
            print("Form errors:", form.errors)
            return HttpResponseBadRequest('Invalid form submission.')

    else:
        if 'survey_step' not in request.session:
            request.session['survey_step'] = 1

        current_step = request.session.get('survey_step', 1)
        initial_data = get_initial_data(user, current_step)
        form = SurveyForm(initial=initial_data, prefix=f'step_{current_step}')

    return render(request, 'survey.html', {
        'form': form,
        'current_step': current_step,
        'total_steps': total_steps,
    })


def update_app_user(app_user, step_data, step):
    if step == 1:
        app_user.family_size = step_data.get('family_size')
    elif step == 2:
        app_user.age_range = step_data.get('age_range', [])
    elif step == 3:
        app_user.meal_preference = step_data.get('meal_preference', [])
    elif step == 4:
        allergies = step_data.get('allergies', [])

        # Debug print
        print("Raw allergies data:", allergies)

        # Normalize the data
        normalized_allergies = [a.lower() for a in allergies]

        if 'none' in normalized_allergies:
            app_user.allergies = ['None']
        else:
            app_user.allergies = list(set(allergies))  # Ensure uniqueness

        # Debug print
        print("Processed allergies data:", app_user.allergies)

    elif step == 5:
        app_user.cooking_skills = step_data.get('cooking_skills')
        app_user.survey_completed = True


def get_initial_data(user, current_step):
    try:
        app_user = AppUser.objects.get(user=user)
        allergies = app_user.allergies if app_user.allergies is not None else []

        return {
            'family_size': app_user.family_size if current_step == 1 else '',
            'age_range': app_user.age_range if current_step == 2 else [],
            'meal_preference': app_user.meal_preference if current_step == 3 else '',
            'allergies': allergies if current_step == 4 else [],
            'cooking_skills': app_user.cooking_skills if current_step == 5 else '',
        }
    except AppUser.DoesNotExist:
        return {
            'family_size': '' if current_step == 1 else '',
            'age_range': [] if current_step == 2 else [],
            'meal_preference': '' if current_step == 3 else '',
            'allergies': [] if current_step == 4 else [],
            'cooking_skills': '' if current_step == 5 else '',
        }





@login_required
def home(request):
    min_budget = request.GET.get('min_budget', '')
    max_budget = request.GET.get('max_budget', '')
    meal_type_filter = request.GET.get('meal_type', '')

    dishes = Dish.objects.all()

    # Handle budget filtering
    if min_budget and max_budget:
        try:
            min_budget = int(min_budget)
            max_budget = int(max_budget)
            if min_budget <= max_budget and 100 <= min_budget <= 1000 and 100 <= max_budget <= 1000:
                dishes = dishes.filter(cost__range=(min_budget, max_budget))
            else:
                dishes = Dish.objects.all()
        except ValueError:
            dishes = Dish.objects.all()
    elif min_budget or max_budget:
        dishes = Dish.objects.all()

    # Apply meal type filter if specified
    if meal_type_filter and meal_type_filter != 'Recommended Dishes':
        dishes = dishes.filter(meal_type=meal_type_filter)

    context = {
        'dishes': dishes,
        'min_budget': min_budget,
        'max_budget': max_budget,
        'selected_meal_type': meal_type_filter,
    }
    return render(request, 'home.html', context)





@login_required
def home(request):
    min_budget = request.GET.get('min_budget', '')
    max_budget = request.GET.get('max_budget', '')
    meal_type_filter = request.GET.get('meal_type', '')

    dishes = Dish.objects.all()

    # Handle budget filtering
    if min_budget and max_budget:
        try:
            min_budget = int(min_budget)
            max_budget = int(max_budget)
            if min_budget <= max_budget and 100 <= min_budget <= 1000 and 100 <= max_budget <= 1000:
                dishes = dishes.filter(cost__range=(min_budget, max_budget))
            else:
                dishes = Dish.objects.all()
        except ValueError:
            dishes = Dish.objects.all()
    elif min_budget or max_budget:
        dishes = Dish.objects.all()

    # Apply meal type filter if specified
    if meal_type_filter and meal_type_filter != 'Recommended Dishes':
        dishes = dishes.filter(meal_type=meal_type_filter)

    # Paginate dishes
    paginator = Paginator(dishes, 9)  # Show 9 dishes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'dishes': page_obj,
        'min_budget': min_budget,
        'max_budget': max_budget,
        'selected_meal_type': meal_type_filter,
        'page_obj': page_obj,
    }
    return render(request, 'home.html', context)







@login_required
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
            user=app_user,
            dish=dish,
            defaults={'plan': category}
        )

        # Check if filters are present, else redirect to Recommended Dishes
        meal_type = request.POST.get('meal_type')
        budget = request.POST.get('budget')

        if meal_type or budget:
            # Redirect with existing filters
            return HttpResponseRedirect(f"{reverse('home')}?meal_type={meal_type}&budget={budget}")
        else:
            # Redirect to Recommended Dishes without extra filters
            return HttpResponseRedirect(f"{reverse('home')}?meal_type=Recommended%20Dishes")

    return HttpResponse('Invalid request', status=400)


@login_required
def save_dish(request):
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        category = request.POST.get('category')
        meal_type = request.POST.get('meal_type')
        budget = request.POST.get('budget')
        referrer = request.POST.get('referrer')  # Get referrer URL

        # Validate inputs
        if not dish_id or not category:
            return HttpResponse('Invalid input', status=400)

        # Get the dish object
        dish = get_object_or_404(Dish, id=dish_id)

        # Get the AppUser instance for the current user
        app_user = get_object_or_404(AppUser, user=request.user)

        # Create or update the DishPlan
        DishPlan.objects.update_or_create(
            user=app_user,
            dish=dish,
            defaults={'plan': category}
        )

        # Determine the redirect URL
        if referrer:
            redirect_url = referrer
        else:
            redirect_url = reverse('home')

        return redirect(redirect_url)

    return HttpResponse('Invalid request', status=400)

@login_required
def homedish(request, dish_id):
    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return HttpResponse('Dish not found', status=404)
    
    # Process the ingredient_list to split it into a list
    ingredients = dish.ingredient_list.split(',')
    
    # Process the procedure to split it into steps
    steps = dish.procedure.split('\n') if dish.procedure else []

    # Retrieve filters from request GET parameters
    meal_type = request.GET.get('meal_type', 'Recommended Dishes')
    budget = request.GET.get('budget', '')

    context = {
        'dish': dish,
        'ingredients': ingredients,  # Add processed ingredients to context
        'steps': steps,  # Add processed steps to context
        'selected_meal_type': meal_type,
        'selected_budget': budget
    }
    return render(request, 'homedish.html', context)



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
            cooked_dish = CookedDish.objects.filter(user=user, dish=dish).first()
            if cooked_dish:
                # Dish already marked as cooked
                return JsonResponse({'success': True, 'cooked': True})

            CookedDish.objects.create(user=user, dish=dish)
            dish_plan.delete()  # Remove from saved dishes
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

    dish_plan = DishPlan.objects.filter(dish=dish, user=user).first()

    ingredients = dish.ingredient_list.split(',') if dish.ingredient_list else []
    procedure_steps = dish.procedure.split('\n') if dish.procedure else []

    return render(request, 'saveddish.html', {
        'dish': dish,
        'dish_plan_id': dish_plan.id if dish_plan else None,
        'ingredients': ingredients,
        'procedure_steps': procedure_steps,
    })





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
            phone = request.POST.get('phone', '')
            if phone.startswith('63'):
                phone = '+' + phone
            else:
                phone = '+63' + phone
            
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
        if code_form.is_valid():
            code = code_form.get_code()  # Use get_code() to get the full code
            phone = request.session.get('phone')
            
            if phone:
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                try:
                    verification_check = client.verify \
                        .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                        .verification_checks \
                        .create(to=phone, code=code)

                    if verification_check.status == 'approved':
                        messages.success(request, 'Verification successful. You can now set a new password.')
                        logger.info('Verification successful, redirecting to forgetnewpass page.')
                        return redirect('forgetnewpass')  # Ensure this matches your URL name
                    else:
                        messages.error(request, 'Invalid verification code. Please try again.')
                except TwilioException as e:
                    messages.error(request, f'An error occurred while verifying the code: {str(e)}')
                except Exception as e:
                    messages.error(request, 'An error occurred during verification. Please try again later.')
            else:
                messages.error(request, 'Phone number not found. Please start the verification process again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        code_form = VerificationCodeForm()

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


def logout(request):
    auth_logout(request)
    return redirect('login')


def resend_otp(request):
    if request.method == 'POST':
        phone_number = request.session.get('phone')
        
        # Debugging output to check session data
        logger.info(f'Resending OTP. Retrieved phone number from session: {phone_number}')
        
        if phone_number:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            try:
                verification = client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID).verifications.create(
                    to=phone_number,
                    channel='sms'
                )
                
                # Check if the verification creation was successful
                if verification.status == 'pending':
                    return JsonResponse({'success': True, 'message': 'Verification code sent again.'})
                else:
                    logger.error(f'Failed to resend verification code. Status: {verification.status}')
                    return JsonResponse({'success': False, 'message': 'Failed to resend verification code.'})
                    
            except Exception as e:
                logger.error(f'Failed to resend verification code: {str(e)}')
                return JsonResponse({'success': False, 'message': 'Failed to resend verification code.'})
        else:
            logger.warning('Phone number not found in session.')
            return JsonResponse({'success': False, 'message': 'Phone number not found. Please start the verification process again.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})








from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash
from .models import ChefAccount, CookedDish, Dish
from .models import Dish, DishPlan
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator
from .forms import DishForm
from django.utils import timezone
import pytz
from .recommendation import RecommendationSystem



from twilio.rest import Client
from twilio.base.exceptions import TwilioException, TwilioRestException

import random
import string
import logging
import time

from .forms import (
    ProfileUpdateForm, SignUpForm, LoginForm, OTPForm,
    PhoneNumberForm, VerificationCodeForm, NewPasswordForm, 
    FamilySizeForm, AgeRangeForm, MealPreferenceForm, AllergiesForm, CookingSkillsForm,
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


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

@login_required
def survey(request):
    user = request.user
    total_steps = 5
    current_step = int(request.session.get('survey_step', 1))

    form_classes = {
        1: FamilySizeForm,
        2: AgeRangeForm,
        3: MealPreferenceForm,
        4: AllergiesForm,
        5: CookingSkillsForm
    }

    print(f"Current Step at the start: {current_step}")  # Debug print

    if request.method == 'POST':
        # Check if the user clicked the "Back" button
        if 'back' in request.POST and current_step > 1:
            # Debug print to track when the "Back" button is clicked
            print(f"Back button clicked on step {current_step}, moving to step {current_step - 1}")
            # Move to the previous step
            request.session['survey_step'] = current_step - 1
            request.session.modified = True  # Ensure session is saved
            print(f"New Step after Back: {request.session['survey_step']}")  # Debug print
            return redirect('survey')

        # Handle the form submission
        form_class = form_classes[current_step]
        form = form_class(request.POST, prefix=f'step_{current_step}')

        if form.is_valid():
            step_data = form.cleaned_data
            app_user, created = AppUser.objects.get_or_create(user=user)

            # Update fields based on the current step
            update_app_user(app_user, step_data, current_step)

            app_user.save()

            if current_step < total_steps:
                # Debug print to track moving to the next step
                print(f"Moving from step {current_step} to step {current_step + 1}")
                # Move to the next step
                request.session['survey_step'] = current_step + 1
                request.session.modified = True  # Ensure session is saved
                print(f"New Step after Next: {request.session['survey_step']}")  # Debug print
                return redirect('survey')
            else:
                # Final step handling
                print("Final step reached, logging out and redirecting to login")
                logout(request)
                return redirect('login')
        else:
            # Debug print to show errors if form is invalid
            print(f"Form invalid at step {current_step}: {form.errors}")
            # Return to the same step with errors
            return render(request, 'survey.html', {
                'form': form,
                'current_step': current_step,
                'total_steps': total_steps,
                'form_errors': form.errors
            })

    else:
        # Handle GET request
        if 'survey_step' not in request.session:
            request.session['survey_step'] = 1

        current_step = request.session.get('survey_step', 1)
        initial_data = get_initial_data(user, current_step)
        form_class = form_classes[current_step]
        form = form_class(initial=initial_data, prefix=f'step_{current_step}')
        print(f"Rendering step {current_step} form")  # Debug print

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
        # Extract the allergies and other_allergies fields
        allergies = step_data.get('allergies', [])
        other_allergies = step_data.get('other_allergies', '').strip()

        # Debugging output to verify the data
        print("Allergies:", allergies)
        print("Other Allergies:", other_allergies)

        # Normalize the allergies data
        normalized_allergies = [a.lower() for a in allergies]

        # Process other_allergies if provided
        if other_allergies:
            # Split the other_allergies string by commas and add to the list
            other_allergies_list = [a.strip().lower() for a in other_allergies.split(',')]
            normalized_allergies.extend(other_allergies_list)

        # Remove duplicates and set the allergies field
        if 'none' in normalized_allergies:
            app_user.allergies = ['None']
        else:
            app_user.allergies = list(set(normalized_allergies))  # Ensure uniqueness

        # Debug print
        print("Processed allergies data before saving:", app_user.allergies)

        # Save the updated allergies to the app_user
        app_user.save()

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







from django.db.models import Avg

@login_required
def check_recipe(request, dish_id):
    app_user = AppUser.objects.get(user=request.user)
    dish = get_object_or_404(Dish, id=dish_id)
    already_saved = DishPlan.objects.filter(user=app_user, dish=dish).exists()
    return JsonResponse({'already_saved': already_saved})

@login_required
def home(request):
    # Retrieve budget and meal type filter values
    min_budget = request.GET.get('min_budget', '')
    max_budget = request.GET.get('max_budget', '')
    meal_type_filter = request.GET.get('meal_type', '')

    print(f"Received filters - Min Budget: {min_budget}, Max Budget: {max_budget}, Meal Type: {meal_type_filter}")

    # Convert meal_type_filter from comma-separated string to a list
    meal_type_filters = meal_type_filter.split(',') if meal_type_filter else []
    print(f"Meal Type Filters: {meal_type_filters}")

    # Get recommendations
    appuser_id = request.user.appuser.id
    recommender = RecommendationSystem(appuser_id)
    recommendations = recommender.get_recommendations()  # Existing logic for recommendations
    
    # Debugging print statements for recommendations
    print("Recommendations:", [dish.dish_name for dish in recommendations])  # Addition from Code 1
    print(f"Number of recommendations: {len(recommendations)}")  # Addition from Code 1

    # Start with recommended dishes that are approved
    dishes = Dish.objects.filter(approved=True, id__in=[dish.id for dish in recommendations]).order_by('dish_name')
    print(f"Initial approved and recommended dishes count: {dishes.count()}")

    # Handle budget filtering
    if min_budget and max_budget:
        try:
            min_budget = int(min_budget)
            max_budget = int(max_budget)
            print(f"Parsed Min Budget: {min_budget}, Max Budget: {max_budget}")
            if min_budget <= max_budget and 100 <= min_budget <= 1000 and 100 <= max_budget <= 1000:
                dishes = dishes.filter(cost__range=(min_budget, max_budget))
                print(f"Filtered dishes count after budget: {dishes.count()}")
            else:
                print("Budget range is invalid.")
        except ValueError:
            print("ValueError encountered during budget filtering. Resetting to initial dishes.")
            dishes = Dish.objects.filter(approved=True, id__in=[dish.id for dish in recommendations]).order_by('dish_name')

    # Apply meal type filters if specified
    if meal_type_filters:
        dishes = dishes.filter(meal_type__name__in=meal_type_filters).distinct()
        print(f"Filtered dishes count after meal type filter: {dishes.count()}")

    # Paginate dishes
    paginator = Paginator(dishes, 9)  # Show 9 dishes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(f"Paginated dishes: Showing page {page_number} with {len(page_obj)} items.")

    # Get top 10 dishes based on average rating from CookedDish
    community_picks = (Dish.objects
                       .filter(approved=True)
                       .annotate(avg_rating=Avg('cookeddish__rating'))
                       .order_by('-avg_rating')[:10])
    
    print(f"Top community picks count: {community_picks.count()}")

    # Create slides containing 2 dishes each
    slides = [community_picks[i:i + 2] for i in range(0, len(community_picks), 2)]

    context = {
        'dishes': page_obj,
        'min_budget': min_budget,
        'max_budget': max_budget,
        'selected_meal_type': meal_type_filter,  # Pass the string of selected meal types
        'page_obj': page_obj,
        'meal_types': Dish.objects.values_list('meal_type__name', flat=True).distinct(),  # Fetch distinct meal types
        'slides': slides,  # Pass the slides to the template
        'recommendations': recommendations,
    }

    return render(request, 'home.html', context)










@login_required
def save_to_saved(request):
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        category = request.POST.get('category')
        saved_date_str = request.POST.get('saved_date')  # Retrieve the saved_date from the POST data

        if not saved_date_str:
            return HttpResponse('Missing date', status=400)

        print(f"Received saved_date: {saved_date_str}")  # Debug print

        # Ensure the date is in the right format and convert to date object
        try:
            # Parse the date in local timezone format (assuming the date is in 'YYYY-MM-DD')
            saved_date = datetime.strptime(saved_date_str, '%Y-%m-%d').date()
            # Use timezone-aware datetime at midnight local time
            local_date = datetime.combine(saved_date, datetime.min.time())
            local_date = timezone.make_aware(local_date, timezone.get_current_timezone())
            # Convert to UTC
            saved_date = local_date.astimezone(pytz.utc)
        except ValueError:
            return HttpResponse('Invalid date format', status=400)

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

        # Create or update the DishPlan with the saved_date
        DishPlan.objects.update_or_create(
            user=app_user,
            dish=dish,
            defaults={'plan': category, 'saved_date': saved_date}
        )

        # Check if filters are present, else redirect to base home URL
        meal_type = request.POST.get('meal_type')
        min_budget = request.POST.get('min_budget')
        max_budget = request.POST.get('max_budget')

        # Construct the redirect URL with valid filters
        redirect_url = reverse('home')
        query_params = []

        if meal_type:
            query_params.append(f"meal_type={meal_type}")
        if min_budget:
            query_params.append(f"min_budget={min_budget}")
        if max_budget:
            query_params.append(f"max_budget={max_budget}")

        if query_params:
            redirect_url += '?' + '&'.join(query_params)

        return HttpResponseRedirect(redirect_url)

    return HttpResponse('Invalid request', status=400)


@login_required
def save_dish(request):
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        category = request.POST.get('category')
        meal_type = request.POST.get('meal_type')
        budget = request.POST.get('budget')
        referrer = request.POST.get('referrer')  # Get referrer URL
        saved_date = request.POST.get('saved_date')  # Get selected date

        # Validate inputs
        if not dish_id or not category or not saved_date:
            return HttpResponse('Invalid input', status=400)

        # Convert the date string to a date object
        try:
            saved_date = datetime.strptime(saved_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse('Invalid date format', status=400)

        # Get the dish object
        dish = get_object_or_404(Dish, id=dish_id)

        # Get the AppUser instance for the current user
        app_user = get_object_or_404(AppUser, user=request.user)

        # Create or update the DishPlan
        DishPlan.objects.update_or_create(
            user=app_user,
            dish=dish,
            defaults={'plan': category, 'saved_date': saved_date}
        )

        # Debug print
        print(f"Dish ID: {dish_id}, Category: {category}, Meal Type: {meal_type}, Budget: {budget}, Saved Date: {saved_date}")

        # Determine the redirect URL
        if referrer:
            redirect_url = referrer
        else:
            redirect_url = reverse('home')

        return redirect(redirect_url)

    return HttpResponse('Invalid request', status=400)

@login_required
def check_if_saved(request, dish_id):
    # Get the AppUser instance for the current user
    try:
        app_user = AppUser.objects.get(user=request.user)
    except AppUser.DoesNotExist:
        return JsonResponse({'isAlreadySaved': False})  # If user not found, treat as not saved

    # Check if the dish is already saved by the current user
    is_saved = DishPlan.objects.filter(dish_id=dish_id, user=app_user).exists()
    return JsonResponse({'isAlreadySaved': is_saved})


from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import json

@login_required
def homedish(request, dish_id):
    try:
        dish = Dish.objects.get(id=dish_id)
    except Dish.DoesNotExist:
        return HttpResponse('Dish not found', status=404)
    
    # Process the ingredient_list as JSON
    ingredients_data = dish.ingredient_list  # This is already a list of dicts
    ingredients = [(item['ingredient'], item['alternatives']) for item in ingredients_data]
    
    # Process the procedure to split it into steps
    steps = dish.procedure.split('\n') if dish.procedure else []

    # Retrieve filters from request GET parameters
    meal_type = request.GET.get('meal_type', 'Recommended Dishes')
    budget = request.GET.get('budget', '')
    selected_date = request.GET.get('selected_date', None)

    # Debug print
    print(f"Selected date: {selected_date}")

    context = {
        'dish': dish,
        'ingredients': ingredients,  # List of tuples (ingredient, alternatives)
        'steps': steps,  # Add processed steps to context
        'selected_meal_type': meal_type,
        'selected_budget': budget,
        'selected_date': selected_date  # Pass selected date to template
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
                
                # Check if the current date is past or matches the saved_date
                if dish_plan.saved_date > timezone.now().date():
                    return JsonResponse({'success': False, 'error': 'Dish cannot be marked as cooked until the saved date is met'}, status=400)

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
        'breakfast': DishPlan.objects.filter(user=app_user, plan='Breakfast').order_by('saved_date'),
        'lunch': DishPlan.objects.filter(user=app_user, plan='Lunch').order_by('saved_date'),
        'dinner': DishPlan.objects.filter(user=app_user, plan='Dinner').order_by('saved_date'),
    }

    logger.debug(f"Saved dishes: {saved_dishes}")  # Logging saved dishes

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
                return JsonResponse({'success': True, 'cooked': True})

            CookedDish.objects.create(user=user, dish=dish)
            dish_plan.delete()
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

    dish_plan = DishPlan.objects.filter(dish=dish, user=user).first()

    ingredients_data = dish.ingredient_list  
    ingredients = [(item['ingredient'], item['alternatives']) for item in ingredients_data]
    procedure_steps = dish.procedure.split('\n') if dish.procedure else []

    # Format saved_date
    saved_date = dish_plan.saved_date.strftime("%b. %d, %Y") if dish_plan else None
    
    # Get the current date
    current_date = timezone.now().strftime("%b. %d, %Y")  # Format current date similarly

    return render(request, 'saveddish.html', {
        'dish': dish,
        'dish_plan_id': dish_plan.id if dish_plan else None,
        'ingredients': ingredients,
        'procedure_steps': procedure_steps,
        'saved_date': saved_date,  # Pass formatted saved date to the template
        'current_date': current_date,  # Pass the current date to the template
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
                cooked_dish.feedback_time = timezone.now()  # Set the feedback time
                cooked_dish.save()
                return JsonResponse({'success': True})
            except CookedDish.DoesNotExist:
                return JsonResponse({'error': 'CookedDish not found'}, status=404)

    try:
        app_user = AppUser.objects.get(user=request.user)
    except AppUser.DoesNotExist:
        return HttpResponse('AppUser not found', status=404)

    # Fetch the cooked dishes for the current user
    cooked_dishes = CookedDish.objects.filter(user=app_user)
    
    # Ensure 'cooked' field is automatically set to True for each dish
    for dish in cooked_dishes:
        if not dish.cooked:  # Only update if not already set to True
            dish.cooked = True
            dish.save()

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


def addrecipe(request):
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # or another success page
        else:
            return render(request, 'addrecipe.html', {'form': form})
    else:
        form = DishForm()
    return render(request, 'addrecipe.html', {'form': form})



def chefhome(request):
    if not request.session.get('chef_id'):
        return redirect('cheflogin')

    chef = ChefAccount.objects.get(id=request.session['chef_id'])
    # Fetch non-approved dishes
    non_approved_dishes = Dish.objects.filter(approved=False)
    
    return render(request, 'chefhome.html', {'chef': chef, 'non_approved_dishes': non_approved_dishes})



def cheflogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            chef = ChefAccount.objects.get(username=username)

            if chef.password == password:  # Simple password check
                request.session['chef_id'] = chef.id  # Store chef ID in session
                return redirect('chefhome')  # Redirect to chef home page
            else:
                messages.error(request, 'Invalid password. Please try again.')
        
        except ChefAccount.DoesNotExist:
            messages.error(request, 'Account does not exist. Please try again.')

    return render(request, 'cheflogin.html')


def dish_detail(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    if request.method == "POST":
        form = DishForm(request.POST, request.FILES, instance=dish)
        if form.is_valid():
            form.save()
            return redirect('chefhome')
    else:
        # Convert preparation_time from timedelta if necessary
        initial_data = {}
        if dish.preparation_time:
            # Example conversion if preparation_time is stored as timedelta
            initial_data['preparation_time'] = convert_timedelta_to_str(dish.preparation_time)

        form = DishForm(instance=dish, initial=initial_data)

    # Prepare ingredients data to pass to the template
    ingredients_data = dish.ingredient_list if dish.ingredient_list else []

    return render(request, 'dish_detail.html', {
        'form': form,
        'ingredients_data': ingredients_data
    })


def convert_timedelta_to_str(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def approve_dish(request, dish_id):
    if request.method == "POST":
        dish = get_object_or_404(Dish, id=dish_id)
        dish.approved = True
        dish.save()
        return redirect('chefhome')
    else:
        return HttpResponseNotFound("Invalid request")
    
def delete_dish(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    dish.delete()
    return redirect('chefhome')





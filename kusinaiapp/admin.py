from django.contrib import admin
from .models import AppUser, Dish, DishPlan, CookedDish
from django import forms
import datetime

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'name', 'phone_number', 'family_size',  'cooking_skills', 'formatted_age_range', 'formatted_meal_preference', 'formatted_allergies')
    search_fields = ('username', 'name', 'phone_number')
    
    def formatted_age_range(self, obj):
        return ', '.join(obj.age_range) if obj.age_range else 'N/A'
    formatted_age_range.short_description = 'Age Range'

    def formatted_meal_preference(self, obj):
        return ', '.join(obj.meal_preference) if obj.meal_preference else 'N/A'
    formatted_meal_preference.short_description = 'Meal Preference'

    def formatted_allergies(self, obj):
        return ', '.join(obj.allergies) if obj.allergies else 'N/A'
    formatted_allergies.short_description = 'Allergies'

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('id', 'dish_name', 'preparation_time', 'meal_type', 'number_of_servings', 'cost')
    search_fields = ('dish_name', 'ingredient_list', 'skills_needed')
    list_filter = ('skills_needed', 'cost', 'meal_type')  # Add meal_type to the filters if needed




@admin.register(DishPlan)
class DishPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish', 'plan')
    search_fields = ('user__username', 'dish__dish_name', 'plan')
    
@admin.register(CookedDish)
class CookedDishAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish', 'rating', 'cooked_date')  # Include 'rating' here
    list_filter = ('user', 'cooked_date', 'rating')  # Optionally filter by rating
    search_fields = ('user__username', 'dish__name')
    ordering = ('-cooked_date',)
    


class DishAdminForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = '__all__'

    def clean_preparation_time(self):
        value = self.cleaned_data.get('preparation_time')
        if isinstance(value, str):
            # Convert the string to timedelta
            try:
                hours, minutes = map(int, value.split(':'))
                return datetime.timedelta(hours=hours, minutes=minutes)
            except ValueError:
                raise forms.ValidationError("Invalid duration format. Use HH:MM format.")
        return value
from django.contrib import admin
from .models import AppUser, Dish, DishPlan, CookedDish
from django import forms
import datetime
from django_select2.forms import Select2MultipleWidget
from django.db import models

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('appuser_id', 'user_id', 'username', 'name', 'phone_number', 'family_size', 'cooking_skills', 'formatted_age_range', 'formatted_meal_preference', 'formatted_allergies')
    search_fields = ('username', 'name', 'phone_number')

    def appuser_id(self, obj):
        return obj.id
    appuser_id.short_description = 'APPUSER_ID'

    def user_id(self, obj):
        return obj.user.id
    user_id.short_description = 'USER_ID'

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
    list_display = ('dish_id', 'dish_name', 'preparation_time', 'get_meal_types', 'number_of_servings', 'cost', 'approved')
    search_fields = ('dish_name', 'ingredient_list', 'skills_needed')
    list_filter = ('skills_needed', 'cost', 'meal_type', 'approved')

    formfield_overrides = {
        models.ManyToManyField: {'widget': Select2MultipleWidget},
    }

    def dish_id(self, obj):
        return obj.id
    dish_id.short_description = 'DISH_ID'

    def get_meal_types(self, obj):
        return ", ".join([meal_type.name for meal_type in obj.meal_type.all()])

    get_meal_types.short_description = 'Meal Types'

@admin.register(DishPlan)
class DishPlanAdmin(admin.ModelAdmin):
    list_display = ('dishplan_id', 'appuser_id', 'dish', 'plan')
    search_fields = ('user__username', 'dish__dish_name', 'plan')

    def dishplan_id(self, obj):
        return obj.id
    dishplan_id.short_description = 'DISHPLAN_ID'

    def appuser_id(self, obj):
        return obj.user.id  # Changed to use AppUser ID
    appuser_id.short_description = 'APPUSER_ID'

@admin.register(CookedDish)
class CookedDishAdmin(admin.ModelAdmin):
    list_display = ('cooked_id', 'appuser_id', 'dish', 'rating', 'cooked_date')
    list_filter = ('user', 'cooked_date', 'rating')
    search_fields = ('user__username', 'dish__dish_name')
    ordering = ('-cooked_date',)

    def cooked_id(self, obj):
        return obj.id
    cooked_id.short_description = 'COOKED_ID'

    def appuser_id(self, obj):
        return obj.user.id  # Changed to use AppUser ID
    appuser_id.short_description = 'APPUSER_ID'

class DishAdminForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = '__all__'

    def clean_preparation_time(self):
        value = self.cleaned_data.get('preparation_time')
        if isinstance(value, str):
            try:
                hours, minutes = map(int, value.split(':'))
                return datetime.timedelta(hours=hours, minutes=minutes)
            except ValueError:
                raise forms.ValidationError("Invalid duration format. Use HH:MM format.")
        return value

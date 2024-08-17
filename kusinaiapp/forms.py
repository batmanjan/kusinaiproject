from django import forms
from django.contrib.auth.models import User
from .models import AppUser
from django.core.validators import RegexValidator

class SignUpForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your name'}),
        help_text='Enter your full name.'
    )
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}),
        help_text='Choose a unique username.'
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'id': 'phone', 'placeholder': 'Enter your phone number'}),
        help_text='Enter your phone number for verification.'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        help_text='Password must be at least 8 characters long.'
    )
    repassword = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),
        help_text='Re-enter your password for confirmation.'
    )

    def clean_repassword(self):
        password = self.cleaned_data.get('password')
        repassword = self.cleaned_data.get('repassword')
        if password and repassword and password != repassword:
            raise forms.ValidationError("Passwords do not match.")
        return repassword

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        help_text='Enter your username.'
    )
    password = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        help_text='Enter your password.'
    )
    
class OTPForm(forms.Form):
    otp_1 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(attrs={'placeholder': '', 'maxlength': '1'}),
        required=True,
        validators=[RegexValidator(r'^\d$', 'Enter a single digit.')]
    )
    otp_2 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(attrs={'placeholder': '', 'maxlength': '1'}),
        required=True,
        validators=[RegexValidator(r'^\d$', 'Enter a single digit.')]
    )
    otp_3 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(attrs={'placeholder': '', 'maxlength': '1'}),
        required=True,
        validators=[RegexValidator(r'^\d$', 'Enter a single digit.')]
    )
    otp_4 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(attrs={'placeholder': '', 'maxlength': '1'}),
        required=True,
        validators=[RegexValidator(r'^\d$', 'Enter a single digit.')]
    )

    def clean(self):
        cleaned_data = super().clean()
        otp_1 = cleaned_data.get("otp_1")
        otp_2 = cleaned_data.get("otp_2")
        otp_3 = cleaned_data.get("otp_3")
        otp_4 = cleaned_data.get("otp_4")

        if not (otp_1 and otp_2 and otp_3 and otp_4):
            raise forms.ValidationError("All digits are required.")
        
        return cleaned_data

    def get_otp(self):
        return ''.join([self.cleaned_data.get("otp_1", ""), 
                        self.cleaned_data.get("otp_2", ""), 
                        self.cleaned_data.get("otp_3", ""), 
                        self.cleaned_data.get("otp_4", "")])

    
class PhoneNumberForm(forms.Form):
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
        help_text='Enter your phone number to receive a verification code.'
    )



class VerificationCodeForm(forms.Form):
    code_1 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(attrs={'placeholder': '', 'maxlength': '1'}),
        required=True,
        validators=[RegexValidator(r'^\d$', 'Enter a single digit.')]
    )
    code_2 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(attrs={'placeholder': '', 'maxlength': '1'}),
        required=True,
        validators=[RegexValidator(r'^\d$', 'Enter a single digit.')]
    )
    code_3 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(attrs={'placeholder': '', 'maxlength': '1'}),
        required=True,
        validators=[RegexValidator(r'^\d$', 'Enter a single digit.')]
    )
    code_4 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(attrs={'placeholder': '', 'maxlength': '1'}),
        required=True,
        validators=[RegexValidator(r'^\d$', 'Enter a single digit.')]
    )

    def clean(self):
        cleaned_data = super().clean()
        code_1 = cleaned_data.get("code_1")
        code_2 = cleaned_data.get("code_2")
        code_3 = cleaned_data.get("code_3")
        code_4 = cleaned_data.get("code_4")

        if not (code_1 and code_2 and code_3 and code_4):
            raise forms.ValidationError("All digits are required.")
        
        return cleaned_data

    def get_code(self):
        return ''.join([self.cleaned_data.get("code_1", ""), 
                        self.cleaned_data.get("code_2", ""), 
                        self.cleaned_data.get("code_3", ""), 
                        self.cleaned_data.get("code_4", "")])


class NewPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}),
        help_text='Enter a new password for your account.'
    )
    re_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter new password'}),
        help_text='Re-enter the new password for confirmation.'
    )

    def clean_re_password(self):
        new_password = self.cleaned_data.get('new_password')
        re_password = self.cleaned_data.get('re_password')
        if new_password and re_password and new_password != re_password:
            raise forms.ValidationError("Passwords do not match.")
        return re_password
    
class FamilySizeForm(forms.Form):
    family_size = forms.ChoiceField(
        choices=[
            ('2-3 Members', '2-3 Members'),
            ('4-5 Members', '4-5 Members'),
        ],
        widget=forms.RadioSelect,
        required=False
    )

class AgeRangeForm(forms.Form):
    age_range = forms.MultipleChoiceField(
        choices=[
            ('kids', 'Kids (2-3yrs old)'),
            ('teens', 'Teens (13-18)'),
            ('adults', 'Adults (19-59)'),
            ('elderly', 'Elderly (60+)')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

class MealPreferenceForm(forms.Form):
    meal_preference = forms.MultipleChoiceField(
        choices=[
            ('appetizer', 'Appetizer'),
            ('soup', 'Soup'),
            ('dessert', 'Dessert'),
            ('vegetable_dish', 'Vegetable Dish'),
            ('vegetable_seafood', 'Vegetable with Seafood'),
            ('vegetable_meat', 'Vegetable with Meat')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

class AllergiesForm(forms.Form):
    allergies = forms.MultipleChoiceField(
        choices=[
            ('milk', 'Milk'),
            ('eggs', 'Eggs'),
            ('seafood', 'Seafood'),
            ('wheat', 'Wheat'),
            ('peanuts', 'Peanuts'),
            ('soybeans', 'Soybeans'),
            ('none', 'None')  # Ensure 'none' is in lowercase
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    other_allergies = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Put other allergies here, if you have 2 or more, separate each with a comma'}),
        required=False
    )

class CookingSkillsForm(forms.Form):
    cooking_skills = forms.ChoiceField(
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        widget=forms.RadioSelect,
        required=False
    )
    
class ProfileUpdateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your new password (leave blank to keep current)'}),
        required=False,
        help_text='Leave blank to keep the current password.'
    )
    repassword = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your new password'}),
        required=False,
        help_text='Re-enter your new password for confirmation.'
    )

    class Meta:
        model = AppUser
        fields = ['name', 'username', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Valid PH number'}),
        }

    def __init__(self, *args, **kwargs):
        # Initialize the form with any existing data
        super().__init__(*args, **kwargs)
        
        # If the form has initial data for the phone_number field, remove the prefix for display
        if self.initial and 'phone_number' in self.initial:
            self.initial['phone_number'] = self.remove_prefix(self.initial['phone_number'])

    def remove_prefix(self, phone_number):
        # Remove +63 prefix if present
        if phone_number.startswith('+63'):
            return phone_number[3:]  # Remove the +63 prefix
        return phone_number

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '')
        if not phone_number.startswith('+63'):
            phone_number = '+63' + phone_number.lstrip('0')  # Add prefix and remove leading zero if present
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        repassword = cleaned_data.get("repassword")

        if password and repassword and password != repassword:
            self.add_error('repassword', 'Passwords do not match.')

        return cleaned_data

from django import forms

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
        widget=forms.TextInput(attrs={'placeholder': 'Valid PH number'}),
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
    otp = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter OTP'}),
        help_text='Enter the OTP sent to your phone.'
    )

    
class PhoneNumberForm(forms.Form):
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
        help_text='Enter your phone number to receive a verification code.'
    )



class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the code'}),
        help_text='Enter the verification code sent to your phone.'
    )

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
    
class SurveyForm(forms.Form):
    family_size = forms.ChoiceField(
        choices=[
            ('2-3 Members', '2-3 Members'),
            ('4-5 Members', '4-5 Members'),
        ],
        widget=forms.RadioSelect,
        required=True
    )
    
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

    allergies = forms.MultipleChoiceField(
        choices=[
            ('milk', 'Milk'),
            ('eggs', 'Eggs'),
            ('seafood', 'Seafood'),
            ('wheat', 'Wheat'),
            ('peanuts', 'Peanuts'),
            ('soybeans', 'Soybeans'),
            ('none', 'None')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    other_allergies = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Put other allergies here, if you have 2 or more, separate each with a comma'}),
        required=False
    )
    
    cooking_skills = forms.ChoiceField(
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        widget=forms.RadioSelect,
        required=False
    )

from django import forms
from .models import *
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        fields = '__all__'
        widgets = {
            'facebook': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Facebook username'}),
            'instgram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instagram username'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'MTNAccount': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MTN account number'}),
            'SyriaAccount': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Syriatel account number'}),
            'maxDelKM': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Maximum delivery distance (KM)'}),
            'priceforKM': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price per KM'}),
        }

class ActiveIngredientForm(forms.ModelForm):
    class Meta:
        model = ActiveIngredient
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ingredient name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        }        

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = '__all__'

from django.contrib.auth import get_user_model

User = get_user_model()
class PrescriptionForm(forms.ModelForm):
    patient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Patient"
    )

    class Meta:
        model = Prescription
        fields = ['patient', 'uploaded_file', 'note']
        widgets = {
            'uploaded_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

        }



class CustomerAddressForm(forms.ModelForm):
    class Meta:
        model = CustomerAddress
        fields = ['label', 'address_line', 'city', 'postal_code', 'phone', 'is_default']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }        
from django import forms
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import User
from .models import Order

class OrderEditForm(forms.ModelForm):
    # user = forms.ModelChoiceField(
    #     queryset=User.objects.all(),
    #     required=True,
    #     widget=forms.Select(attrs={'class': 'form-control'}),
    #     empty_label="Select a user"
    # )
    
    class Meta:
        model = Order
        fields = [
         
            'prescription', 
            'address', 
            'scheduled_for',
            'status', 
            'payment_delivery', 
            'payment_reference', 
            'notes',
            'his_driver'  # أضف هذا إذا كنت تريد تعديله
        ]
        widgets = {
            'scheduled_for': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'payment_reference': forms.TextInput(attrs={'class': 'form-control'}),
            'prescription': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'address': forms.Select(attrs={'class': 'form-control'}),
            'payment_delivery': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'his_driver': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تنسيق قيمة scheduled_for للعرض
        if self.instance and self.instance.scheduled_for:
            # تحويل إلى توقيت محلي للعرض
            dt = self.instance.scheduled_for
            if timezone.is_aware(dt):
                dt = timezone.localtime(dt)
            self.initial['scheduled_for'] = dt.strftime('%Y-%m-%dT%H:%M')
        else:
            # تعيين قيمة افتراضية إذا لم تكن موجودة
            self.initial['scheduled_for'] = ''
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['medicine', 'quantity']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            # 'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medicine'].queryset = Medicine.objects.all()  # To limit medicines to the available ones        

from django.contrib.auth.forms import UserCreationForm
from User.models import *
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # ✅ اجبار المستخدم يكتب ايميل

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password1', 'password2', 'is_verified']  

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']   # ✅ احفظ الايميل
        if commit:
            user.save()
        return user



# forms.py
from django import forms
from django.contrib.auth import authenticate

class UserLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError("Invalid username or password")
            elif not self.user.is_verified:
                raise forms.ValidationError("Please verify your email address before logging in.")
        
        return cleaned_data

from django import forms
from .models import BatchMed

class BatchMedForm(forms.ModelForm):
    class Meta:
        model = BatchMed
        fields = ['medicine', 'batch_number', 'quantity', 'expiration_date', 'purchase_price']
        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'purchase_price': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError("الكمية لا يمكن أن تكون سالبة")
        return quantity
    
    def clean_expiration_date(self):
        expiration_date = self.cleaned_data.get('expiration_date')
        if expiration_date and expiration_date < timezone.now().date():
            raise forms.ValidationError("لا يمكن إضافة دفعة منتهية الصلاحية")
        return expiration_date
    

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [ 'first_name', 'last_name', 'username', 'email','photo','birthy_day']
        widgets = {
                'birthy_day': forms.DateInput(attrs={'type': 'date'})  # Fixed field name
        }

# forms.py
from django import forms
from .models import CustomerAddress

class AddressForm(forms.ModelForm):
    loction_Des = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'background-color: #0e69ca68; color: white;',
            'placeholder': 'Enter location description'
        })
    )
    loction_x = forms.FloatField(
        required=True,
        widget=forms.HiddenInput(attrs={
            'class': 'form-control',
            'style': 'background-color: #0e69ca68; color: white;'
        })
    )
    loction_y = forms.FloatField(
        required=True,
        widget=forms.HiddenInput(attrs={
            'class': 'form-control', 
            'style': 'background-color: #0e69ca68; color: white;'
        })
    )
    
    class Meta:
        model = CustomerAddress
        fields = ['label', 'address_line', 'city', 'postal_code', 'phone', 'is_default']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Home, Work, etc.'}),
            'address_line': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing address, populate the custom fields
        if self.instance and self.instance.pk:
            self.fields['loction_Des'].initial = self.instance.label or f"Location in {self.instance.city}"
            self.fields['loction_x'].initial = self.instance.x
            self.fields['loction_y'].initial = self.instance.y
    
    def save(self, commit=True):
        # Map the custom fields to the model fields
        instance = super().save(commit=False)
        instance.x = self.cleaned_data.get('loction_x', 0.0)
        instance.y = self.cleaned_data.get('loction_y', 0.0)
        
        # You can also use loction_Des as the label if needed
        if not instance.label and self.cleaned_data.get('loction_Des'):
            instance.label = self.cleaned_data['loction_Des']
        
        if commit:
            instance.save()
        return instance

# Forms
class PrescriptionFormCus(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['uploaded_file', 'note']


class AddMoneyForm(forms.ModelForm):
    class Meta:
        model = OpertionMoney
        fields = ['type', 'Amount', 'code', 'image']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'Amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '0.01', 
                'step': '0.01',
                'placeholder': 'Enter amount to add'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Transaction code (optional)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
            })
        }
    
    def clean_Amount(self):
        amount = self.cleaned_data.get('Amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

class WithdrawMoneyForm(forms.ModelForm):
    class Meta:
        model = OpertionMoney
        fields = ['type', 'Amount', 'Account']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'Amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '0.01', 
                'step': '0.01',
                'placeholder': 'Enter amount to withdraw'
            }),
            'Account': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Transaction code (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.wallet = kwargs.pop('wallet', None)
        super().__init__(*args, **kwargs)
        # self.fields['Method'].initial = 'Withdraw'
        # self.fields['Method'].widget = forms.HiddenInput()
    
    def clean_Amount(self):
        amount = self.cleaned_data.get('Amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        
        if self.wallet and amount > self.wallet.Amount:
            raise forms.ValidationError("Insufficient balance for withdrawal.")
        
        return amount
    

class DriverUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2','birthy_day']

class DriverForm(forms.ModelForm):
    class Meta:
        model = driver
        fields = ['current_x', 'current_y','vehicle_type','license_plate']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_x'].widget.attrs.update({'placeholder': 'e.g., 36.2021'})
        self.fields['current_y'].widget.attrs.update({'placeholder': 'e.g., 37.1343'})

class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'his_driver', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'his_driver': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available drivers (those not assigned to active deliveries)
        self.fields['his_driver'].queryset = driver.objects.all()
        self.fields['his_driver'].required = False

# forms.py
from django.contrib.auth.forms import AuthenticationForm
class DriverLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )        

# forms.py
from django import forms
from django.core.validators import EmailValidator

class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control'
        }),
        validators=[EmailValidator()]
    )

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit OTP',
            'class': 'form-control',
            'maxlength': '6'
        })
    )

class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter new password',
            'class': 'form-control'
        }),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password',
            'class': 'form-control'
        }),
        min_length=8
    )
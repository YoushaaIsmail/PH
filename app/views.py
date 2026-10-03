from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
# Create your views here.
from django.db import transaction
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from User.models import *
from .models import *
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta, time
from django.utils import timezone
# from .emails import *
from django.contrib.auth import logout
# from transformers import AutoProcessor, AutoModelForImageClassification
from PIL import Image
import torch
# Add these imports at the top of your views.py file
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Comment, Medicine
from .serializers import CommentSerializer
import json
from datetime import datetime, timedelta, time
from collections import defaultdict
from collections import defaultdict

from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, redirect
from django.contrib import messages 
@login_required
def category_list(request):
    query = request.GET.get('q', '')
    categories = Category.objects.all()
    if query:
        categories = categories.filter(name__icontains=query)

    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'category/list.html', {
        'categories': page_obj,
        'page_obj': page_obj,
    })


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('app:category_list')
    return render(request, 'category/form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('app:category_list')
    return render(request, 'category/form.html', {'form': form, 'title': 'Edit Category'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('app:category_list')
    return render(request, 'category/confirm_delete.html', {'category': category})



@login_required
def driver_list(request):
    query = request.GET.get('q', '')
    drivers_list = driver.objects.all()
    
    if query:
        drivers_list = drivers_list.filter(
            user__first_name__icontains=query
        ) | drivers_list.filter(
            user__last_name__icontains=query
        ) | drivers_list.filter(
            user__username__icontains=query
        )

    paginator = Paginator(drivers_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'driver/list.html', {
        'drivers': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


@login_required
@transaction.atomic
def driver_create(request):
    if request.method == 'POST':
        user_form = DriverUserCreationForm(request.POST)
        driver_form = DriverForm(request.POST)
        
        if user_form.is_valid() and driver_form.is_valid():
            # Create the user first
            user = user_form.save(commit=False)
            user.email = user_form.cleaned_data['email']
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']
            user.save()
            
            # Create the driver profile
            driver_profile = driver_form.save(commit=False)
            driver_profile.user = user
            driver_profile.save()
            
            messages.success(request, f'Driver {user.get_full_name()} created successfully!')
            return redirect('app:driver_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = DriverUserCreationForm()
        driver_form = DriverForm()

    return render(request, 'driver/form.html', {
        'user_form': user_form,
        'driver_form': driver_form,
        'title': 'Add Driver'
    })


@login_required
def driver_edit(request, pk):
    driver_profile = get_object_or_404(driver, pk=pk)
    
    if request.method == 'POST':
        user_form = DriverUserCreationForm(request.POST, instance=driver_profile.user)
        driver_form = DriverForm(request.POST, instance=driver_profile)
        
        # Remove password requirements for editing
        user_form.fields['password1'].required = False
        user_form.fields['password2'].required = False
        
        if user_form.is_valid() and driver_form.is_valid():
            user = user_form.save(commit=False)
            # Only update password if provided
            password = user_form.cleaned_data.get('password1')
            if password:
                user.set_password(password)
            user.save()
            
            driver_form.save()
            
            messages.success(request, f'Driver {user.get_full_name()} updated successfully!')
            return redirect('app:driver_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = DriverUserCreationForm(instance=driver_profile.user)
        driver_form = DriverForm(instance=driver_profile)
        
        # Remove password requirements for editing
        user_form.fields['password1'].required = False
        user_form.fields['password2'].required = False

    return render(request, 'driver/form.html', {
        'user_form': user_form,
        'driver_form': driver_form,
        'title': 'Edit Driver',
        'is_edit': True
    })


@login_required
@transaction.atomic
def driver_delete(request, pk):
    driver_profile = get_object_or_404(driver, pk=pk)
    user = driver_profile.user
    
    if request.method == 'POST':
        driver_profile.delete()
        user.delete()
        messages.success(request, f'Driver {user.get_full_name()} deleted successfully!')
        return redirect('app:driver_list')
    
    return render(request, 'driver/confirm_delete.html', {'driver': driver_profile})



@login_required
def ingredient_list(request):
    query = request.GET.get('q', '')
    ingredients = ActiveIngredient.objects.all()
    if query:
        ingredients = ingredients.filter(name__icontains=query)
    
    paginator = Paginator(ingredients, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'ingredients/list.html', {
        'ingredients': page_obj,
        'page_obj': page_obj,
    })

@login_required
def ingredient_create(request):
    form = ActiveIngredientForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('app:ingredient_list')
    return render(request, 'ingredients/form.html', {'form': form, 'title': 'Add Ingredient'})

@login_required
def ingredient_edit(request, pk):
    ingredient = get_object_or_404(ActiveIngredient, pk=pk)
    form = ActiveIngredientForm(request.POST or None, instance=ingredient)
    if form.is_valid():
        form.save()
        return redirect('app:ingredient_list')
    return render(request, 'ingredients/form.html', {'form': form, 'title': 'Edit Ingredient'})

@login_required
def ingredient_delete(request, pk):
    ingredient = get_object_or_404(ActiveIngredient, pk=pk)
    if request.method == 'POST':
        ingredient.delete()
        return redirect('app:ingredient_list')
    return render(request, 'ingredients/confirm_delete.html', {'ingredient': ingredient})

from django.db.models import Q
@login_required
def medicine_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    ingredient_id = request.GET.get('ingredient', '')

    medicines = Medicine.objects.all()

    # فلترة حسب النص
    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query) | 
            Q(active_ingredients__name__icontains=query)
        ).distinct()

    # فلترة حسب الفئة
    if category_id:
        medicines = medicines.filter(category_id=category_id)

    # فلترة حسب المادة الفعالة
    if ingredient_id:
        medicines = medicines.filter(active_ingredients__id=ingredient_id)

    categories = Category.objects.all()
    ingredients = ActiveIngredient.objects.all()

    return render(request, 'medicines/list.html', {
        'medicines': medicines,
        'categories': categories,
        'ingredients': ingredients,
        'selected_category': category_id,
        'selected_ingredient': ingredient_id,
        'query': query,
    })

# =============================
# ➕ Create medicine
# =============================
@login_required
def medicine_create(request):
    form = MedicineForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('app:medicine_list')
    return render(request, 'medicines/form.html', {
        'form': form,
        'title': 'Add Medicine'
    })

# =============================
# ✏️ Edit medicine
# =============================
@login_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, request.FILES or None, instance=medicine)
    if form.is_valid():
        form.save()
        return redirect('app:medicine_list')
    return render(request, 'medicines/form.html', {
        'form': form,
        'title': 'Edit Medicine'
    })

# =============================
# ❌ Delete medicine
# =============================
@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        return redirect('app:medicine_list')
    return render(request, 'medicines/confirm_delete.html', {
        'medicine': medicine
    })


@login_required
def prescription_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    prescriptions = Prescription.objects.all()

    # فلترة حسب المستخدم (المرضى يرون فقط وصفاتهم)
    if not request.user.is_staff:
        prescriptions = prescriptions.filter(patient=request.user)

    # فلترة حسب النص (البحث)
    if query:
        prescriptions = prescriptions.filter(
            Q(note__icontains=query) |
            Q(patient__username__icontains=query)
        ).distinct()

    # فلترة حسب الحالة
    if status_filter:
        prescriptions = prescriptions.filter(status=status_filter)

    return render(request, 'prescriptions/list.html', {
        'prescriptions': prescriptions,
        'query': query,
        'status_filter': status_filter,
    })

# =============================
# ➕ Create Prescription
# =============================
@login_required
def prescription_create(request):
    form = PrescriptionForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        prescription = form.save(commit=False)
        prescription.save()
        return redirect('app:prescription_list')

    return render(request, 'prescriptions/form.html', {
        'form': form,
        'title': 'Upload Prescription'
    })

# =============================
# ✏️ Edit Prescription
# =============================
@login_required
def prescription_edit(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)

    # فقط الطبيب أو الأدمن يمكنهم التعديل
    if not request.user.is_staff and prescription.patient != request.user:
        return redirect('app:prescription_list')

    form = PrescriptionForm(request.POST or None, request.FILES or None, instance=prescription)
    if form.is_valid():
        form.save()
        return redirect('app:prescription_list')

    return render(request, 'prescriptions/form.html', {
        'form': form,
        'title': 'Edit Prescription'
    })

# =============================
# ❌ Delete Prescription
# =============================
@login_required
def prescription_delete(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)

    if not request.user.is_staff and prescription.patient != request.user:
        return redirect('app:prescription_list')

    if request.method == 'POST':
        prescription.delete()
        return redirect('app:prescription_list')

    return render(request, 'prescriptions/confirm_delete.html', {
        'prescription': prescription
    })

@login_required
def address_list(request):
    addresses = CustomerAddress.objects.all()
    return render(request, 'addresses/list.html', {
        'addresses': addresses,
    })

# =============================
# ➕ Create Customer Address
# =============================
@login_required
def address_create(request):
    form = CustomerAddressForm(request.POST or None)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        if address.is_default:
            # If setting new address as default, unset previous defaults
            CustomerAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address.save()
        return redirect('app:address_list')
    return render(request, 'addresses/form.html', {
        'form': form,
        'title': 'Add Address'
    })

# =============================
# ✏️ Edit Customer Address
# =============================
@login_required
def address_edit(request, pk):
    address = get_object_or_404(CustomerAddress, pk=pk)
    form = CustomerAddressForm(request.POST or None, instance=address)
    if form.is_valid():
        address = form.save(commit=False)
        if address.is_default:
            # If setting this address as default, unset others
            CustomerAddress.objects.filter(user=request.user, is_default=True).exclude(pk=pk).update(is_default=False)
        address.save()
        return redirect('app:address_list')
    return render(request, 'addresses/form.html', {
        'form': form,
        'title': 'Edit Address'
    })

# =============================
# ❌ Delete Customer Address
# =============================
@login_required
def address_delete(request, pk):
    address = get_object_or_404(CustomerAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('app:address_list')
    return render(request, 'addresses/confirm_delete.html', {
        'address': address
    })



def order_listA(request):
    search_query = request.GET.get('search', '')  # Get the search query from the request GET parameters
    orders = Order.objects.all()  # Get orders for the current user
    
    # If there is a search query, filter orders by the user's name
    if search_query:
        orders = orders.filter(user__username__icontains=search_query)  # Filter orders based on username (case-insensitive)

    return render(request, 'orders/list.html', {'orders': orders, 'search_query': search_query})


@login_required
def order_create(request):
    form = OrderForm(request.POST or None)
    if form.is_valid():
        order = form.save()  # user comes from the form
        return redirect('app:order_listA')
    
    return render(request, 'form.html', {'form': form, 'title': 'Create Order'})

# @login_required
# def order_editA(request, pk):
#     # Allow staff to edit any order, regular users only their own
#     if request.user.is_staff:
#         order = get_object_or_404(Order, pk=pk)
#     else:
#         order = get_object_or_404(Order, pk=pk, user=request.user)
    
#     if request.method == 'POST':
#         # Handle scheduled_for separately if needed, or use the form
#         form = OrderForm(request.POST, instance=order)
        
#         if form.is_valid():
#             # Check if scheduled_for was changed
#             scheduled_str = request.POST.get('scheduled_for', '').strip()
            
#             try:
#                 if scheduled_str:
#                     # Parse the datetime
#                     scheduled_for = datetime.strptime(scheduled_str, '%Y-%m-%dT%H:%M')
                    
#                     # Make timezone aware if needed
#                     if timezone.is_naive(scheduled_for):
#                         scheduled_for = timezone.make_aware(scheduled_for)
                    
#                     # Update the scheduled_for field
#                     order.scheduled_for = scheduled_for
#                 else:
#                     # Clear the scheduled date if empty
#                     order.scheduled_for = None
                
#                 # Save the form and order
#                 form.save()
                
#                 messages.success(request, f'Order #{order.id} has been updated successfully!')
#                 if 'scheduled_for' in form.changed_data:
#                     messages.info(request, f'Ready date updated')
                
#                 return redirect('app:order_listA')
                
#             except ValueError as e:
#                 messages.error(request, f'Invalid date format: {e}')
#                 # Continue with form validation
#         else:
#             messages.error(request, 'Please correct the errors below.')
    
#     else:
#         form = OrderForm(instance=order)
    
#     # Format the scheduled_for value for datetime-local input
#     scheduled_value = ''
#     if order.scheduled_for:
#         # Convert to format for datetime-local input: YYYY-MM-DDTHH:MM
#         scheduled_value = order.scheduled_for.strftime('%Y-%m-%dT%H:%M')
    
#     context = {
#         'form': form,
#         'order': order,
#         'title': f'Edit Order #{order.id}',
#         'scheduled_value': scheduled_value,  # Pass to template
#     }
#     return render(request, 'orders/form.html', context)
@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == 'POST':
        order.delete()
        return redirect('app:order_listA')
    return render(request, 'orders/confirm_delete.html', {'order': order})

@login_required
def order_item_edit(request, order_id, item_id):
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, id=item_id, order=order)

    if order.user != request.user and not request.user.is_staff:
        return redirect('app:order_list')  # Redirect if unauthorized
    if order.status !="draft":
        messages.error(request, "Can't Edite order.")
        return redirect('app:order_listA')
    if request.method == 'POST':
        form = OrderItemForm(request.POST, instance=order_item)
        if form.is_valid():
            form.save()
            return redirect('app:order_item_list', order_id=order.id)
    else:
        form = OrderItemForm(instance=order_item)

    return render(request, 'order_items/form.html', {
        'form': form,
        'order': order,
        'order_item': order_item,
        'title': 'Edit Order Item'
    })

@login_required
def order_item_create(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user and not request.user.is_staff:
        return redirect('app:order_listA')  # Redirect to the order list if unauthorized
    if order.status !="draft":
        messages.error(request, "Can't Edite order.")
        return redirect('app:order_listA')  # Redirect to the order list if unauthorized

    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            # Create and save the new order item
            order_item = form.save(commit=False)
            order_item.order = order  # Link the order
            order_item.save()
            return redirect('app:order_item_list', order_id=order.id)
    else:
        form = OrderItemForm()

    return render(request, 'order_items/form.html', {
        'form': form,
        'order': order,
        'title': 'Create Order Item'
    })
  

@login_required
def order_item_list(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Ensure that the logged-in user has access to this order
    if order.user != request.user and not request.user.is_staff:
        return redirect('app:order_list')  # Redirect to the order list if unauthorized

    order_items = order.items.all()  # Get all order items for the specific order

    return render(request, 'order_items/list.html', {
        'order_items': order_items,
        'order': order
    })

@login_required
def order_item_delete(request, order_id, item_id):
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, id=item_id, order=order)

    if order.user != request.user and not request.user.is_staff:
        return redirect('app:order_list')  # Redirect if unauthorized
    if order.status !="draft":
        messages.error(request, "Can't Edite order.")
        return redirect('app:order_listA')
    if request.method == 'POST':
        order_item.delete()
        return redirect('app:order_item_list', order_id=order.id)

    return render(request, 'order_items/confirm_delete.html', {
        'order': order,
        'order_item': order_item
    })

from django.contrib.auth.forms import AuthenticationForm
def login_view(request):
    if request.user.is_authenticated:
        return redirect('app:category_list')  # Redirect to home if already logged in

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('app:category_list')  # Redirect after successful login
        else:
            messages.error(request, "Invalid username or password.")

    else:
        form = AuthenticationForm()

    return render(request, 'authadmin/login.html', {'form': form, 'title': 'Login'})

from django.contrib.auth.forms import PasswordChangeForm

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Keep user logged in after password change
            messages.success(request, "Your password has been successfully updated.")
            return redirect('app:category_list')  # Redirect to profile or home page
        else:
            print( "Please correct the er")
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'authadmin/change_password.html', {'form': form, 'title': 'Change Password'})


def logout_view(request):
    logout(request)
    return redirect('app:login')  # Redirect to home or login page after logout
def home(request):
        medicines = Medicine.objects.all()
        return render(request, 'home.html')

def medicine_show(request):
    category_slug = request.GET.get('category')
    ingredient_id = request.GET.get('ingredient')
    
    medicines = Medicine.objects.all()
    
    # فلترة حسب الفئة
    if category_slug:
        medicines = medicines.filter(category__slug=category_slug)
    
    # فلترة حسب المادة الفعالة باستخدام ID
    if ingredient_id:
        try:
            ingredient = ActiveIngredient.objects.get(id=ingredient_id)
            medicines = medicines.filter(active_ingredients=ingredient)
        except ActiveIngredient.DoesNotExist:
            pass
    
    categories = Category.objects.all()
    active_ingredients = ActiveIngredient.objects.all()
    
    return render(request, 'home.html', {
        'medicines': medicines,
        'categories': categories,
        'active_ingredients': active_ingredients,
        'selected_ingredient_id': ingredient_id,
    })
from .models import About

def about_edit(request):
    about = About.objects.first()

    if request.method == 'POST':
        form = AboutForm(request.POST, instance=about)
        if form.is_valid():
            form.save()
            return redirect('app:about_edit')  # refresh page or redirect
    else:
        form = AboutForm(instance=about)
    
    return render(request, 'about/about_form.html', {'form': form, 'title': 'About Information'})
# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             login(request, user)
#             return redirect('app:profile')  # Redirect to profile after successful login
#         else:
#             messages.error(request, 'Invalid username or password.')
    
#     return render(request, 'User/login.html')


# def Enteremail(request):
#     email1= request.session.get('email')
#     if request.method == 'POST':
#         email1=request.POST['email']
#         request.session['email']=email1
#         user1=User.objects.filter(email=email1).first()
#         if user1:
#             # send_otp_via_email(user1.email)
#             return redirect('app:Forcode')
#         else:
#             print('No Account you must register')   
#             return redirect('app:register') 

#     return render(request, 'User/forgetpass.html')


# def Forcode(request):
#     email1= request.session.get('email')
#     if request.method == 'POST':
#         code=request.POST['code']
#         user1=User.objects.filter(email=email1).first()
#         print(user1)
#         if user1.otp == code:
#             user1.is_verified=True
#             user1.save()
#             login(request, user1)
#         return redirect('app:resetpassword') 
#     return render(request, 'User/Forcode.html',{'email':email1})

from .forms import UserRegistrationForm, CustomerAddressForm
from .emails import send_otp_via_email
def registerCus(request):

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        # person_form = CustomerAddressForm(request.POST, request.FILES)
        if user_form.is_valid():
            user1 = user_form.save()
            # person1 = person_form.save(commit=False)
            # person1.user = user
            # person1.save()
            login(request, user1)
            Wallet.objects.create(user=user1,Amount=0)
            request.session['email'] = user1.email
            send_otp_via_email(user1.email)
            return redirect('app:Regcode')
        else:
            print(user_form.errors)
            # print(person_form.errors)
    else:
        user_form = UserRegistrationForm()
        # person_form = CustomerAddressForm()
    return render(request, 'User/register.html', {'user_form': user_form})

def loginCus(request):
    # if request.user.is_authenticated:
    #     return redirect('app:home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('app:home')
        else:
            # Form errors will be displayed automatically in template
            print(form.errors)
    else:
        form = UserLoginForm()
    
    return render(request, 'User/login.html', {'user_form': form})


def forget_password(request):
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                # Check if user exists
                user = User.objects.get(email=email)
                # Generate and send OTP
                send_otp_via_email(email)
              
             
                
                # Store email in session for verification
                request.session['reset_email'] = email
                messages.success(request, 'OTP has been sent to your email!')
                return redirect('app:verify_otp')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
    else:
        form = ForgetPasswordForm()
    
    return render(request, 'forget_password.html', {'form': form})

def verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('app:forget_password')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            try:
                user = User.objects.get(email=email)
                print(user.otp)
                
                # Check if OTP is expired (e.g., 10 minutes)
           
                
                if str(user.otp) == str(otp):
                    # OTP verified successfully
                    request.session['otp_verified'] = True
                    messages.success(request, 'OTP verified successfully!')
                    return redirect('app:reset_password')
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid request.')
                return redirect('app:forget_password')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'verify_otp.html', {'form': form, 'email': email})

def reset_password(request):
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified')
    
    if not email or not otp_verified:
        messages.error(request, 'Session expired. Please start the process again.')
        return redirect('app:forget_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'reset_password.html', {'form': form})
            
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.otp = None  # Clear OTP after successful reset
                user.otp_created_at = None
                user.is_verified = True
                user.save()
                
                # Update session if user is logged in
                update_session_auth_hash(request, user)
                
                # Clear session data
                del request.session['reset_email']
                del request.session['otp_verified']
                
                messages.success(request, 'Password reset successfully! You can now login with your new password.')
                return redirect('app:loginCus')  # Change to your login URL name
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('app:forget_password')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'reset_password.html', {'form': form})

def Regcode(request):
    email1= request.session.get('email')
    if request.method == 'POST':
        code=request.POST['code']
        user1=User.objects.filter(email=email1).first()
        if user1.otp == code:
            user1.is_verified=True
            user1.save()
            login(request, user1)
            return redirect('app:medicine_show') 


    return render(request, 'User/Regcode.html',{'email':email1})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!', extra_tags='profile')
            else:
                # Better error handling
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}", extra_tags='profile')
          
        elif form_type == 'password':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!', extra_tags='password')
            else:
                for error in form.errors.values():
                    messages.error(request, error, extra_tags='password')
        
        elif form_type == 'save_address':
            address_id = request.POST.get('address_id')
            
            try:
                if address_id:
                    # Edit existing address
                    address = CustomerAddress.objects.get(id=address_id, user=request.user)
                    form = AddressForm(request.POST, instance=address)
                else:
                    # Create new address
                    form = AddressForm(request.POST)
                
                if form.is_valid():
                    address = form.save(commit=False)
                    address.user = request.user
                    
                    # Handle location fields
                    loction_x = request.POST.get('loction_x')
                    loction_y = request.POST.get('loction_y')
                    
                    if loction_x and loction_y:
                        try:
                            address.x = float(loction_x)
                            address.y = float(loction_y)
                        except (ValueError, TypeError):
                            messages.error(request, 'Invalid location coordinates', extra_tags='address')
                            return redirect('app:profile')
                    
                    # If this is set as default, unset other defaults
                    if address.is_default:
                        CustomerAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
                    
                    address.save()
                    messages.success(request, 'Address saved successfully!', extra_tags='address')
                else:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}", extra_tags='address')
            
            except CustomerAddress.DoesNotExist:
                messages.error(request, 'Address not found!', extra_tags='address')
            except Exception as e:
                messages.error(request, f'Error saving address: {str(e)}', extra_tags='address')
        
        elif form_type == 'set_default_address':
            address_id = request.POST.get('address_id')
            try:
                # Unset all defaults
                CustomerAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
                # Set new default
                address = CustomerAddress.objects.get(id=address_id, user=request.user)
                address.is_default = True
                address.save()
                messages.success(request, 'Default address updated!', extra_tags='address')
            except CustomerAddress.DoesNotExist:
                messages.error(request, 'Address not found!', extra_tags='address')
        
        elif form_type == 'delete_address':
            address_id = request.POST.get('address_id')
            try:
                address = CustomerAddress.objects.get(id=address_id, user=request.user)
                address.delete()
                messages.success(request, 'Address deleted successfully!', extra_tags='address')
            except CustomerAddress.DoesNotExist:
                messages.error(request, 'Address not found!', extra_tags='address')
        
        return redirect('app:profile')
    
    return render(request, 'User/profile.html')

# # @login_required(login_url='app:login')

# # def profile(request):
# #     # try:
# #     #     person_instance = request.user.
# #     # except person.DoesNotExist:
# #     #     person_instance = person.objects.create(user=request.user)

# #     if request.method == 'POST':
# #             Des1=request.POST['Des']
# #             phone1=request.POST['phone']
# #             work1=request.POST['work']
            
# #             im1=request.FILES.get('Img') 
# #             if im1:
# #                 person_instance.phone=im1
# #             person_instance.Des=Des1
# #             person_instance.phone=phone1
# #             person_instance.work=work1
# #             person_instance.save()
       
# #             return redirect('app:profile')
# #     else:
# #         person_form = PersonForm(instance=person_instance)

# #     return render(request, 'User/profile.html', {
# #         'form': person_form,
# #         'person': person_instance
# #     })
# from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
# @login_required(login_url='app:login')
# def change_password(request):
#     if request.method == 'POST':
#         form = PasswordChangeForm(user=request.user, data=request.POST)
#         if form.is_valid():
#             user = form.save()
#             update_session_auth_hash(request, user)  # يبقيه مسجل دخول
#             messages.success(request, "Password changed successfully.")
#             return redirect('app:profile')  # عدّل حسب اسم الـ url عندك
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = PasswordChangeForm(user=request.user)
#     messages.error(request, "Please correct the errors below.")
#     return redirect('app:profile')

# def user_logout(request):
#     logout(request)
#     return redirect('app:login')  # غيّر 'login' لاسم صفحة تسجيل الدخول عندك

# from django.contrib.auth.hashers import check_password, make_password
# def resetpassword(request):
#     email1= request.session.get('email')    
#     if request.method=="POST":
#         user1=User.objects.filter(email=email1).first()
#         password1=request.POST['password']
#         Cpassword1=request.POST['Cpassword']
#         paa=make_password(password1)
#         if Cpassword1 != password1:
#             print('11')
       
#         user1.set_password(password1)
#         user1.save()
#         login(request, user1)
#         messages.success(request, "Password is reseted")  
       
#         return redirect('app:profile') 
#     return render(request,'User/resetpassword.html')


from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BatchMed
from .forms import BatchMedForm

# =============================
# 📋 BatchMed List
# =============================
@login_required
def batchmed_list(request):
    query = request.GET.get('q', '')
    medicine_filter = request.GET.get('medicine', '')
    expired_filter = request.GET.get('expired', '')

    batches = BatchMed.objects.all()

    # فلترة حسب النص (البحث)
    if query:
        batches = batches.filter(
            Q(batch_number__icontains=query) |
            Q(medicine__name__icontains=query) |
            Q(medicine__brand__icontains=query)
        ).distinct()

    # فلترة حسب الدواء
    if medicine_filter:
        batches = batches.filter(medicine_id=medicine_filter)

    # فلترة حسب الصلاحية
    if expired_filter == 'expired':
        batches = batches.filter(expiration_date__lt=timezone.now().date())
    elif expired_filter == 'active':
        batches = batches.filter(
            Q(expiration_date__gte=timezone.now().date()) | 
            Q(expiration_date__isnull=True)
        )

    # إحصائيات سريعة
    total_batches = batches.count()
    expired_batches = batches.filter(expiration_date__lt=timezone.now().date()).count()
    low_quantity_batches = batches.filter(quantity__lt=10).count()

    return render(request, 'batchmed/list.html', {
        'batches': batches,
        'query': query,
        'medicine_filter': medicine_filter,
        'expired_filter': expired_filter,
        'total_batches': total_batches,
        'expired_batches': expired_batches,
        'low_quantity_batches': low_quantity_batches,
    })

# =============================
# ➕ Create BatchMed
# =============================
@login_required
def batchmed_create(request):
    # فقط الموظفين يمكنهم إضافة دفعات
    if not request.user.is_staff:
        return redirect('app:batchmed_list')

    form = BatchMedForm(request.POST or None)
    
    if form.is_valid():
        batch = form.save(commit=False)
        batch.save()
        return redirect('app:batchmed_list')

    return render(request, 'batchmed/form.html', {
        'form': form,
        'title': 'Add New Batch'
    })

# =============================
# ✏️ Edit BatchMed
# =============================
@login_required
def batchmed_edit(request, pk):
    # فقط الموظفين يمكنهم التعديل
    if not request.user.is_staff:
        return redirect('app:batchmed_list')

    batch = get_object_or_404(BatchMed, pk=pk)
    form = BatchMedForm(request.POST or None, instance=batch)
    
    if form.is_valid():
        form.save()
        return redirect('app:batchmed_list')

    return render(request, 'batchmed/form.html', {
        'form': form,
        'title': 'Edit Batch',
        'batch': batch
    })

# =============================
# ❌ Delete BatchMed
# =============================
@login_required
def batchmed_delete(request, pk):
    # فقط الموظفين يمكنهم الحذف
    if not request.user.is_staff:
        return redirect('app:batchmed_list')

    batch = get_object_or_404(BatchMed, pk=pk)

    if request.method == 'POST':
        batch.delete()
        return redirect('app:batchmed_list')

    return render(request, 'batchmed/confirm_delete.html', {
        'batch': batch
    })

# =============================
# 📊 BatchMed Detail
# =============================
@login_required
def batchmed_detail(request, pk):
    batch = get_object_or_404(BatchMed, pk=pk)
    
    return render(request, 'batchmed/detail.html', {
        'batch': batch
    })



@login_required
def account_dashboard(request):
    # Get or create wallet for user
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Get recent transactions
    recent_operations = OpertionMoney.objects.filter(MyAccount=wallet).order_by('-Date1')[:10]
    
    context = {
        'wallet': wallet,
        'recent_operations': recent_operations,
    }
    return render(request, 'User/account_dashboard.html', context)



@login_required
def add_money(request):
    # Get or create wallet for the user
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = AddMoneyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create the operation but don't save yet
                operation = form.save(commit=False)
                operation.MyAccount = wallet
                operation.Method = 'Add'  # Set method to Add
                operation.state = 'pending'  # Set initial state
                operation.save()
                
                messages.success(request, f'✅ Add money request for ${operation.Amount} submitted successfully! Status: {operation.state}')
                return redirect('app:add_money')  # Redirect back to add money page
                
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
        else:
            messages.error(request, '❌ Please correct the errors below.')
    else:
        form = AddMoneyForm()
    
    context = {
        'wallet': wallet,
        'form': form,
    }
    return render(request, 'User/add_money.html', context)



@login_required
def withdraw_money(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = WithdrawMoneyForm(request.POST, request.FILES, wallet=wallet)
        if form.is_valid():
            operation = form.save(commit=False)
            operation.MyAccount = wallet
            operation.Method = 'Withdraw'
            operation.save()
            
            messages.success(request, f'Withdrawal request for ${operation.Amount} submitted successfully! Status: {operation.state}')
            return redirect('app:account_dashboard')
    else:
        form = WithdrawMoneyForm(wallet=wallet)
    
    context = {
        'wallet': wallet,
        'form': form,
        'action': 'Withdraw Money'
    }
    return render(request, 'User/withdraw_money.html', context)

@login_required
def transaction_history(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    operations = OpertionMoney.objects.filter(MyAccount=wallet).order_by('-Date1')
    
    context = {
        'wallet': wallet,
        'operations': operations,
    }
    return render(request, 'User/transaction_history.html', context)

from django.http import JsonResponse,Http404
from django.db.models import Count

def medicine_comments(request, medicine_id):
    try:
        # Get the medicine object or return 404
        medicine = get_object_or_404(Medicine, id=medicine_id)
        
        # Get all comments for this medicine
        comments = Comment.objects.filter(comment_medicine=medicine).select_related('comment_customer').order_by('-id')
        
        # Get comment statistics
        comment_stats = Comment.objects.filter(comment_medicine=medicine).values('type').annotate(count=Count('id'))
        
        context = {
            'medicine': medicine,
            'comments': comments,
            'comment_stats': comment_stats,
        }
        
        return render(request, 'medicine_comments.html', context)
    
    except Http404:
        available_medicines = Medicine.objects.all()[:10]
        messages.error(request, f'Medicine with ID {medicine_id} not found.')
        return redirect('app:medicine_list')

from django.http import JsonResponse
from transformers import pipeline

model_save_path = "./sentiment_model"
sentiment_pipeline = pipeline("sentiment-analysis", model=model_save_path, tokenizer=model_save_path)


@login_required
def add_comment(request, medicine_id):
    try:
        medicine = get_object_or_404(Medicine, id=medicine_id)
        
        if request.method == 'POST':
            text = request.POST.get('text', '').strip()
            # comment_type = request.POST.get('type', 'general')
           
            comment_type = sentiment_pipeline(text)[0]
            print(comment_type['label'])
            if text:
                # Create the comment
                Comment.objects.create(
                    text=text,
                    type=comment_type['label'],
                    
                    comment_customer=request.user,
                    comment_medicine=medicine
                )
                messages.success(request, 'Comment added successfully!')
            else:
                messages.error(request, 'Comment text cannot be empty!')
        
        # FIX: Redirect back to the comments display page, not the add_comment page
        return redirect('app:medicine_comments', medicine_id=medicine_id)
    
    except Http404:
        messages.error(request, f'Medicine with ID {medicine_id} not found.')
        return redirect('app:medicine_list')
    
from django.db import transaction
from django.utils import timezone

def medicine_detail(request, medicine_id):
    """Show medicine details page"""
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    context = {
        'medicine': medicine,
        'related_medicines': Medicine.objects.filter(
            category=medicine.category
        ).exclude(id=medicine.id)[:4]
    }
    return render(request, 'medicine_detail.html', context)

@login_required
@transaction.atomic
def add_to_cart(request, medicine_id):
    """Add medicine to cart - create order if needed"""
    if request.method == 'POST':
        medicine = get_object_or_404(Medicine, id=medicine_id)
        quantity = request.POST.get('quantity', 1)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messages.error(request, 'Quantity must be greater than 0')
                return redirect('app:medicine_detail', medicine_id=medicine_id)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid quantity')
            return redirect('app:medicine_detail', medicine_id=medicine_id)
        
        # Check if medicine is available
        if not medicine.is_available(quantity):
            messages.error(request, f'Sorry, only {medicine.total_quantity} items available')
            return redirect('app:medicine_detail', medicine_id=medicine_id)
        
        # Get or create order with status 'draft' for the user
        order = Order.objects.filter(
            user=request.user,
            status='draft'
        ).first()
        
        if not order:
            # Create new order
            order = Order.objects.create(
                user=request.user,
                status='draft',
                payment_delivery=False,  # Default value
                # price_delivery=False     # Default value
            )
        
        # Check if medicine already exists in order items
        order_item = OrderItem.objects.filter(
            order=order,
            medicine=medicine
        ).first()
        
        if order_item:
            # Update quantity if item already exists
            order_item.quantity += quantity
            order_item.save()
            messages.success(request, f'Updated {medicine.name} quantity to {order_item.quantity}')
        else:
            # Create new order item
            OrderItem.objects.create(
                order=order,
                medicine=medicine,
                quantity=quantity
            )
            messages.success(request, f'Added {quantity} {medicine.name} to your cart')
        
        return redirect('app:medicine_detail', medicine_id=medicine_id)
    
    return redirect('app:medicine_detail', medicine_id=medicine_id)    
import json

@login_required
def order_list(request):
    """Display all orders for the user"""
    orders = Order.objects.filter(user=request.user).select_related('address').prefetch_related('items')
    
    # Group orders by status for better organization
    orders_by_status = {
        'active': orders.exclude(status__in=['completed', 'cancelled']),
        'completed': orders.filter(status='completed'),
        'cancelled': orders.filter(status='cancelled'),
    }
    
    context = {
        'orders_by_status': orders_by_status,
        'total_orders': orders.count(),
    }
    return render(request, 'order_list.html', context)

@login_required
def order_detail(request, order_id):
    """Display order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all().select_related('medicine'),
    }
    return render(request, 'order_detail.html', context)

@login_required
def order_items(request, order_id):
    """Display and manage order items for a specific order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Handle AJAX requests for item updates
        return handle_ajax_item_request(request, order)
    
    context = {
        'order': order,
        'order_items': order.items.all().select_related('medicine'),
    }
    return render(request, 'order_items.html', context)

@login_required
@transaction.atomic
def update_order_item(request, item_id):
    """Update order item quantity"""
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    
    if not order_item.can_edit():
        messages.error(request, 'Cannot edit items in this order status')
        return redirect('app:order_items', order_id=order_item.order.id)
    
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                # If quantity is 0 or negative, delete the item
                order_item.delete()
                messages.success(request, 'Item removed from order')
            else:
                # Check stock availability
                if order_item.medicine.is_available(quantity):
                    order_item.quantity = quantity
                    order_item.save()
                    messages.success(request, 'Item quantity updated')
                else:
                    messages.error(request, f'Only {order_item.medicine.total_quantity} items available')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid quantity')
    
    return redirect('app:order_items', order_id=order_item.order.id)

@login_required
@transaction.atomic
def delete_order_item(request, item_id):
    """Delete order item"""
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    order_id = order_item.order.id
    
    if not order_item.can_edit():
        messages.error(request, 'Cannot delete items in this order status')
    else:
        order_item.delete()
        messages.success(request, 'Item removed from order')
    
    return redirect('app:order_items', order_id=order_id)
import requests
@login_required
def order_payment(request, order_id):
    """Handle order payment with prescription and address selection"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not order.can_pay:
        messages.error(request, 'This order cannot be paid at the moment')
        return redirect('app:order_detail', order_id=order.id)
    
    # Get user's prescriptions and addresses
    user_prescriptions = Prescription.objects.filter(patient=request.user)
    user_addresses = CustomerAddress.objects.filter(user=request.user)
    
    about = About.objects.first()
    delivery_info = None
    
    # Calculate delivery info if address is selected
    selected_address_id = request.POST.get('selected_address') or request.GET.get('selected_address')
    if selected_address_id:
        try:
            selected_address = CustomerAddress.objects.get(id=selected_address_id, user=request.user)
            delivery_info = calculate_delivery_info(about, selected_address)
        except CustomerAddress.DoesNotExist:
            pass
    
    if request.method == 'POST':
        selected_prescriptions = request.POST.getlist('prescriptions')
        selected_address_id = request.POST.get('selected_address')
        need_delivery = request.POST.get('payment_delivery') == 'true'  # Get delivery choice
        print(selected_address_id)
        # Validate delivery address if delivery is needed
        if need_delivery and not selected_address_id:
            messages.error(request, 'Please select a delivery address for delivery option')
            return redirect('app:order_payment', order_id=order.id)
        
        try:
            selected_address = CustomerAddress.objects.get(id=selected_address_id, user=request.user) if selected_address_id else None
        except CustomerAddress.DoesNotExist:
            messages.error(request, 'Invalid address selected')
            return redirect('app:order_payment', order_id=order.id)
        
        # Calculate delivery fee if delivery is needed
        delivery_fee = Decimal('0.00')
        calculated_distance = None
        
        if need_delivery and selected_address and about:
            delivery_info = calculate_delivery_info(about, selected_address)
            if delivery_info and delivery_info['within_range']:
                delivery_fee = delivery_info['delivery_fee']
                calculated_distance = delivery_info['distance']
            else:
                messages.error(request, 'Selected address is outside delivery range')
                return redirect('app:order_payment', order_id=order.id)
        total= delivery_fee + order.total_amount
        if request.user.wallet.Amount < total:
            messages.error(request, 'Not Enough Money')
            return redirect('app:order_payment', order_id=order.id)
        request.user.wallet.Amount -=float(total)
        

        # Update order
        if selected_prescriptions:
            order.prescription.set(selected_prescriptions)
        
        order.selected_address = selected_address
        order.payment_delivery = need_delivery  # Set delivery flag
        order.delivery_fee = delivery_fee
        order.calculated_distance = calculated_distance
        order.status = 'processing'
        order.payment_reference = f"PAY-{order.id.hex[:8].upper()}"
        order.save()
        request.user.wallet.save()
        
        messages.success(request, f'Payment successful! Reference Withdrow Money from Your Wallet')
        if need_delivery:
            messages.info(request, f'Delivery fee: ${delivery_fee:.2f}')

            
        return redirect('app:order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'prescriptions': user_prescriptions,
        'addresses': user_addresses,
        'about': about,
        'delivery_info': delivery_info,
    }
    return render(request, 'order_payment.html', context)

def calculate_delivery_info(about, selected_address):
    """Calculate delivery distance and fee"""
    if not about or not selected_address:
        return None
    
    try:
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{about.loction_x},{about.loction_y}:{selected_address.x},{selected_address.y}/json?key=wncqPXyuwK1DoGAegYSHAJ5SyE3ATzh7"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('routes') and len(data['routes']) > 0:
                distance_km = data['routes'][0]['summary']['lengthInMeters'] / 1000
                
                within_range = distance_km <= about.maxDelKM
                delivery_fee = distance_km * float(about.priceforKM) if within_range else 0
                
                return {
                    'distance': round(distance_km, 2),
                    'within_range': within_range,
                    'delivery_fee': Decimal(str(delivery_fee)),
                    'max_delivery_km': about.maxDelKM,
                    'price_per_km': about.priceforKM
                }
    except Exception as e:
        print(f"Error calculating delivery: {e}")
    
    return None

@login_required
def calculate_delivery(request):
    """AJAX view to calculate delivery distance and fee"""
    address_id = request.GET.get('address_id')
    order_id = request.GET.get('order_id')
    
    try:
        address = CustomerAddress.objects.get(id=address_id, user=request.user)
        about = About.objects.first()
        
        if about:
            delivery_info = calculate_delivery_info(about, address)
            if delivery_info:
                return JsonResponse({
                    'success': True,
                    'distance': delivery_info['distance'],
                    'within_range': delivery_info['within_range'],
                    'delivery_fee': str(delivery_info['delivery_fee']),
                    'max_delivery_km': delivery_info['max_delivery_km']
                })
        
        return JsonResponse({'success': False, 'error': 'Could not calculate delivery'})
    
    except CustomerAddress.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Address not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Views
@login_required
def upload_prescription(request):
    """Upload a new prescription"""
    if request.method == 'POST':
        form = PrescriptionFormCus(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.patient = request.user
            prescription.save()
            messages.success(request, 'Prescription uploaded successfully and is pending verification')
            
            # Redirect back to payment page if order_id is provided
            order_id = request.GET.get('order_id')
            if order_id:
                return redirect('app:order_payment', order_id=order_id)
            return redirect('app:prescription_list')  # Or wherever you list prescriptions
    else:
        form = PrescriptionForm()
    
    return render(request, 'upload_prescription.html', {'form': form})

@login_required
def cancel_order(request, order_id):
    """Cancel an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not order.can_cancel:
        messages.error(request, 'This order cannot be cancelled')
    else:
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Order has been cancelled')
    
    return redirect('app:order_list')

def handle_ajax_item_request(request, order):
    """Handle AJAX requests for order item operations"""
    try:
        data = json.loads(request.body)
        action = data.get('action')
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        
        if action == 'update' and item_id:
            item = get_object_or_404(OrderItem, id=item_id, order=order)
            if item.can_edit():
                item.quantity = quantity
                item.save()
                return JsonResponse({
                    'success': True,
                    'line_total': float(item.line_total()),
                    'order_total': float(order.total_amount()),
                    'item_count': order.item_count
                })
        
        elif action == 'delete' and item_id:
            item = get_object_or_404(OrderItem, id=item_id, order=order)
            if item.can_edit():
                item.delete()
                return JsonResponse({
                    'success': True,
                    'order_total': float(order.total_amount()),
                    'item_count': order.item_count
                })
        
        return JsonResponse({'success': False, 'error': 'Invalid action'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def operation_list(request):
    query = request.GET.get('q', '')
    method_filter = request.GET.get('method', '')
    status_filter = request.GET.get('status', '')
    
    operations = OpertionMoney.objects.all().select_related('MyAccount').order_by('-Date1')
    
    # Apply filters
    if query:
        operations = operations.filter(
            models.Q(code__icontains=query) |
            models.Q(Account__icontains=query) |
            models.Q(type__icontains=query)
        )
    
    if method_filter:
        operations = operations.filter(Method=method_filter)
    
    if status_filter:
        operations = operations.filter(state=status_filter)

    # Calculate summary statistics
    total_added = operations.filter(Method='Add').aggregate(total=models.Sum('Amount'))['total'] or 0
    total_withdrawn = operations.filter(Method='Withdraw').aggregate(total=models.Sum('Amount'))['total'] or 0
    pending_count = operations.filter(state='pending').count()

    paginator = Paginator(operations, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'operation/list.html', {
        'operations': page_obj,
        'page_obj': page_obj,
        'total_added': total_added,
        'total_withdrawn': total_withdrawn,
        'pending_count': pending_count,
    })


@login_required
def operation_approve(request, pk):
    operation = get_object_or_404(OpertionMoney, pk=pk)
    
    # Check if operation is pending
    if operation.state != 'pending':
        messages.error(request, 'This operation has already been processed.')
        return redirect('app:operation_list')
    
    # Update operation state to Success
    operation.state = 'Success'
    operation.Date2 = timezone.now()  # Set completion date
    operation.save()
    
    # Update wallet amount based on operation type
    wallet = operation.MyAccount
    if operation.Method == 'Add':
        wallet.Amount += operation.Amount
        messages.success(request, f'Successfully approved money addition of ${operation.Amount}.')
    elif operation.Method == 'Withdraw':
        # Check if sufficient balance exists for withdrawal
        if wallet.Amount >= operation.Amount:
            wallet.Amount -= operation.Amount
            messages.success(request, f'Successfully approved money withdrawal of ${operation.Amount}.')
        else:
            operation.state = 'Failed'
            operation.save()
            messages.error(request, 'Insufficient balance for withdrawal.')
            return redirect('app:operation_list')
    
    wallet.save()
    
    return redirect('app:operation_list')

@login_required
def operation_reject(request, pk):
    operation = get_object_or_404(OpertionMoney, pk=pk)
    
    # Check if operation is pending
    if operation.state != 'pending':
        messages.error(request, 'This operation has already been processed.')
        return redirect('app:operation_list')
    
    # Update operation state to Failed
    operation.state = 'Failed'
    operation.Date2 = timezone.now()  # Set completion date
    operation.save()
    
    messages.success(request, 'Operation has been rejected.')
    return redirect('app:operation_list')

@login_required
def operation_approve_withdraw(request, pk):
    operation = get_object_or_404(OpertionMoney, pk=pk)
    
    # Check if operation is pending and is a withdrawal
    if operation.state != 'pending' or operation.Method != 'Withdraw':
        messages.error(request, 'Invalid operation for approval.')
        return redirect('app:operation_list')
    
    if request.method == 'POST':
        # Get form data
        transaction_code = request.POST.get('transaction_code')
        proof_image = request.FILES.get('proof_image')
        notes = request.POST.get('notes', '')
        
        # Validate required fields
        if not transaction_code or not proof_image:
            messages.error(request, 'Transaction code and proof image are required.')
            return redirect('app:operation_list')
        
        # Check balance
        if operation.MyAccount.Amount < operation.Amount:
            messages.error(request, 'Insufficient balance for withdrawal.')
            return redirect('app:operation_list')
        
        # Update operation with provided details
        operation.code = transaction_code
        operation.image = proof_image
        operation.state = 'Success'
        operation.Date2 = timezone.now()
        operation.save()
        
        # Update wallet balance
        wallet = operation.MyAccount
        wallet.Amount -= operation.Amount
        wallet.save()
        
        # Add notes if provided (you might want to store this in a separate model)
        if notes:
            # You can create an OperationNote model or use messages
            messages.info(request, f'Notes: {notes}')
        
        messages.success(request, f'Withdrawal of ${operation.Amount} approved successfully.')
        return redirect('app:operation_list')
    
    messages.error(request, 'Invalid request method.')
    return redirect('app:operation_list')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Order
from .forms import OrderEditForm

@login_required
def order_edit(request, pk):
    """Edit order status and assign driver"""
    order = get_object_or_404(Order, id=pk)
    
    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order)
        
        if form.is_valid():
            # حفظ البيانات من الفورم
            updated_order = form.save(commit=False)
            
            # معالجة scheduled_for يدوياً
            scheduled_str = request.POST.get('scheduled_for', '').strip()
            if scheduled_str:
                try:
                    # تحويل النص إلى datetime
                    naive_datetime = datetime.strptime(scheduled_str, '%Y-%m-%dT%H:%M')
                    
                    # جعله timezone aware
                    if timezone.is_naive(naive_datetime):
                        aware_datetime = timezone.make_aware(naive_datetime)
                        updated_order.scheduled_for = aware_datetime
                    else:
                        updated_order.scheduled_for = naive_datetime
                except ValueError:
                    messages.error(request, 'Invalid date format for scheduled time.')
                    context = {
                        'form': form,
                        'order': order,
                        'title': f'Edit Order {order.id}'
                    }
                    return render(request, 'orders/edit.html', context)
            else:
                updated_order.scheduled_for = None
            
            # حفظ التعديلات
            updated_order.save()
            form.save_m2m()  # لحفظ علاقات ManyToMany
            
            # رسائل النجاح
            old_status = order.status
            old_driver = order.his_driver
            
            if old_status != updated_order.status:
                messages.success(request, f'Order status changed from {old_status} to {updated_order.status}')
            
            if old_driver != updated_order.his_driver:
                if updated_order.his_driver:
                    messages.success(request, f'Driver assigned: {updated_order.his_driver.user.get_full_name()}')
                else:
                    messages.info(request, 'Driver assignment removed')
            
            messages.success(request, f'Order #{order.id} has been updated successfully!')
            return redirect('app:order_listA')
        else:
            messages.error(request, 'Please correct the errors below.')
            # لعرض الأخطاء للمساعدة في التصحيح
            print("Form errors:", form.errors)
    else:
        form = OrderEditForm(instance=order)
    
    context = {
        'form': form,
        'order': order,
        'title': f'Edit Order {order.id}'
    }
    return render(request, 'orders/edit.html', context)
from django.views.decorators.cache import never_cache
def driver_login(request):
    # if request.user.is_authenticated:
    #     # Check if user is a driver (in session or has specific pattern)
    #     if request.session.get('is_driver', False):
    #         return redirect('app:driver_dashboard')
    #     else:
    #         messages.warning(request, 'You are logged in as a regular user. Please logout first.')
    #         return redirect('app:home')
    
    if request.method == 'POST':
        form = DriverLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
         
            if user is not None:

                    # Mark as driver in session
                    request.session['is_driver'] = True
                    request.session['driver_username'] = username
                    
                    # Login the user
                    login(request, user)
                    messages.success(request, 'Driver login successful!')
                    return redirect('app:driver_dashboard')
                
            else:
                    messages.error(request, 'This account is not authorized as a driver.')
 
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = DriverLoginForm()
    
    return render(request, 'drivers/login.html', {'form': form})
# In views.py
from django.utils import timezone
import requests

@login_required
@never_cache
def driver_dashboard(request):
    if not request.session.get('is_driver', False):
        messages.error(request, 'Access denied. Driver login required.')
        return redirect('app:driver_login')
    
    # Get driver profile
    try:
        driver_profile = driver.objects.get(user=request.user)
    except driver.DoesNotExist:
        messages.error(request, 'Driver profile not found.')
        return redirect('app:driver_login')
    
    # Get assigned orders
    assigned_orders = Order.objects.filter(
        his_driver=driver_profile,
        status__in=['processing', 'ready', 'delivering']
    ).select_related('user', 'address')
    
    # Get completed orders (for history)
    completed_orders = Order.objects.filter(
        his_driver=driver_profile,
        status='completed'
    ).order_by('-placed_at')[:10]
    
    # Get about settings
    about = About.objects.first()
    
    context = {
        'driver': driver_profile,
        'assigned_orders': assigned_orders,
        'completed_orders': completed_orders,
        'about': about,
        'tomtom_api_key': 'wncqPXyuwK1DoGAegYSHAJ5SyE3ATzh7',  # Replace with your actual key
    }
    return render(request, 'drivers/dashboard_new.html', context)


@login_required
# @require_POST
def update_driver_location(request):
    """Update driver's current location"""
    try:
        driver_profile = driver.objects.get(user=request.user)
        x = request.POST.get('y')
        y = request.POST.get('x')
        
        if x and y:
            driver_profile.current_x = float(x)
            driver_profile.current_y = float(y)
            driver_profile.last_online = timezone.now()
            driver_profile.save()
            
            return JsonResponse({'success': True, 'message': 'Location updated'})
        return JsonResponse({'success': False, 'error': 'Invalid coordinates'})
    except driver.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Driver not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
# @require_POST
def complete_order(request):
    """Mark order as completed"""
    try:
        driver_profile = driver.objects.get(user=request.user)
        order_id = request.POST.get('order_id')
        
        order = Order.objects.get(
            id=order_id,
            his_driver=driver_profile,
            status='delivering'
        )
        
        order.status = 'completed'
        order.save()
        
        return JsonResponse({'success': True, 'message': 'Order marked as completed'})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found or not deliverable'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_order_details(request, order_id):
    """Get order details for AJAX"""
    try:
        driver_profile = driver.objects.get(user=request.user)
        order = Order.objects.get(
            id=order_id,
            his_driver=driver_profile
        )
        
        # Get customer details
        customer = order.user
        
        data = {
            'success': True,
            'order': {
                'id': str(order.id),
                'status': order.status,
                'placed_at': order.placed_at.strftime('%Y-%m-%d %H:%M'),
                'delivery_fee': str(order.delivery_fee),
                'total_amount': str(order.total_amount()),
                'notes': order.notes,
            },
            'customer': {
                'name': customer.get_full_name() or customer.username,
                'phone': customer.phone if hasattr(customer, 'phone') else '',
                'email': customer.email,
            },
            'address': {
                'label': order.address.label if order.address else '',
                'address_line': order.address.address_line if order.address else '',
                'city': order.address.city if order.address else '',
                'phone': order.address.phone if order.address else '',
                'x': float(order.address.x) if order.address else 0,
                'y': float(order.address.y) if order.address else 0,
            }
        }
        
        # Get order items
        items = []
        for item in order.items.all():
            items.append({
                'medicine': str(item.medicine),
                'quantity': item.quantity,
                'line_total': str(item.line_total()),
            })
        data['items'] = items
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
def driver_logout(request):
    # Clear driver session
    if 'is_driver' in request.session:
        del request.session['is_driver']
    if 'driver_username' in request.session:
        del request.session['driver_username']
    
    # Logout user
    logout(request)
    messages.success(request, 'Driver logout successful!')
    return redirect('app:driver_login')

# Middleware to protect driver routes (alternative approach)
def driver_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_driver', False):
            messages.error(request, 'Driver access required.')
            return redirect('app:driver_login')
        return view_func(request, *args, **kwargs)
    return wrapper

# In views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import math
# In views.py

def order_locations_page(request, order_id):
    """Show order locations page"""
    from .models import Order, About, driver
    from django.shortcuts import get_object_or_404
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    about = About.objects.first()
    
    # Assign a driver if not already assigned (simplified logic)
    if not order.his_driver and order.status in ['ready', 'delivering']:
        # Find available active drivers
        available_drivers = driver.objects.filter(is_active=True)
        if available_drivers.exists():
            # Simple assignment: pick first available driver
            # In production, you might want more sophisticated logic
            order.his_driver = available_drivers.first()
            order.save()
    
    context = {
        'order': order,
        'about': about,
        'tomtom_api_key': 'wncqPXyuwK1DoGAegYSHAJ5SyE3ATzh7',  # Consider moving to settings
    }
    return render(request, 'orders/order_locations.html', context)

# views.py - FIX THIS PART
@require_GET
def get_driver_location(request, order_id):
    """API to get driver location"""
    try:
        from .models import Order
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Check if driver is assigned
        if not order.his_driver:
            return JsonResponse({
                'success': False, 
                'message': 'No driver assigned yet',
                'status': 'waiting'
            })
        
        driver_obj = order.his_driver
        
        # Check if driver is online (active within last 5 minutes)
        from django.utils import timezone
        from datetime import timedelta
        
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        is_online = driver_obj.last_online > five_minutes_ago
        
        # FIXED: Don't swap coordinates!
        # current_x should be longitude, current_y should be latitude
        if driver_obj.current_x is None or driver_obj.current_y is None:
            from .models import About
            about = About.objects.first()
            if about:
                current_x = about.loction_y  # longitude
                current_y = about.loction_x  # latitude
            else:
                current_x = 36.276  # Default longitude
                current_y = 33.513  # Default latitude
        else:
            # NO SWAPPING - use as stored in database
            current_x = driver_obj.current_x  # longitude
            current_y = driver_obj.current_y  # latitude
        
        return JsonResponse({
            'success': True,
            'driver_id': driver_obj.id,
            'driver_name': driver_obj.user.get_full_name() or driver_obj.user.username,
            'vehicle_type': driver_obj.vehicle_type or 'Car',
            'license_plate': driver_obj.license_plate or 'N/A',
            'current_x': current_y,  # longitude
            'current_y': current_x,  # latitude
            'is_online': is_online,
            'last_online': driver_obj.last_online.isoformat() if driver_obj.last_online else None,
            'order_status': order.status
        })
        
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Medicine, Category, ActiveIngredient
from .serializers import *
from rest_framework.permissions import IsAuthenticated ,AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def get_medicines(request):
    # Get base querysets
    medicines = Medicine.objects.all()
    categories = Category.objects.all()
    ingredients = ActiveIngredient.objects.all()

    # Apply filters from query parameters
    category_slug = request.query_params.get('category')
    ingredient_id = request.query_params.get('ingredient')

    if category_slug:
        medicines = medicines.filter(category__slug=category_slug)
    if ingredient_id:
        medicines = medicines.filter(active_ingredients__id=ingredient_id)

    # Remove duplicates that may appear from many-to-many filtering
    medicines = medicines.distinct()

    # Serialize
    medicine_serializer = MedicineSerializer(medicines, many=True, context={'request': request})
    category_serializer = CategorySerializer(categories, many=True)
    ingredient_serializer = ActiveIngredientSerializer(ingredients, many=True)

    data = {
        'medicines': medicine_serializer.data,
        'categories': category_serializer.data,
        'active_ingredients': ingredient_serializer.data,
    }
    return Response(data)

from rest_framework import generics, permissions
from User.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

class ProtectedView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'This is a protected endpoint'}
        return Response(content)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer  # you need to define this serializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wallet(request):
    user1 = request.user
    print(user1)
    try:
        wallet, created = Wallet.objects.get_or_create(user=user1)
        serializer = WalletSerializer(wallet)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Add money to wallet
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_money(request):
    """Add money to user's wallet"""
    try:
        # Get required data from request
        operation_type = request.data.get('type')  # Syriatel or MTN
        amount = request.data.get('amount')
        code = request.data.get('code')
        account_number = request.data.get('account_number')
        image = request.FILES.get('image')
        
        # Validate required fields
        if not all([operation_type, amount]):
            return Response({
                'status': 'error',
                'message': 'Type and amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({
                    'status': 'error',
                    'message': 'Amount must be greater than 0'
                }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({
                'status': 'error',
                'message': 'Invalid amount format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user's wallet
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        
        # Create operation record
        operation = OpertionMoney.objects.create(
            type=operation_type,
            Method='Add',
            Amount=amount,
            code=code,
            image=image,
            MyAccount=wallet,
            Account=account_number,
            state='pending'  # Starts as pending until admin approves
        )
        
        serializer = OpertionMoneySerializer(operation)
        
        return Response({
            'status': 'success',
            'message': 'Money addition request submitted successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Withdraw money from wallet
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_money(request):
    """Withdraw money from user's wallet"""
    try:
        # Get required data from request
        operation_type = request.data.get('type')  # Syriatel or MTN
        amount = request.data.get('amount')
        account_number = request.data.get('account_number')
        
        # Validate required fields
        if not all([operation_type, amount, account_number]):
            return Response({
                'status': 'error',
                'message': 'Type, amount, and account number are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({
                    'status': 'error',
                    'message': 'Amount must be greater than 0'
                }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({
                'status': 'error',
                'message': 'Invalid amount format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's wallet
        wallet = get_object_or_404(Wallet, user=request.user)
        
        # Check if user has sufficient balance
        if wallet.Amount < amount:
            return Response({
                'status': 'error',
                'message': 'Insufficient balance'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create operation record
        operation = OpertionMoney.objects.create(
            type=operation_type,
            Method='Withdraw',
            Amount=amount,
            MyAccount=wallet,
            Account=account_number,
            state='pending'  # Starts as pending until admin approves
        )
        
        # Temporarily deduct from wallet (will be confirmed after admin approval)
        # You might want to implement a different logic here
        
        serializer = OpertionMoneySerializer(operation)
        
        return Response({
            'status': 'success',
            'message': 'Withdrawal request submitted successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get user's operation history
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_operations(request):
    """Get all operations for the authenticated user"""
    try:
        wallet = get_object_or_404(Wallet, user=request.user)
        operations = OpertionMoney.objects.filter(MyAccount=wallet).order_by('-Date1')
        serializer = OpertionMoneySerializer(operations, many=True)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get specific operation details
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_operation_detail(request, operation_id):
    """Get details of a specific operation"""
    try:
        wallet = get_object_or_404(Wallet, user=request.user)
        operation = get_object_or_404(
            OpertionMoney, 
            id=operation_id, 
            MyAccount=wallet
        )
        serializer = OpertionMoneySerializer(operation)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Cancel pending operation
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_operation(request, operation_id):
    """Cancel a pending operation"""
    try:
        wallet = get_object_or_404(Wallet, user=request.user)
        operation = get_object_or_404(
            OpertionMoney, 
            id=operation_id, 
            MyAccount=wallet,
            state='pending'
        )
        
        operation.state = 'Failed'
        operation.Date2 = timezone.now()
        operation.save()
        
        serializer = OpertionMoneySerializer(operation)
        
        return Response({
            'status': 'success',
            'message': 'Operation cancelled successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except OpertionMoney.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Operation not found or cannot be cancelled'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Load sentiment analysis model
model_save_path = "./sentiment_model"
try:
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model=model_save_path, 
        tokenizer=model_save_path
    )
    print("✅ Sentiment model loaded successfully")
except Exception as e:
    print(f"⚠️ Error loading sentiment model: {e}")
    sentiment_pipeline = None

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def medicine_comments1(request, medicine_id):
    """
    GET: Get all comments for a specific medicine
    POST: Create a new comment for a specific medicine
    """
    # Validate UUID format
    try:
        # Check if medicine_id is a valid UUID
        uuid.UUID(medicine_id)
    except ValueError:
        return Response({
            'success': False,
            'error': 'Invalid medicine ID format'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the medicine using string ID (UUID)
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'GET':
        # Get all comments for this medicine
        comments = Comment.objects.filter(comment_medicine=medicine)
        
        # Apply filters if provided
        comment_type = request.query_params.get('type')
        if comment_type:
            comments = comments.filter(type=comment_type)
        
        # Order by newest first
        comments = comments.order_by('-created_at')
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        paginated_comments = comments[start:end]
        
        # Serialize comments
        serializer = CommentSerializer(
            paginated_comments, 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'count': comments.count(),
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Create new comment
        serializer = CreateCommentSerializer(data=request.data)
        
        if serializer.is_valid():
            text = serializer.validated_data['text']
            
            # Perform sentiment analysis
            comment_type = 'general'
            sentiment_score = None
            
            # Add your sentiment analysis logic here
            # comment_type = analyze_sentiment(text)
            
            # Create comment
            comment = Comment.objects.create(
                text=text,
                type=comment_type,
                comment_customer=request.user,
                comment_medicine=medicine
            )
            
            # Return the created comment
            response_serializer = CommentSerializer(
                comment, 
                context={'request': request}
            )
            
            return Response({
                'success': True,
                'message': 'Comment added successfully',
                'sentiment_score': sentiment_score,
                'comment': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def comment_detail(request, comment_id):
    """
    GET: Get a specific comment
    PUT: Update a comment (only by owner)
    DELETE: Delete a comment (only by owner)
    """
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check permissions
    if comment.comment_customer != request.user:
        return Response({
            'success': False,
            'error': 'You do not have permission to modify this comment'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = CommentSerializer(comment, context={'request': request})
        return Response({
            'success': True,
            'comment': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Update comment
        serializer = CreateCommentSerializer(comment, data=request.data, partial=True)
        
        if serializer.is_valid():
            text = serializer.validated_data.get('text', comment.text)
            comment.text = text
            comment.save()
            
            response_serializer = CommentSerializer(
                comment, 
                context={'request': request}
            )
            
            return Response({
                'success': True,
                'message': 'Comment updated successfully',
                'comment': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        comment.delete()
        return Response({
            'success': True,
            'message': 'Comment deleted successfully'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_comments(request):
    """
    Get all comments by the authenticated user
    """
    # Get user's comments
    comments = Comment.objects.filter(comment_customer=request.user)
    
    # Apply filters
    medicine_id = request.query_params.get('medicine_id')
    if medicine_id:
        comments = comments.filter(comment_medicine_id=medicine_id)
    
    comment_type = request.query_params.get('type')
    if comment_type:
        comments = comments.filter(type=comment_type)
    
    # Order by newest first
    comments = comments.order_by('-created_at')
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    paginated_comments = comments[start:end]
    
    # Serialize
    serializer = CommentSerializer(
        paginated_comments, 
        many=True, 
        context={'request': request}
    )
    
    return Response({
        'success': True,
        'count': comments.count(),
        'page': page,
        'page_size': page_size,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medicine_comment_stats(request, medicine_id):
    """
    Get statistics about comments for a medicine
    """
    # Validate UUID format
    try:
        uuid.UUID(medicine_id)
    except ValueError:
        return Response({
            'success': False,
            'error': 'Invalid medicine ID format'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    comments = Comment.objects.filter(comment_medicine=medicine)
    
    # Calculate statistics
    total_comments = comments.count()
    positive_count = comments.filter(type='POSITIVE').count()
    negative_count = comments.filter(type='NEGATIVE').count()
    neutral_count = comments.filter(type='NEUTRAL').count()
    general_count = comments.filter(type='general').count()
    
    return Response({
        'success': True,
        'medicine_id': medicine.id,
        'medicine_name': medicine.name,
        'statistics': {
            'total_comments': total_comments,
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'general': general_count,
            'sentiment_distribution': {
                'positive_percentage': (positive_count / total_comments * 100) if total_comments > 0 else 0,
                'negative_percentage': (negative_count / total_comments * 100) if total_comments > 0 else 0,
                'neutral_percentage': (neutral_count / total_comments * 100) if total_comments > 0 else 0,
            }
        }
    }, status=status.HTTP_200_OK)



@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def customer_address_list_create(request):
    """List all addresses for current user or create a new address"""
    
    if request.method == 'GET':
        # Get all addresses for the current user
        addresses = CustomerAddress.objects.filter(
            user=request.user
        ).order_by('-is_default', '-created_at' if hasattr(CustomerAddress, 'created_at') else 'id')
        
        serializer = CustomerAddressSerializer(addresses, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'count': addresses.count(),
            'addresses': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Create a new address
        serializer = CreateUpdateCustomerAddressSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        address = serializer.save()
        
        # Return full address details
        response_serializer = CustomerAddressSerializer(address, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Address created successfully',
            'address': response_serializer.data
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def customer_address_detail(request, id):
    """Retrieve, update, or delete a specific address"""
    
    # Get the address and ensure it belongs to the current user
    address = get_object_or_404(CustomerAddress, id=id, user=request.user)
    
    if request.method == 'GET':
        # Retrieve address
        serializer = CustomerAddressSerializer(address, context={'request': request})
        
        return Response({
            'success': True,
            'address': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        # Update address
        partial = request.method == 'PATCH'
        serializer = CreateUpdateCustomerAddressSerializer(
            address, 
            data=request.data, 
            partial=partial,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_address = serializer.save()
        response_serializer = CustomerAddressSerializer(updated_address, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Address updated successfully',
            'address': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        # Delete address
        was_default = address.is_default
        
        address.delete()
        
        # If deleted address was default, set another address as default if available
        if was_default:
            next_address = CustomerAddress.objects.filter(user=request.user).first()
            if next_address:
                next_address.is_default = True
                next_address.save()
        
        return Response({
            'success': True,
            'message': 'Address deleted successfully'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])

@permission_classes([IsAuthenticated])

def set_default_address(request, address_id):
    """Set a specific address as default"""
    
    # Get the address and ensure it belongs to the current user
    address = get_object_or_404(CustomerAddress, id=address_id, user=request.user)
    
    # Clear all default addresses for this user
    CustomerAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set this address as default
    address.is_default = True
    address.save()
    
    serializer = CustomerAddressSerializer(address, context={'request': request})
    
    return Response({
        'success': True,
        'message': 'Default address set successfully',
        'address': serializer.data
    }, status=status.HTTP_200_OK)
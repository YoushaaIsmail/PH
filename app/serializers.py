# serializers.py
from rest_framework import serializers
from .models import *

# class DriverLocationSerializer(serializers.ModelSerializer):
#     """Serializer for driver location history (optional)"""
#     class Meta:
#         model = DriverLocationHistory
#         fields = ['longitude', 'latitude', 'timestamp']

class DriverSimpleSerializer(serializers.ModelSerializer):
    """Simplified driver info"""
    username = serializers.CharField(source='user.username')
    full_name = serializers.CharField(source='user.get_full_name')
    
    class Meta:
        model = driver
        fields = ['id', 'username', 'full_name', 'vehicle_type', 'license_plate']

class OrderTrackingSerializer(serializers.ModelSerializer):
    """Main serializer for order tracking - PATIENT VIEW"""
    driver_info = DriverSimpleSerializer(source='his_driver', read_only=True)
    driver_location = serializers.SerializerMethodField()
    customer_address = serializers.SerializerMethodField()
    order_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'placed_at',
            'scheduled_for',
            'delivery_fee',
            'driver_info',
            'driver_location',
            'customer_address',
            'order_items',
            'can_cancel',
            'can_pay'
        ]
    
    def get_driver_location(self, obj):
        """Get driver's current location if driver is assigned"""
        if obj.his_driver:
            driver = obj.his_driver
            if driver.current_longitude and driver.current_latitude:
                return {
                    'longitude': driver.current_longitude,
                    'latitude': driver.current_latitude,
                    'last_updated': driver.last_online
                }
        return None
    
    def get_customer_address(self, obj):
        """Get customer address details"""
        if obj.address:
            return {
                'street': obj.address.street_address,
                'city': obj.address.city,
                'x': obj.address.x,  # Longitude
                'y': obj.address.y   # Latitude
            }
        return None
    
    def get_order_items(self, obj):
        """Get items in the order"""
        # You'll need to adjust this based on your OrderItem model
        items = []
        if hasattr(obj, 'items'):
            for item in obj.items.all():
                items.append({
                    'name': item.product.name if hasattr(item, 'product') else 'Item',
                    'quantity': item.quantity,
                    'price': item.price
                })
        return items

from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ActiveIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveIngredient
        fields = ['id', 'name']


class MedicineSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    active_ingredients = ActiveIngredientSerializer(many=True, read_only=True)
    total_quantity = serializers.ReadOnlyField()
    nearest_expiration_date = serializers.ReadOnlyField()

    class Meta:
        model = Medicine
        fields = '__all__'

# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Comment, Medicine

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'photo')
        read_only_fields = ('id',)

class CommentSerializer(serializers.ModelSerializer):
    # Don't use nested serializer directly - use SerializerMethodField for better control
    customer_details = serializers.SerializerMethodField()
    customer_photo = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 
            'text', 
            'type', 
            'comment_customer',
            'customer_details',
            'customer_name', 
            'customer_photo',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'type']
    
    def get_customer_details(self, obj):
        """Get full customer details"""
        if obj.comment_customer:
            return {
                'id': obj.comment_customer.id,
                'username': obj.comment_customer.username,
                'email': obj.comment_customer.email,
                'first_name': obj.comment_customer.first_name,
                'last_name': obj.comment_customer.last_name,
                'photo': self.get_customer_photo(obj)
            }
        return None
    
    def get_customer_name(self, obj):
        """Get customer full name or username"""
        if not obj.comment_customer:
            return None
            
        if obj.comment_customer.first_name and obj.comment_customer.last_name:
            return f"{obj.comment_customer.first_name} {obj.comment_customer.last_name}"
        elif obj.comment_customer.first_name:
            return obj.comment_customer.first_name
        elif obj.comment_customer.last_name:
            return obj.comment_customer.last_name
        return obj.comment_customer.username
    
    def get_customer_photo(self, obj):
        """Get customer photo URL"""
        if obj.comment_customer and obj.comment_customer.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.comment_customer.photo.url)
            return obj.comment_customer.photo.url
        return None

# serializers.py
from rest_framework import serializers
from .models import Comment
from transformers import pipeline

# Load the model once at module level
model_save_path = "./sentiment_model"
sentiment_pipeline = pipeline("sentiment-analysis", model=model_save_path, tokenizer=model_save_path)

class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'type']
        read_only_fields = ['type']  # Type will be auto-generated
    
    def validate_text(self, value):
        """Auto-analyze sentiment when text is provided"""
        if value:
            try:
                # Run sentiment analysis
                result = sentiment_pipeline(value)[0]
                # Set the type in the validated data
                self.context['auto_type'] = result['label']
            except Exception as e:
                # Fallback to 'general' if analysis fails
                self.context['auto_type'] = 'GENERAL'
        return value
    
    def create(self, validated_data):
        """Override create to add the auto-analyzed type"""
        auto_type = self.context.get('auto_type', 'GENERAL')
        validated_data['type'] = auto_type
        return super().create(validated_data)


class WalletSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['id', 'username', 'Amount', 'user']
        read_only_fields = ['id', 'username', 'user']


class OpertionMoneySerializer(serializers.ModelSerializer):
    wallet_balance = serializers.SerializerMethodField()
    formatted_date1 = serializers.DateTimeField(source='Date1', format='%Y-%m-%d %H:%M:%S', read_only=True)
    formatted_date2 = serializers.DateTimeField(source='Date2', format='%Y-%m-%d %H:%M:%S', read_only=True)
    
    class Meta:
        model = OpertionMoney
        fields = [
            'id', 'type', 'Method', 'Amount', 'code', 'image',
            'Date1', 'Date2', 'MyAccount', 'state', 'Account',
            'wallet_balance', 'formatted_date1', 'formatted_date2'
        ]
        read_only_fields = ['id', 'Date1', 'Date2', 'state']
    
    def get_wallet_balance(self, obj):
        return obj.MyAccount.Amount
    
    def validate_Amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 
            'user', 
            'label', 
            'address_line', 
            'city', 
            'postal_code', 
            'phone', 
            'is_default', 
            'x', 
            'y'
        ]
        read_only_fields = ['id', 'user']
    
    def validate(self, data):
        """Validate that only one address is set as default per user"""
        if data.get('is_default'):
            # If setting this address as default, check if user already has a default
            user = self.context['request'].user
            if CustomerAddress.objects.filter(user=user, is_default=True).exists():
                # Option 1: Clear other default addresses
                CustomerAddress.objects.filter(user=user, is_default=True).update(is_default=False)
                # Option 2: Raise error
                # raise serializers.ValidationError(
                #     {"is_default": "User already has a default address"}
                # )
        return data

class CreateUpdateCustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            'label', 
            'address_line', 
            'city', 
            'postal_code', 
            'phone', 
            'is_default', 
            'x', 
            'y'
        ]
    
    def validate(self, data):
        """Validate address data"""
        # Validate coordinates
        if 'x' in data and 'y' in data:
            if not (-90 <= data['y'] <= 90):
                raise serializers.ValidationError(
                    {"y": "Latitude must be between -90 and 90"}
                )
            if not (-180 <= data['x'] <= 180):
                raise serializers.ValidationError(
                    {"x": "Longitude must be between -180 and 180"}
                )
        
        # Validate postal code format (example for Netherlands)
        if data.get('postal_code'):
            import re
            # Example: 1234 AB format
            if not re.match(r'^[0-9]{4}\s?[A-Z]{2}$', data['postal_code']):
                # Remove this validation if not needed
                pass
        
        return data
    
    def create(self, validated_data):
        """Create address with user from request"""
        user = self.context['request'].user
        
        # If setting as default, clear other defaults
        if validated_data.get('is_default'):
            CustomerAddress.objects.filter(user=user, is_default=True).update(is_default=False)
        
        return CustomerAddress.objects.create(user=user, **validated_data)
    
    def update(self, instance, validated_data):
        """Update address instance"""
        user = self.context['request'].user
        
        # If setting as default, clear other defaults
        if validated_data.get('is_default'):
            CustomerAddress.objects.filter(user=user, is_default=True).exclude(id=instance.id).update(is_default=False)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

# In your models.py, update the driver model
class driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driver_profile')
    is_active = models.BooleanField(default=True)
    current_x = models.FloatField(null=True, blank=True)
    current_y = models.FloatField(null=True, blank=True)
    vehicle_type = models.CharField(max_length=100, blank=True)
    license_plate = models.CharField(max_length=20, blank=True)
    last_online = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Driver"

class Category(models.Model):
    """تصنيف الدواء (أمراض القلب، الحساسية، الأطفال، ...)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class ActiveIngredient(models.Model):
    """المادة الفعالة — يبحث المستخدمون عنها أيضاً."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Medicine(models.Model):
    """موديل الدواء مع البيانات التفصيلية والبحث بالمادة الفعالة."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    brand = models.CharField(max_length=120, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='medicines')
    active_ingredients = models.ManyToManyField('ActiveIngredient', related_name='medicines', blank=True)
    form = models.CharField(max_length=80, blank=True)  # tablet, syrup, injection ...
    strength = models.CharField(max_length=80, blank=True)  # e.g., 500mg
    dosage = models.TextField(blank=True)
    warnings = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    barcode = models.CharField(max_length=120, blank=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    prescription_required = models.BooleanField(default=False)
    image = models.ImageField(upload_to='medicines/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    Addpiont=models.IntegerField()

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['barcode'])
        ]

    def __str__(self):
        return f"{self.name} {self.strength or ''}".strip()

    @property
    def total_quantity(self):
        """إرجاع الكمية الإجمالية من جميع الدفعات غير المنتهية الصلاحية"""
        total = 0
        for batch in self.batches.filter(expiration_date__gte=timezone.now().date()):
            total += batch.quantity
        return total

    def is_available(self, needed=1):
        """Returns True if there's enough stock from non-expired batches."""
        return self.total_quantity >= needed

    @property
    def needs_reorder(self):
        """تحقق إذا كان الدواء يحتاج إلى إعادة طلب"""
        return self.total_quantity <= self.low_stock_threshold

    @property
    def nearest_expiration_date(self):
        """أقرب تاريخ انتهاء صلاحية من الدفعات"""
        active_batches = self.batches.filter(
            expiration_date__gte=timezone.now().date(),
            quantity__gt=0
        ).order_by('expiration_date').first()
        
        return active_batches.expiration_date if active_batches else None

    @property
    def is_expired(self):
        """تحقق إذا انتهت صلاحية جميع الدفعات"""
        return self.total_quantity == 0 and self.batches.exists()


class BatchMed(models.Model):
    """موديل دفعات الأدوية مع معلومات الصلاحية والكمية"""
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100, blank=True)  # رقم الدفعة
    quantity = models.PositiveIntegerField(default=0)
    expiration_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # سعر الشراء
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['expiration_date']  # ترتيب حسب تاريخ الصلاحية
        verbose_name = 'Batch Medicine'
        verbose_name_plural = 'Batch Medicines'

    def __str__(self):
        return f"{self.medicine.name} - Batch: {self.batch_number} - Qty: {self.quantity}"

    def is_available(self, needed=1):
        """Returns True if this batch has enough stock and not expired."""
        if self.expiration_date and self.expiration_date < timezone.now().date():
            return False
        return self.quantity >= needed

    @property
    def is_expired(self):
        """تحقق إذا انتهت صلاحية الدفعة"""
        if self.expiration_date:
            return self.expiration_date < timezone.now().date()
        return False

    @property
    def days_until_expiration(self):
        """عدد الأيام المتبقية حتى انتهاء الصلاحية"""
        if self.expiration_date:
            delta = self.expiration_date - timezone.now().date()
            return delta.days
        return None


class Prescription(models.Model):
    """وصفة طبية رقمية — صورة أو PDF مرفوعة من المستخدم.
    يتم الربط مع Order عند إنشاء طلب يحتوي على أصناف من الوصفة.
    """


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    uploaded_file = models.FileField(upload_to='prescriptions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_prescriptions')
    note = models.TextField(blank=True)

    def __str__(self):
        return f"Prescription {self.id} - {self.patient} "


class CustomerAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=80, blank=True)
    address_line = models.TextField()
    city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    is_default = models.BooleanField(default=False)
    x=models.FloatField()
    y=models.FloatField()

    def __str__(self):
        return f"{self.user} - {self.label or self.city}"

import requests
from decimal import Decimal
class Order(models.Model):
    """نظام سلة شراء وطلب مع خيارات الدفع والتسليم."""
    STATUS = (
        ('draft', 'Draft'),
        ('placed', 'Placed'),
        ('processing', 'Processing'),
        ('ready', 'Ready for pickup'),
        ('delivering', 'Out for delivery'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    prescription = models.ManyToManyField(Prescription, related_name='order_prescription', blank=True)
    address = models.ForeignKey(CustomerAddress, on_delete=models.SET_NULL, null=True, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS, default='draft')
    payment_delivery = models.BooleanField(default=False)
    # price_delivery = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field to store calculated delivery fee
    his_driver=models.ForeignKey(driver, on_delete=models.SET_NULL, null=True, related_name='Order_driver')
    class Meta:
        ordering = ['-placed_at']

    def __str__(self):
        return f"Order {self.id} - {self.user} - {self.status}"

    @property
    def total_amount(self):
        total = sum(item.line_total() for item in self.items.all())
        return total

    @property
    def item_count(self):
        """Return total number of items in order"""
        return sum(item.quantity for item in self.items.all())

    @property
    def can_edit(self):
        """Check if order can be edited (only draft and placed orders)"""
        return self.status in ['draft', 'placed']

    @property
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in ['draft', 'placed', 'processing']

    @property
    def can_pay(self):
        """Check if order can be paid"""
        return self.status in ['draft', 'placed']

    def get_status_badge_class(self):
        """Return Bootstrap badge class for status"""
        status_classes = {
            'draft': 'bg-secondary',
            'placed': 'bg-primary',
            'processing': 'bg-warning',
            'ready': 'bg-info',
            'delivering': 'bg-primary',
            'completed': 'bg-success',
            'cancelled': 'bg-danger',
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    
    def calculate_delivery_fee(self, selected_address):
        """Calculate delivery fee based on distance"""
        try:
            about = About.objects.first()
            if not about:
                return 0.00
            
            # Calculate distance using TomTom API
            url = f"https://api.tomtom.com/routing/1/calculateRoute/{about.loction_x},{about.loction_y}:{selected_address.x},{selected_address.y}/json?key=wncqPXyuwK1DoGAegYSHAJ5SyE3ATzh7"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('routes'):
                    # Get distance in kilometers
                    distance_km = data['routes'][0]['summary']['lengthInMeters'] / 1000
                    
                    if distance_km <= about.maxDelKM:
                        delivery_fee = distance_km * float(about.priceforKM)
                        return Decimal(delivery_fee)
                    else:
                        return None  # Out of delivery range
            return 0.00
        except Exception:
            return 0.00

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.medicine} x {self.quantity}"

    def line_total(self):
        return self.medicine.price * self.quantity

    def can_edit(self):
        """Check if order item can be edited"""
        return self.order.can_edit

class LoyaltyAccount(models.Model):
    """نقاط الولاء المرتبطة بالمستخدم."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loyalty')
    points = models.PositiveIntegerField(default=0)

    def add_points(self, pts: int):
        self.points += pts
        self.save()

    def redeem_points(self, pts: int):
        if pts > self.points:
            raise ValueError('Not enough points')
        self.points -= pts
        self.save()

    def __str__(self):
        return f"{self.user} - {self.points} pts"


class Notification(models.Model):
    """تنبيهات للمستخدم أو للصيدلي (نفاد المخزون، عروض، ...)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.user}: {self.title}"


# تقارير ومؤشرات بيانية — سجلات المبيعات لاستخراج تقارير لاحقاً
class SalesRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    sold_at = models.DateTimeField(default=timezone.now)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['sold_at']), models.Index(fields=['medicine'])]

    def __str__(self):
        return f"Sale {self.medicine} x {self.quantity} @ {self.sold_at}"


class About(models.Model):
    facebook=models.CharField(max_length=30)
    instgram=models.CharField(max_length=30)
    phone=models.CharField(max_length=10)
    MTNAccount=models.CharField(max_length=15)
    SyriaAccount=models.CharField(max_length=15)
    maxDelKM=models.IntegerField()
    priceforKM=models.DecimalField(max_digits=10, decimal_places=2)
    loction_x=models.FloatField()
    loction_y=models.FloatField()


# models.py
from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    Amount = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"{self.user.username}'s Wallet - ${self.Amount}"

class OpertionMoney(models.Model):
    TYPE_CHOICES = (
        ('Syriatel', 'Syriatel'),
        ('MTN', 'MTN'),
       
    )
    
    METHOD_CHOICES = (
        ('Add', 'Add'),
        ('Withdraw', 'Withdraw'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    )
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    Method = models.CharField(max_length=20, choices=METHOD_CHOICES)    
    Amount = models.FloatField()
    code = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='money_images/', blank=True, null=True)
    Date1 = models.DateTimeField(auto_now_add=True)
    Date2 = models.DateTimeField(null=True, blank=True)
    MyAccount = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='operations')
    state = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    Account=models.CharField(max_length=15,null=True)
    
    def __str__(self):
        return f"{self.Method} - ${self.Amount} - {self.state}"
    
class Comment(models.Model):
    text = models.TextField()
    type = models.CharField(max_length=15, default='general')
    comment_customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, name="comment_customer")
    Medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, name="comment_medicine")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.comment_customer}"



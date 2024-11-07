from django.contrib.sitemaps.views import index
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone

class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, username, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not username:
            raise ValueError('User must have an username address.')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password):
        """Create and return a new superuser."""
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        user.role = 'admin'

        return user

class Position(models.Model):
    class Meta:
        verbose_name = 'Лавозим'
        verbose_name_plural = "Лавозимлар"
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Лавозим номи")

    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Фойдаланувчи'
        verbose_name_plural = "Фойдаланувчилар"

    """User in the system."""
    ROLE_CHOICES = (
        ('admin', 'СуперАдмин'),
        ('region_admin', 'Вилоят Админи'),
        ('mosque_admin', 'Масжид Админи'),
    )
    role = models.CharField(max_length=20, null = True, blank=True, default = 'mosque_admin', choices = ROLE_CHOICES)
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    place = models.ForeignKey('Place', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Жой")
    objects = UserManager()
    USERNAME_FIELD = 'username'
    objective_file = models.FileField(upload_to='files/objectives', verbose_name="Объективка", null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Лавозими")

    def __str__(self):
        return f"{self.username} - {self.name}"

class ActivityLog(models.Model):
    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = "Логлар"

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the log is created
    object_id = models.PositiveIntegerField(null=True, blank=True)  # ID of the affected object, if applicable
    object_type = models.CharField(max_length=100, null=True, blank=True)  # The model name or type of the affected object
    description = models.TextField(null=True, blank=True)  # Optional details about the activity
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Store the user's IP address if necessary

    def __str__(self):
        return f'{self.user} - {self.action} at {self.timestamp}'

class AuditableModel(models.Model):
    """Common auditable model"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        related_name='created_%(class)s_set',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    updated_by = models.ForeignKey(
        User, 
        related_name='updated_%(class)s_set',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    def save(self, *args, **kwargs):
        # Check if the object is being created or updated
        if self.pk is None:
            action = 'create'
        else:
            action = 'update'

        # Save the object
        request = kwargs.pop('request', None)
        user = None
        remote_addr = None
        if request:
            user = request.user
            if action == 'create':
                self.created_by = user
            else:
                self.updated_by = user
            remote_addr = request.META.get('REMOTE_ADDR')

        super().save(*args, **kwargs)
        # Log the action
        ActivityLog.objects.create(
            user=user,  # Pass request from view
            action=action,
            object_id=self.pk,
            object_type=self.__class__.__name__,
            description=f'{self.__class__.__name__} {action}',
            ip_address=remote_addr
        )

    def delete(self, *args, **kwargs):
        request = kwargs.pop('request', None)

        user = None
        remote_addr = None
        if request:
            user = request.user
            remote_addr = request.META.get('REMOTE_ADDR')
        # Log the delete action
        ActivityLog.objects.create(
            user=user,  # Pass request from view
            action='delete',
            object_id=self.pk,
            object_type=self.__class__.__name__,
            description=f'{self.__class__.__name__} deleted',
            ip_address=remote_addr
        )
        # Delete the object
        super().delete(*args, **kwargs)

    class Meta:
        abstract = True

class Unit(models.Model):
    class Meta:
        verbose_name = 'Улчов бирлиги'
        verbose_name_plural = "Улчов бирликлари"
    """Unit for category"""
    name = models.CharField(max_length=50, verbose_name="Номи")

    def __str__(self):
        return self.name

class Category(models.Model):

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Категориялар"
        indexes = [
            models.Index(fields=['name'])
        ]

    """The Category"""
    class OperationType(models.TextChoices):
        """Type of category: income or expense"""
        INCOME = 'income', 'Кирим'
        EXPENSE = 'expense', 'Чиким'

    name = models.CharField(max_length=255, verbose_name="Номи")
    operation_type = models.CharField(
        max_length = 10,
        choices = OperationType.choices,
        default = OperationType.EXPENSE,
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, default=None, blank=True, verbose_name="Улчов бирлиги")
    percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None, verbose_name="Процент")
    is_communal = models.BooleanField(default=False, verbose_name="Коммунал")

    def __str__(self):
        return self.name

class Place(AuditableModel):
    class Meta:
        verbose_name = 'Жой'
        verbose_name_plural = "Жойлар"
        indexes = [
            models.Index(fields=['name', 'inn'])
        ]
    """It can be Region, City or Mosque"""
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Номи")
    inn = models.CharField(max_length=255, null=False, blank=True, default='', verbose_name="ИНН")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Тегишли")
    is_mosque = models.BooleanField(null=False, default=False, verbose_name="Масжид")
    employee_count = models.IntegerField(null=False, default=0, verbose_name="Ишчилар сони")

    def __str__(self):
        return f"{self.name}, ({ self.inn or 'No Inn' })"

class Record(AuditableModel):
    class Meta:
        verbose_name = 'Кирим/Чиким'
        verbose_name_plural = "Киримлар/Чикимлар"
        ordering = ['-created_at']

    """Main document for accounting expenses and incomes"""
    date = models.DateField(null=True, blank=True, default=timezone.now(), verbose_name="Вакти")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0, verbose_name="Сумма")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Микдор")
    description = models.CharField(max_length=500, null=True, blank=True, verbose_name="Изох")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Жой")

    def __str__(self):
        return f"{self.place}, {self.category}, {self.amount}, {self.description}"



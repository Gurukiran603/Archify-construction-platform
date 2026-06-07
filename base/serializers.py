from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from .models import (
    User, ProfessionalProfile, ClientProfile, ProjectCategory,
    ConstructionProject, BuildingPlan, ProjectMilestone, SiteUpdate,
    SiteUpdateImage, CCTVCamera, Worker, ProjectWorker, WorkerAttendance,
    WagePayment, Material, ProjectMaterial, ConsultationRequest,
    Conversation, Message, ProjectReview, PortfolioProject, PortfolioImage,
    Notification, ActivityLog
)

User = get_user_model()


# ========== User & Profile Serializers ==========

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'profile_image', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['id', 'is_verified', 'date_joined']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number', 'role']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfessionalProfileSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = ProfessionalProfile
        fields = [
            'id', 'user', 'user_detail', 'firm_name', 'license_number',
            'specialization', 'experience_years', 'bio', 'service_locations',
            'consultation_fee', 'verification_status', 'average_rating',
            'total_projects', 'created_at'
        ]
        read_only_fields = ['id', 'verification_status', 'average_rating', 'total_projects', 'created_at']


class ClientProfileSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = ClientProfile
        fields = ['id', 'user', 'user_detail', 'address', 'city', 'state', 'preferred_project_type']


# ========== Project Serializers ==========

class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ['id', 'name', 'slug', 'description']
        lookup_field = 'slug'


class ConstructionProjectListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    progress_percent = serializers.IntegerField()
    
    class Meta:
        model = ConstructionProject
        fields = [
            'id', 'title', 'slug', 'client_name', 'category_name',
            'estimated_budget', 'status', 'progress_percent', 'created_at'
        ]


class ConstructionProjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested relationships"""
    client_detail = UserSerializer(source='client', read_only=True)
    architect_detail = UserSerializer(source='architect', read_only=True)
    civil_engineer_detail = UserSerializer(source='civil_engineer', read_only=True)
    contractor_detail = UserSerializer(source='contractor', read_only=True)
    category_detail = ProjectCategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = ConstructionProject
        fields = [
            'id', 'client', 'client_detail', 'architect', 'architect_detail',
            'civil_engineer', 'civil_engineer_detail', 'contractor', 'contractor_detail',
            'category', 'category_detail', 'title', 'slug', 'description',
            'site_address', 'city', 'state', 'plot_area_sqft', 'estimated_budget',
            'actual_cost', 'start_date', 'expected_completion_date', 'completed_at',
            'status', 'progress_percent', 'is_public_portfolio', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'actual_cost', 'completed_at', 'created_at', 'updated_at']


class ConstructionProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstructionProject
        fields = [
            'client', 'architect', 'civil_engineer', 'contractor', 'category',
            'title', 'description', 'site_address', 'city', 'state',
            'plot_area_sqft', 'estimated_budget', 'start_date',
            'expected_completion_date', 'is_public_portfolio'
        ]
    
    def validate(self, data):
        start_date = data.get('start_date')
        expected_completion_date = data.get('expected_completion_date')
        
        if start_date and expected_completion_date and expected_completion_date < start_date:
            raise serializers.ValidationError({
                "expected_completion_date": "Expected completion date cannot be before start date."
            })
        return data
    
    def create(self, validated_data):
        # Auto-generate slug from title
        from django.utils.text import slugify
        title = validated_data.get('title')
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while ConstructionProject.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        validated_data['slug'] = slug
        return super().create(validated_data)


# ========== Building Plan Serializers ==========

class BuildingPlanSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = BuildingPlan
        fields = [
            'id', 'project', 'project_title', 'uploaded_by', 'uploaded_by_name',
            'plan_type', 'title', 'file', 'version', 'approval_status',
            'client_notes', 'professional_notes', 'approved_at', 'created_at'
        ]
        read_only_fields = ['id', 'version', 'approved_at', 'created_at']


class BuildingPlanApprovalSerializer(serializers.ModelSerializer):
    """Serializer for approving/rejecting plans"""
    
    class Meta:
        model = BuildingPlan
        fields = ['approval_status', 'professional_notes']
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if instance.approval_status == 'APPROVED':
            instance.approved_at = timezone.now()
            instance.save()
        return instance


# ========== Milestone & Site Update Serializers ==========

class ProjectMilestoneSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectMilestone
        fields = [
            'id', 'project', 'title', 'description', 'planned_start_date',
            'planned_end_date', 'actual_start_date', 'actual_end_date',
            'progress_percent', 'is_completed', 'display_order', 'is_overdue'
        ]
    
    def get_is_overdue(self, obj):
        if not obj.is_completed and obj.planned_end_date:
            return obj.planned_end_date < timezone.now().date()
        return False


class SiteUpdateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteUpdateImage
        fields = ['id', 'image', 'caption', 'created_at']


class SiteUpdateSerializer(serializers.ModelSerializer):
    images = SiteUpdateImageSerializer(many=True, read_only=True)
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    milestone_title = serializers.CharField(source='milestone.title', read_only=True)
    
    class Meta:
        model = SiteUpdate
        fields = [
            'id', 'project', 'milestone', 'milestone_title', 'posted_by',
            'posted_by_name', 'title', 'description', 'progress_percent',
            'update_date', 'weather_note', 'is_visible_to_client', 'images', 'created_at'
        ]


class SiteUpdateCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = SiteUpdate
        fields = [
            'project', 'milestone', 'title', 'description',
            'progress_percent', 'weather_note', 'is_visible_to_client', 'images'
        ]
    
    def create(self, validated_data):
        images = validated_data.pop('images', [])
        site_update = SiteUpdate.objects.create(**validated_data)
        
        for image in images:
            SiteUpdateImage.objects.create(site_update=site_update, image=image)
        
        return site_update


# ========== CCTV Serializers ==========

class CCTVCameraSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CCTVCamera
        fields = [
            'id', 'project', 'project_title', 'name', 'location_note',
            'stream_url', 'snapshot_image', 'status', 'status_display',
            'last_checked_at', 'created_at'
        ]
        read_only_fields = ['id', 'last_checked_at', 'created_at']


# ========== Worker Serializers ==========

class WorkerSerializer(serializers.ModelSerializer):
    worker_type_display = serializers.CharField(source='get_worker_type_display', read_only=True)
    user_detail = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Worker
        fields = [
            'id', 'user', 'user_detail', 'full_name', 'phone_number',
            'worker_type', 'worker_type_display', 'daily_wage', 'address',
            'id_proof', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectWorkerSerializer(serializers.ModelSerializer):
    worker_detail = WorkerSerializer(source='worker', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = ProjectWorker
        fields = [
            'id', 'project', 'project_title', 'worker', 'worker_detail',
            'assigned_by', 'assigned_by_name', 'start_date', 'end_date',
            'custom_daily_wage', 'is_active', 'created_at'
        ]


class WorkerAttendanceSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='project_worker.worker.full_name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WorkerAttendance
        fields = [
            'id', 'project_worker', 'worker_name', 'attendance_date',
            'status', 'status_display', 'check_in_time', 'check_out_time',
            'marked_by', 'marked_by_name', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BulkAttendanceSerializer(serializers.Serializer):
    attendance_date = serializers.DateField()
    attendance_data = serializers.ListField(
        child=serializers.DictField()
    )
    
    def validate_attendance_data(self, value):
        for item in value:
            if 'project_worker_id' not in item or 'status' not in item:
                raise serializers.ValidationError(
                    "Each attendance entry must have 'project_worker_id' and 'status'"
                )
        return value


class WagePaymentSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source='project_worker.worker.full_name', read_only=True)
    project_title = serializers.CharField(source='project_worker.project.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    remaining_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = WagePayment
        fields = [
            'id', 'project_worker', 'worker_name', 'project_title',
            'period_start', 'period_end', 'total_days', 'wage_per_day',
            'total_amount', 'paid_amount', 'remaining_amount', 'status',
            'status_display', 'paid_at', 'payment_reference', 'created_at'
        ]
        read_only_fields = ['id', 'total_amount', 'status', 'paid_at', 'created_at']
    
    def get_remaining_amount(self, obj):
        return obj.total_amount - obj.paid_amount


# ========== Material Serializers ==========

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'unit', 'description']


class ProjectMaterialSerializer(serializers.ModelSerializer):
    material_detail = MaterialSerializer(source='material', read_only=True)
    material_name = serializers.CharField(source='material.name', read_only=True)
    estimated_cost = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    
    class Meta:
        model = ProjectMaterial
        fields = [
            'id', 'project', 'material', 'material_detail', 'material_name',
            'quantity_required', 'quantity_used', 'unit_cost', 'estimated_cost'
        ]


# ========== Consultation Serializers ==========

class ConsultationRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    professional_name = serializers.CharField(source='professional.get_full_name', read_only=True)
    category_name = serializers.CharField(source='project_category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
   
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active')
    list_filter = ('role', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'profile_image', 'is_verified')}),
    )

@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'firm_name', 'license_number', 'verification_status', 'average_rating')
    list_filter = ('verification_status',)
    search_fields = ('user__username', 'firm_name', 'license_number')

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state')
    search_fields = ('user__username', 'city')

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ConstructionProject)
class ConstructionProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'architect', 'civil_engineer', 'contractor', 'status', 'progress_percent')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'site_address')
    readonly_fields = ('slug', 'created_at', 'updated_at')

@admin.register(BuildingPlan)
class BuildingPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'plan_type', 'version', 'approval_status')
    list_filter = ('plan_type', 'approval_status')

@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'planned_end_date', 'is_completed')
    list_filter = ('is_completed',)

@admin.register(SiteUpdate)
class SiteUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'update_date', 'is_visible_to_client')
    list_filter = ('is_visible_to_client', 'update_date')

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'worker_type', 'daily_wage', 'is_active')
    list_filter = ('worker_type', 'is_active')
    search_fields = ('full_name', 'phone_number')

@admin.register(ProjectWorker)
class ProjectWorkerAdmin(admin.ModelAdmin):
    list_display = ('worker', 'project', 'start_date', 'is_active')
    list_filter = ('is_active',)

@admin.register(WorkerAttendance)
class WorkerAttendanceAdmin(admin.ModelAdmin):
    list_display = ('project_worker', 'attendance_date', 'status')
    list_filter = ('status', 'attendance_date')

@admin.register(WagePayment)
class WagePaymentAdmin(admin.ModelAdmin):
    list_display = ('project_worker', 'period_start', 'period_end', 'total_amount', 'status')
    list_filter = ('status',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)

@admin.register(ProjectMaterial)
class ProjectMaterialAdmin(admin.ModelAdmin):
    list_display = ('project', 'material', 'quantity_required', 'unit_cost')

@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('client', 'professional', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read')
    list_filter = ('notification_type', 'is_read')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'object_type', 'created_at')
    list_filter = ('action', 'created_at')
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from .models import (
    User, ProfessionalProfile, ClientProfile, ProjectCategory,
    ConstructionProject, BuildingPlan, ProjectMilestone, SiteUpdate,
    SiteUpdateImage, CCTVCamera, Worker, ProjectWorker, WorkerAttendance,
    WagePayment, Material, ProjectMaterial, ConsultationRequest,
    Conversation, Message, ProjectReview, PortfolioProject, PortfolioImage,
    Notification
)


# ========== User & Profile Forms ==========

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'role']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }


class ProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = ProfessionalProfile
        fields = [
            'firm_name', 'license_number', 'specialization', 'experience_years',
            'bio', 'service_locations', 'consultation_fee'
        ]
        widgets = {
            'firm_name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'service_locations': forms.Textarea(attrs={'class': 'form-control', 'help_text': 'Enter locations as JSON array or comma-separated'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean_consultation_fee(self):
        fee = self.cleaned_data.get('consultation_fee')
        if fee and fee < 0:
            raise ValidationError('Consultation fee cannot be negative.')
        return fee


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ['address', 'city', 'state', 'preferred_project_type']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_project_type': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ========== Project Forms ==========

class ProjectCategoryForm(forms.ModelForm):
    class Meta:
        model = ProjectCategory
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ConstructionProjectForm(forms.ModelForm):
    class Meta:
        model = ConstructionProject
        fields = [
            'client', 'architect', 'civil_engineer', 'contractor',
            'category', 'title', 'description', 'site_address',
            'city', 'state', 'plot_area_sqft', 'estimated_budget',
            'start_date', 'expected_completion_date', 'is_public_portfolio'
        ]
        # Note: 'slug' is NOT in fields - it will be auto-generated
        # Note: 'status' is NOT in create form - will be set to ENQUIRY by default
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your project requirements'}),
            'site_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Full site address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City name'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State name'}),
            'plot_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Area in square feet'}),
            'estimated_budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Estimated budget in INR'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_public_portfolio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ConstructionProjectStatusForm(forms.ModelForm):
    """Form for updating just the status and progress of a project"""
    
    class Meta:
        model = ConstructionProject
        fields = ['status', 'progress_percent']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'progress_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }


# ========== Building Plan Forms ==========
class BuildingPlanForm(forms.ModelForm):
    class Meta:
        model = BuildingPlan
        fields = ['plan_type', 'title', 'file', 'client_notes']
        widgets = {
            'plan_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter plan title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'client_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add notes...'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show plan types that exist in the model
        if user and user.role == 'ARCHITECT':
            self.fields['plan_type'].choices = [
                ('FLOOR_PLAN', '🏠 Floor Plan'),
                ('ELEVATION', '🏢 Elevation'),
                ('INTERIOR', '🛋️ Interior Design'),
            ]
        elif user and user.role == 'CIVIL_ENGINEER':
            self.fields['plan_type'].choices = [
                ('STRUCTURAL', '🏗️ Structural Plan'),
                ('FOUNDATION', '📐 Foundation Plan'),
            ]
        elif user and user.role == 'CONTRACTOR':
            self.fields['plan_type'].choices = [
                ('SITE_PLAN', '📍 Site Plan'),
                ('ESTIMATE', '💰 Cost Estimate'),
            ]
        else:
            # Only use choices that exist in the model
            existing_choices = [('FLOOR_PLAN', 'Floor Plan'), ('ELEVATION', 'Elevation'), ('STRUCTURAL', 'Structural')]
            self.fields['plan_type'].choices = existing_choices

class BuildingPlanApprovalForm(forms.ModelForm):
    """Form for professionals to approve/reject building plans"""
    
    class Meta:
        model = BuildingPlan
        fields = ['approval_status', 'professional_notes']
        widgets = {
            'approval_status': forms.Select(attrs={'class': 'form-control'}),
            'professional_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ========== Milestone & Site Update Forms ==========

class ProjectMilestoneForm(forms.ModelForm):
    class Meta:
        model = ProjectMilestone
        fields = [
            'project', 'title', 'description', 'planned_start_date',
            'planned_end_date', 'display_order'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'planned_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('planned_start_date')
        end_date = cleaned_data.get('planned_end_date')
        
        if start_date and end_date and end_date < start_date:
            raise ValidationError('End date cannot be before start date.')
        return cleaned_data


class SiteUpdateForm(forms.ModelForm):
    class Meta:
        model = SiteUpdate
        fields = [
            'project', 'milestone', 'title', 'description',
            'progress_percent', 'weather_note', 'is_visible_to_client'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'milestone': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'progress_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'weather_note': forms.TextInput(attrs={'class': 'form-control'}),
            'is_visible_to_client': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SiteUpdateImageForm(forms.ModelForm):
    class Meta:
        model = SiteUpdateImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SiteUpdateImageInlineFormSet(forms.models.BaseInlineFormSet):
    """Formset for handling multiple images for a site update"""
    
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        # Ensure at least one image is provided
        if not any(form.cleaned_data.get('image') for form in self.forms if form not in self.deleted_forms):
            raise ValidationError('At least one image is required for site update.')


# ========== CCTV Forms ==========

class CCTVCameraForm(forms.ModelForm):
    class Meta:
        model = CCTVCamera
        fields = ['project', 'name', 'location_note', 'stream_url']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location_note': forms.TextInput(attrs={'class': 'form-control'}),
            'stream_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


# ========== Worker Management Forms ==========
class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['user', 'full_name', 'phone_number', 'worker_type', 'daily_wage', 'address', 'id_proof', 'is_active']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter worker full name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'worker_type': forms.Select(attrs={'class': 'form-control'}),
            'daily_wage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Daily wage in INR'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter address'}),
            'id_proof': forms.FileInput(attrs={'class': 'form-control-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_daily_wage(self):
        wage = self.cleaned_data.get('daily_wage')
        if wage and wage < 0:
            raise ValidationError('Daily wage cannot be negative.')
        return wage


class ProjectWorkerForm(forms.ModelForm):
    class Meta:
        model = ProjectWorker
        fields = ['project', 'worker', 'start_date', 'end_date', 'custom_daily_wage']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'worker': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'custom_daily_wage': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise ValidationError('End date cannot be before start date.')
        return cleaned_data


class WorkerAttendanceForm(forms.ModelForm):
    class Meta:
        model = WorkerAttendance
        fields = ['status', 'check_in_time', 'check_out_time', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'check_in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class BulkAttendanceForm(forms.Form):
    """Form for marking attendance for multiple workers at once"""
    
    attendance_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.localdate
    )
    
    def __init__(self, project_workers, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for pw in project_workers:
            field_name = f'attendance_{pw.id}'
            self.fields[field_name] = forms.ChoiceField(
                choices=WorkerAttendance.Status.choices,
                widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
                required=False,
                label=f"{pw.worker.full_name}"
            )


class WagePaymentForm(forms.ModelForm):
    class Meta:
        model = WagePayment
        fields = ['period_start', 'period_end', 'total_days', 'wage_per_day', 'paid_amount', 'payment_reference']
        widgets = {
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'wage_per_day': forms.NumberInput(attrs={'class': 'form-control'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_reference': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        paid_amount = cleaned_data.get('paid_amount')
        total_amount = cleaned_data.get('total_days', 0) * cleaned_data.get('wage_per_day', 0)
        
        if period_start and period_end and period_end < period_start:
            raise ValidationError('Period end cannot be before period start.')
        
        if paid_amount and paid_amount > total_amount:
            raise ValidationError('Paid amount cannot exceed total amount.')
        
        return cleaned_data


# ========== Material Management Forms ==========

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'unit', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ProjectMaterialForm(forms.ModelForm):
    class Meta:
        model = ProjectMaterial
        fields = ['material', 'quantity_required', 'unit_cost']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'quantity_required': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        quantity_required = cleaned_data.get('quantity_required', 0)
        unit_cost = cleaned_data.get('unit_cost', 0)
        
        if quantity_required < 0:
            raise ValidationError('Quantity cannot be negative.')
        
        if unit_cost < 0:
            raise ValidationError('Unit cost cannot be negative.')
        
        return cleaned_data


# ========== Consultation Forms ==========

class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ['professional', 'project_category', 'requirement', 'preferred_date']
        widgets = {
            'professional': forms.Select(attrs={'class': 'form-control'}),
            'project_category': forms.Select(attrs={'class': 'form-control'}),
            'requirement': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ConsultationResponseForm(forms.ModelForm):
    """Form for professionals to respond to consultation requests"""
    
    class Meta:
        model = ConsultationRequest
        fields = ['status', 'response_message']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'response_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


# ========== Messaging Forms ==========

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body', 'attachment']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your message...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control-file'}),
        }


# ========== Review Forms ==========

class ProjectReviewForm(forms.ModelForm):
    class Meta:
        model = ProjectReview
        fields = ['rating', 'comment', 'is_public']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ========== Portfolio Forms ==========

class PortfolioProjectForm(forms.ModelForm):
    class Meta:
        model = PortfolioProject
        fields = [
            'project', 'title', 'description', 'location',
            'cover_image', 'completion_year', 'is_featured', 'is_public'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'completion_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PortfolioImageForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ['image', 'caption', 'display_order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PortfolioImageInlineFormSet(forms.models.BaseInlineFormSet):
    """Formset for handling multiple images for portfolio projects"""
    
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        
        # Validate at least one image
        if not any(form.cleaned_data.get('image') for form in self.forms if form not in self.deleted_forms):
            raise ValidationError('At least one image is required for portfolio project.')


class ConsultationResponseForm(forms.ModelForm):
    """Form for professionals to respond to consultation requests"""
    
    class Meta:
        model = ConsultationRequest
        fields = ['status', 'response_message']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'response_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your response here...'}),
        }

class WorkerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise ValidationError("Passwords do not match")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'WORKER'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Create worker profile
            Worker.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}",
                phone_number=user.phone_number,
                worker_type='LABOUR',
                daily_wage=500  # Default wage
            )
        return user
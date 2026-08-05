from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView, View
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Avg, Sum, F, Max
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal

# REST Framework imports
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

# Local imports
from .models import *
from .forms import *
from .serializers import *

# ========== Helper Functions ==========

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def is_professional(user):
    """Check if user is a professional"""
    return user.is_authenticated and user.role in ['ARCHITECT', 'CIVIL_ENGINEER', 'CONTRACTOR']

def home(request):
    """Home page view"""
    return render(request, 'home.html')

def create_notification(recipient, notification_type, title, message, project=None, metadata=None):
    """Helper function to create notifications"""
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        project=project,
        metadata=metadata or {},
        email_sent=False,
        sms_sent=False
    )
    return notification

# ========== Authentication Views ==========

class LoginView(FormView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        login(self.request, form.get_user())
        messages.success(self.request, f'Welcome back, {self.request.user.get_full_name() or self.request.user.username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)

class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login.')
        return response

class WorkerRegisterView(CreateView):
    model = User
    form_class = WorkerRegistrationForm
    template_name = 'registration/worker_register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Worker registration successful! Please login.')
        return response

# ========== Dashboard View ==========

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user'] = user
        context['user_role'] = user.role
        
        # Common counts
        context['total_projects'] = ConstructionProject.objects.filter(
            Q(client=user) | Q(architect=user) | Q(civil_engineer=user) | Q(contractor=user)
        ).count() if not user.is_superuser else ConstructionProject.objects.count()
        
        context['active_projects'] = ConstructionProject.objects.filter(
            Q(client=user) | Q(architect=user) | Q(civil_engineer=user) | Q(contractor=user),
            status__in=['PLANNING', 'DESIGNING', 'IN_PROGRESS']
        ).count() if not user.is_superuser else ConstructionProject.objects.filter(status__in=['PLANNING', 'DESIGNING', 'IN_PROGRESS']).count()
        
        context['total_workers'] = Worker.objects.filter(is_active=True).count()
        context['pending_consultations'] = ConsultationRequest.objects.filter(
            Q(client=user) | Q(professional=user),
            status='PENDING'
        ).count() if not user.is_superuser else ConsultationRequest.objects.filter(status='PENDING').count()
        
        # Role-specific data
        if user.role == 'CLIENT':
            context['my_projects'] = ConstructionProject.objects.filter(client=user)[:5]
            context['consultation_requests'] = ConsultationRequest.objects.filter(client=user).order_by('-created_at')[:5]
            context['recent_updates'] = SiteUpdate.objects.filter(
                project__client=user, 
                is_visible_to_client=True
            ).order_by('-created_at')[:10]
            
        elif user.role in ['ARCHITECT', 'CIVIL_ENGINEER', 'CONTRACTOR']:
            context['assigned_projects'] = ConstructionProject.objects.filter(
                Q(architect=user) | Q(civil_engineer=user) | Q(contractor=user)
            )[:5]
            context['pending_plan_reviews'] = BuildingPlan.objects.filter(
                project__in=ConstructionProject.objects.filter(
                    Q(architect=user) | Q(civil_engineer=user)
                ),
                approval_status='SUBMITTED'
            ).count()
            
        elif user.role == 'WORKER':
            worker_profile = getattr(user, 'worker_profile', None)
            if worker_profile:
                context['active_assignments'] = ProjectWorker.objects.filter(worker=worker_profile, is_active=True)
                context['recent_attendance'] = WorkerAttendance.objects.filter(project_worker__worker=worker_profile)[:10]
                context['pending_payments'] = WagePayment.objects.filter(project_worker__worker=worker_profile, status='PENDING')
                
        elif user.is_superuser or user.role == 'ADMIN':
            context['total_users'] = User.objects.count()
            context['pending_verifications'] = ProfessionalProfile.objects.filter(verification_status='PENDING').count()
            context['recent_users'] = User.objects.order_by('-date_joined')[:10]
            context['recent_projects'] = ConstructionProject.objects.order_by('-created_at')[:10]
        
        return context

# ========== Profile Views ==========

class ProfessionalProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = ProfessionalProfile
    form_class = ProfessionalProfileForm
    template_name = 'professionals/profile_form.html'
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ['ARCHITECT', 'CIVIL_ENGINEER', 'CONTRACTOR'] and not request.user.is_superuser:
            messages.error(request, 'Only professionals can access professional profile.')
            return redirect('dashboard')
        
        if not hasattr(request.user, 'professional_profile'):
            ProfessionalProfile.objects.create(user=request.user)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        return self.request.user.professional_profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Professional profile updated successfully!')
        return super().form_valid(form)

class ClientProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = ClientProfile
    form_class = ClientProfileForm
    template_name = 'clients/profile_form.html'
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'CLIENT' and not request.user.is_superuser:
            messages.error(request, 'Only clients can access client profile.')
            return redirect('dashboard')
        
        if not hasattr(request.user, 'client_profile'):
            ClientProfile.objects.create(user=request.user)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        return self.request.user.client_profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Client profile updated successfully!')
        return super().form_valid(form)

# ========== Project Views ==========

class ProjectListView(LoginRequiredMixin, ListView):
    model = ConstructionProject
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = ConstructionProject.objects.all()
        user = self.request.user
        
        if user.role == 'CLIENT':
            queryset = queryset.filter(client=user)
        elif user.role == 'ARCHITECT':
            queryset = queryset.filter(architect=user)
        elif user.role == 'CIVIL_ENGINEER':
            queryset = queryset.filter(civil_engineer=user)
        elif user.role == 'CONTRACTOR':
            queryset = queryset.filter(contractor=user)
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(city__icontains=search_query)
            )
        
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('client', 'category').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ConstructionProject.Status.choices
        context['categories'] = ProjectCategory.objects.all()
        context['current_status'] = self.request.GET.get('status', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = ConstructionProject
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # This line is CRITICAL - make sure it exists
        context['building_plans'] = project.building_plans.all().order_by('-created_at')
        context['milestones'] = project.milestones.all()
        context['site_updates'] = project.site_updates.all()[:20]
        context['materials'] = project.materials.select_related('material').all()
        context['workers'] = project.project_workers.select_related('worker').filter(is_active=True)
        
        return context

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = ConstructionProject
    form_class = ConstructionProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('project_list')
    
    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.role == 'CLIENT':
            initial['client'] = self.request.user
        return initial
    
    def form_valid(self, form):
        if self.request.user.role == 'CLIENT' and not form.cleaned_data.get('client'):
            form.instance.client = self.request.user
        
        title = form.cleaned_data.get('title')
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while ConstructionProject.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        form.instance.slug = slug
        
        response = super().form_valid(form)
        messages.success(self.request, f'Project "{self.object.title}" created successfully!')
        return response
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ConstructionProject
    form_class = ConstructionProjectForm
    template_name = 'projects/project_update_form.html'
    pk_url_kwarg = 'pk'
    
    def test_func(self):
        project = self.get_object()
        user = self.request.user
        return user == project.client or user == project.architect or user == project.civil_engineer or user == project.contractor or user.is_superuser
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Project "{self.object.title}" updated successfully!')
        return super().form_valid(form)

class ProjectStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = ConstructionProject
    form_class = ConstructionProjectStatusForm
    template_name = 'projects/status_update.html'
    pk_url_kwarg = 'pk'
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Project status updated successfully!')
        return super().form_valid(form)

class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ConstructionProject
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')
    pk_url_kwarg = 'pk'
    
    def test_func(self):
        project = self.get_object()
        return self.request.user == project.client or self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Project deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ========== Building Plan Views ==========

class BuildingPlanListView(LoginRequiredMixin, ListView):
    model = BuildingPlan
    template_name = 'plans/plan_list.html'
    context_object_name = 'plans'
    paginate_by = 12
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            return BuildingPlan.objects.filter(project_id=project_id)
        return BuildingPlan.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            context['project'] = get_object_or_404(ConstructionProject, id=project_id)
        context['plan_types'] = BuildingPlan.PlanType.choices
        context['approval_statuses'] = BuildingPlan.ApprovalStatus.choices
        return context

class BuildingPlanUploadView(LoginRequiredMixin, CreateView):
    model = BuildingPlan
    form_class = BuildingPlanForm
    template_name = 'plans/plan_upload.html'
    
    def dispatch(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        self.project = get_object_or_404(ConstructionProject, id=project_id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
    
    def form_valid(self, form):
        print("=" * 50)
        print("FORM IS VALID - SAVING PLAN")
        print(f"User: {self.request.user}")
        print(f"Project: {self.project}")
        print(f"Plan Type: {form.cleaned_data.get('plan_type')}")
        print(f"Title: {form.cleaned_data.get('title')}")
        
        form.instance.uploaded_by = self.request.user
        form.instance.project = self.project
        
        # Auto-increment version
        from django.db.models import Max
        last_version = BuildingPlan.objects.filter(
            project=self.project,
            plan_type=form.cleaned_data['plan_type']
        ).aggregate(max_version=Max('version'))['max_version']
        form.instance.version = (last_version or 0) + 1
        
        response = super().form_valid(form)
        
        print(f"Plan saved with ID: {self.object.id}")
        print("=" * 50)
        
        messages.success(self.request, f'Plan "{self.object.title}" uploaded successfully!')
        return response
    
    def form_invalid(self, form):
        print("=" * 50)
        print("FORM IS INVALID")
        print(f"Errors: {form.errors}")
        print("=" * 50)
        messages.error(self.request, f'Error uploading plan: {form.errors}')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.project.id})
class BuildingPlanApprovalView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BuildingPlan
    form_class = BuildingPlanApprovalForm
    template_name = 'plans/plan_approval.html'
    
    def test_func(self):
        plan = self.get_object()
        user = self.request.user
        return user == plan.project.architect or user == plan.project.civil_engineer or user.is_superuser
    
    def get_success_url(self):
        return reverse('plan_list', kwargs={'project_id': self.object.project.id})
    
    def form_valid(self, form):
        if form.cleaned_data['approval_status'] == 'APPROVED':
            form.instance.approved_at = timezone.now()
        messages.success(self.request, f'Plan "{self.object.title}" has been reviewed.')
        return super().form_valid(form)

# ========== Milestone Views ==========

class MilestoneListView(LoginRequiredMixin, ListView):
    model = ProjectMilestone
    template_name = 'milestones/milestone_list.html'
    context_object_name = 'milestones'
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            return ProjectMilestone.objects.filter(project_id=project_id).order_by('display_order')
        return ProjectMilestone.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            context['project'] = get_object_or_404(ConstructionProject, id=project_id)
        return context

class MilestoneCreateView(LoginRequiredMixin, CreateView):
    model = ProjectMilestone
    fields = ['title', 'description', 'planned_start_date', 'planned_end_date', 'display_order']
    template_name = 'milestones/milestone_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        self.project = get_object_or_404(ConstructionProject, id=project_id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
    
    def form_valid(self, form):
        form.instance.project = self.project
        response = super().form_valid(form)
        messages.success(self.request, f'Milestone "{self.object.title}" created!')
        return response
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.project.id})


class MilestoneUpdateView(LoginRequiredMixin, UpdateView):
    model = ProjectMilestone
    form_class = ProjectMilestoneForm
    template_name = 'milestones/milestone_form.html'
    
    def get_success_url(self):
        return reverse('milestone_list', kwargs={'project_id': self.object.project.id})
    
    def form_valid(self, form):
        messages.success(self.request, f'Milestone "{self.object.title}" updated successfully!')
        return super().form_valid(form)

# ========== Site Update Views ==========

class SiteUpdateListView(LoginRequiredMixin, ListView):
    model = SiteUpdate
    template_name = 'site_updates/update_list.html'
    context_object_name = 'updates'
    paginate_by = 10
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            queryset = SiteUpdate.objects.filter(project_id=project_id)
            
            if self.request.user.role == 'CLIENT':
                queryset = queryset.filter(is_visible_to_client=True)
            
            return queryset.select_related('posted_by', 'milestone').order_by('-update_date', '-created_at')
        return SiteUpdate.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            context['project'] = get_object_or_404(ConstructionProject, id=project_id)
        return context

class SiteUpdateCreateView(LoginRequiredMixin, CreateView):
    model = SiteUpdate
    fields = ['title', 'description', 'progress_percent', 'weather_note', 'milestone', 'is_visible_to_client']
    template_name = 'site_updates/update_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        self.project = get_object_or_404(ConstructionProject, id=project_id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
    
    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        form.instance.project = self.project
        response = super().form_valid(form)
        
        # Update project progress
        if form.cleaned_data.get('progress_percent'):
            self.project.progress_percent = form.cleaned_data['progress_percent']
            self.project.save()
        
        messages.success(self.request, 'Site update posted successfully!')
        return response
    
    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.project.id})

# ========== Worker Views ==========

class WorkerListView(LoginRequiredMixin, ListView):
    model = Worker
    template_name = 'workers/worker_list.html'
    context_object_name = 'workers'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Worker.objects.all()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(Q(full_name__icontains=search) | Q(phone_number__icontains=search))
        
        worker_type = self.request.GET.get('worker_type', '')
        if worker_type:
            queryset = queryset.filter(worker_type=worker_type)
        
        is_active = self.request.GET.get('is_active', '')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('full_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['worker_types'] = Worker.WorkerType.choices
        context['current_type'] = self.request.GET.get('worker_type', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class WorkerCreateView(LoginRequiredMixin, CreateView):
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'
    success_url = reverse_lazy('worker_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Worker "{self.object.full_name}" created successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class WorkerUpdateView(LoginRequiredMixin, UpdateView):
    model = Worker
    form_class = WorkerForm
    template_name = 'workers/worker_form.html'
    success_url = reverse_lazy('worker_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Worker "{self.object.full_name}" updated successfully!')
        return super().form_valid(form)

class WorkerDeleteView(LoginRequiredMixin, DeleteView):
    model = Worker
    template_name = 'workers/worker_confirm_delete.html'
    success_url = reverse_lazy('worker_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Worker deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ========== Project Worker Views ==========

class ProjectWorkerListView(LoginRequiredMixin, ListView):
    model = ProjectWorker
    template_name = 'workers/project_worker_list.html'
    context_object_name = 'assignments'
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            return ProjectWorker.objects.filter(project_id=project_id).select_related('worker')
        return ProjectWorker.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            context['project'] = get_object_or_404(ConstructionProject, id=project_id)
        return context

class ProjectWorkerAssignView(LoginRequiredMixin, CreateView):
    model = ProjectWorker
    form_class = ProjectWorkerForm
    template_name = 'workers/project_worker_assign.html'
    
    def dispatch(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        self.project = get_object_or_404(ConstructionProject, id=project_id)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.project = self.project
        form.instance.assigned_by = self.request.user
        messages.success(self.request, 'Worker assigned successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('project_worker_list', kwargs={'project_id': self.project.id})

# ========== Attendance Views ==========

class AttendanceProjectSelectView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/project_select.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role == 'CONTRACTOR':
            context['projects'] = ConstructionProject.objects.filter(contractor=user)
        elif user.role == 'ADMIN':
            context['projects'] = ConstructionProject.objects.all()
        else:
            context['projects'] = ConstructionProject.objects.filter(
                Q(architect=user) | Q(civil_engineer=user) | Q(contractor=user)
            )
        
        if user.role == 'CONTRACTOR':
            context['recent_attendances'] = WorkerAttendance.objects.filter(
                project_worker__project__contractor=user
            ).order_by('-attendance_date')[:20]
        elif user.role == 'ADMIN':
            context['recent_attendances'] = WorkerAttendance.objects.all().order_by('-attendance_date')[:20]
        else:
            context['recent_attendances'] = WorkerAttendance.objects.filter(
                project_worker__project__in=context['projects']
            ).order_by('-attendance_date')[:20]
        
        return context

class WorkerAttendanceListView(LoginRequiredMixin, ListView):
    model = WorkerAttendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 20
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        if project_id:
            return WorkerAttendance.objects.filter(
                project_worker__project_id=project_id
            ).select_related('project_worker__worker', 'marked_by').order_by('-attendance_date')
        return WorkerAttendance.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            context['project'] = get_object_or_404(ConstructionProject, id=project_id)
        context['today'] = timezone.now().date()
        return context

class WorkerAttendanceMarkView(LoginRequiredMixin, View):
    template_name = 'attendance/attendance_mark.html'
    
    def dispatch(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        self.project = get_object_or_404(ConstructionProject, id=project_id)
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        context = {
            'project': self.project,
            'project_workers': ProjectWorker.objects.filter(project=self.project, is_active=True).select_related('worker'),
            'today': timezone.now().date(),
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        today = timezone.now().date()
        
        for key, value in request.POST.items():
            if key.startswith('attendance_'):
                try:
                    project_worker_id = int(key.split('_')[1])
                except (IndexError, ValueError):
                    continue
                
                if value:
                    check_in = request.POST.get(f'check_in_{project_worker_id}', '')
                    check_out = request.POST.get(f'check_out_{project_worker_id}', '')
                    notes = request.POST.get(f'notes_{project_worker_id}', '')
                    
                    check_in_time = None
                    check_out_time = None
                    
                    if check_in:
                        try:
                            check_in_time = datetime.strptime(check_in, '%H:%M').time()
                        except ValueError:
                            pass
                    
                    if check_out:
                        try:
                            check_out_time = datetime.strptime(check_out, '%H:%M').time()
                        except ValueError:
                            pass
                    
                    WorkerAttendance.objects.update_or_create(
                        project_worker_id=project_worker_id,
                        attendance_date=today,
                        defaults={
                            'status': value,
                            'marked_by': request.user,
                            'notes': notes,
                            'check_in_time': check_in_time,
                            'check_out_time': check_out_time
                        }
                    )
        
        messages.success(request, f'Attendance for {today.strftime("%Y-%m-%d")} saved successfully!')
        return redirect('attendance_list')

class MonthlyAttendanceReportView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/monthly_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        year = self.request.GET.get('year', timezone.now().year)
        month = self.request.GET.get('month', timezone.now().month)
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            year = timezone.now().year
            month = timezone.now().month
        
        context['selected_year'] = year
        context['selected_month'] = month
        
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        context['month_name'] = f"{month_names[month-1]} {year}"
        
        user = self.request.user
        if user.role == 'CONTRACTOR':
            projects = ConstructionProject.objects.filter(contractor=user)
        elif user.role == 'ADMIN':
            projects = ConstructionProject.objects.all()
        else:
            projects = ConstructionProject.objects.filter(
                Q(architect=user) | Q(civil_engineer=user) | Q(contractor=user)
            )
        
        project_workers = ProjectWorker.objects.filter(
            project__in=projects,
            is_active=True
        ).select_related('worker', 'project')
        
        worker_summaries = []
        total_workers = 0
        total_present_days = 0
        total_absent_days = 0
        total_half_days = 0
        total_leave_days = 0
        
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        working_days = 0
        current = first_day
        while current <= last_day:
            if current.weekday() != 6:
                working_days += 1
            current += timedelta(days=1)
        
        for pw in project_workers:
            attendances = WorkerAttendance.objects.filter(
                project_worker=pw,
                attendance_date__year=year,
                attendance_date__month=month
            )
            
            present = attendances.filter(status='PRESENT').count()
            absent = attendances.filter(status='ABSENT').count()
            half_day = attendances.filter(status='HALF_DAY').count()
            paid_leave = attendances.filter(status='PAID_LEAVE').count()
            
            days_in_month = (last_day - first_day).days + 1
            not_recorded = days_in_month - attendances.count()
            total_absent = absent + not_recorded
            
            daily_wage = pw.custom_daily_wage or pw.worker.daily_wage
            total_wage = (present * daily_wage) + (half_day * daily_wage / 2) + (paid_leave * daily_wage)
            
            if days_in_month > 0:
                attendance_percentage = round((present + half_day * 0.5 + paid_leave) / days_in_month * 100, 1)
            else:
                attendance_percentage = 0
            
            worker_summaries.append({
                'worker': pw.worker,
                'project': pw.project,
                'present': present,
                'absent': total_absent,
                'half_day': half_day,
                'paid_leave': paid_leave,
                'total_days': days_in_month,
                'attendance_percentage': attendance_percentage,
                'total_wage': total_wage,
                'daily_wage': daily_wage
            })
            
            total_workers += 1
            total_present_days += present
            total_absent_days += total_absent
            total_half_days += half_day
            total_leave_days += paid_leave
        
        worker_summaries.sort(key=lambda x: x['worker'].full_name)
        
        context['worker_summaries'] = worker_summaries
        context['total_workers'] = total_workers
        context['total_present_days'] = total_present_days
        context['total_absent_days'] = total_absent_days
        context['total_half_days'] = total_half_days
        context['total_leave_days'] = total_leave_days
        context['working_days'] = working_days
        
        current_year = timezone.now().year
        context['years'] = range(current_year - 2, current_year + 3)
        context['months'] = [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ]
        
        return context

# ========== Wage Payment Views ==========

class WagePaymentListView(LoginRequiredMixin, ListView):
    model = WagePayment
    template_name = 'payments/wage_payment_list.html'
    context_object_name = 'payments'
    paginate_by = 15
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            return WagePayment.objects.filter(project_worker__project_id=project_id).select_related('project_worker__worker')
        return WagePayment.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            context['project'] = get_object_or_404(ConstructionProject, id=project_id)
        return context

class WagePaymentCreateView(LoginRequiredMixin, CreateView):
    model = WagePayment
    fields = ['period_start', 'period_end', 'total_days', 'wage_per_day', 'paid_amount', 'payment_reference']
    template_name = 'payments/wage_payment_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.project_worker = get_object_or_404(ProjectWorker, id=kwargs['project_worker_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        return {'wage_per_day': self.project_worker.custom_daily_wage or self.project_worker.worker.daily_wage}
    
    def form_valid(self, form):
        form.instance.project_worker = self.project_worker
        messages.success(self.request, 'Payment recorded successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('wage_payment_list', kwargs={'project_id': self.project_worker.project.id})

# ========== Material Views (SINGLE DEFINITION) ==========

class MaterialListView(LoginRequiredMixin, ListView):
    model = Material
    template_name = 'materials/material_list.html'
    context_object_name = 'materials'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Material.objects.all()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['total_materials'] = Material.objects.count()
        return context

class MaterialCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Material
    fields = ['name', 'unit', 'description']
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('material_list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'CONTRACTOR'] or self.request.user.is_superuser
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Material "{self.object.name}" created successfully!')
        return response

class MaterialUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Material
    fields = ['name', 'unit', 'description']
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('material_list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'CONTRACTOR'] or self.request.user.is_superuser
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Material "{self.object.name}" updated successfully!')
        return response

class MaterialDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Material
    template_name = 'materials/material_confirm_delete.html'
    success_url = reverse_lazy('material_list')
    
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'CONTRACTOR'] or self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        material = self.get_object()
        messages.success(request, f'Material "{material.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ========== Project Material Views ==========

class ProjectMaterialListView(LoginRequiredMixin, ListView):
    model = ProjectMaterial
    template_name = 'materials/project_material_list.html'
    context_object_name = 'materials'
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            return ProjectMaterial.objects.filter(project_id=project_id).select_related('material')
        return ProjectMaterial.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        if project_id:
            if isinstance(project_id, str):
                project_id = uuid.UUID(project_id)
            context['project'] = get_object_or_404(ConstructionProject, id=project_id)
            
            total_cost = ProjectMaterial.objects.filter(project_id=project_id).aggregate(
                total=Sum(F('quantity_required') * F('unit_cost'))
            )['total'] or 0
            context['total_estimated_cost'] = total_cost
        return context

class ProjectMaterialCreateView(LoginRequiredMixin, CreateView):
    model = ProjectMaterial
    fields = ['material', 'quantity_required', 'unit_cost']
    template_name = 'materials/project_material_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        if isinstance(project_id, str):
            project_id = uuid.UUID(project_id)
        self.project = get_object_or_404(ConstructionProject, id=project_id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
    
    def form_valid(self, form):
        form.instance.project = self.project
        response = super().form_valid(form)
        messages.success(self.request, f'Material "{self.object.material.name}" added to project!')
        return response
    
    def get_success_url(self):
        return reverse('project_material_list', kwargs={'project_id': self.project.id})

class ProjectMaterialUpdateView(LoginRequiredMixin, UpdateView):
    model = ProjectMaterial
    fields = ['quantity_required', 'quantity_used', 'unit_cost']
    template_name = 'materials/project_material_form.html'
    
    def get_success_url(self):
        return reverse('project_material_list', kwargs={'project_id': self.object.project.id})
    
    def form_valid(self, form):
        messages.success(self.request, f'Material "{self.object.material.name}" updated successfully!')
        return super().form_valid(form)

class ProjectMaterialDeleteView(LoginRequiredMixin, DeleteView):
    model = ProjectMaterial
    template_name = 'materials/project_material_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('project_material_list', kwargs={'project_id': self.object.project.id})
    
    def delete(self, request, *args, **kwargs):
        material = self.get_object()
        messages.success(request, f'Material "{material.material.name}" removed from project!')
        return super().delete(request, *args, **kwargs)

# ========== Consultation Views ==========

class ConsultationRequestListView(LoginRequiredMixin, ListView):
    model = ConsultationRequest
    template_name = 'consultations/request_list.html'
    context_object_name = 'requests'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'CLIENT':
            return ConsultationRequest.objects.filter(client=user).order_by('-created_at')
        elif user.role in ['ARCHITECT', 'CIVIL_ENGINEER', 'CONTRACTOR']:
            # Show ALL consultations for professionals (not just pending)
            return ConsultationRequest.objects.filter(professional=user).order_by('-created_at')
        return ConsultationRequest.objects.all().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add status filter options
        context['status_choices'] = ConsultationRequest.Status.choices
        return context



class ConsultationRequestCreateView(LoginRequiredMixin, CreateView):
    model = ConsultationRequest
    fields = ['professional', 'project_category', 'requirement', 'preferred_date']
    template_name = 'consultations/request_form.html'
    success_url = reverse_lazy('consultation_list')
    
    def form_valid(self, form):
        form.instance.client = self.request.user
        messages.success(self.request, 'Consultation request sent successfully!')
        return super().form_valid(form)

class ConsultationRequestDetailView(LoginRequiredMixin, DetailView):
    model = ConsultationRequest
    template_name = 'consultations/request_detail.html'
    context_object_name = 'consultation'

class ConsultationResponseView(LoginRequiredMixin, UpdateView):
    model = ConsultationRequest
    fields = ['status', 'response_message']
    template_name = 'consultations/request_respond.html'
    
    def get_success_url(self):
        return reverse('consultation_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.responded_at = timezone.now()
        response = super().form_valid(form)
        
        create_notification(
            recipient=self.object.client,
            notification_type='CONSULTATION_REQUEST',
            title=f'Consultation Request {self.object.get_status_display()}',
            message=f'Your consultation request has been {self.object.get_status_display().lower()} by {self.object.professional.get_full_name()}',
            project=None,
            metadata={'consultation_id': str(self.object.id)}
        )
        
        messages.success(self.request, 'Response sent successfully!')
        return response

# ========== Notifications API Views ==========
def get_notifications_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:20]
    
    notification_data = []
    for n in notifications:
        notification_data.append({
            'id': str(n.id),
            'title': n.title,
            'message': n.message,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
            'time_ago': n.created_at.strftime('%b %d, %H:%M'),
            'is_read': n.is_read,
            'notification_type': n.notification_type,
            'metadata': n.metadata or {}  # Include metadata
        })
    
    return JsonResponse({
        'notifications': notification_data,
        'unread_count': notifications.count()
    })

@require_http_methods(["POST"])
def mark_notification_read_api(request, notification_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True, 'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

@require_http_methods(["POST"])
def mark_all_notifications_read_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    count = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    return JsonResponse({'success': True, 'message': f'{count} notifications marked as read'})

# ========== Error Handlers ==========

def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)

from django.http import HttpResponse
from django.db import connection
from django.contrib.auth import get_user_model

def debug(request):
    User = get_user_model()

    users = [
        f"{u.username} | staff={u.is_staff} | super={u.is_superuser}"
        for u in User.objects.all()
    ]

    return HttpResponse(
        f"""
        ENGINE: {connection.settings_dict['ENGINE']}<br>
        DB: {connection.settings_dict['NAME']}<br><br>
        USERS:<br>
        {'<br>'.join(users)}
        """
    )


from django.http import HttpResponse
from django.contrib.auth import get_user_model

def test_admin(request):
    User = get_user_model()

    try:
        u = User.objects.get(username="adminkiran")
        return HttpResponse(
            f"""
            Username: {u.username}<br>
            Staff: {u.is_staff}<br>
            Superuser: {u.is_superuser}<br>
            Active: {u.is_active}
            """
        )
    except Exception as e:
        return HttpResponse(str(e))

from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

def test_admin(request):
    User = get_user_model()

    u = User.objects.get(username="adminkiran")

    auth = authenticate(
        username="adminkiran",
        password="csgk9741"   # replace with your current password
    )

    return HttpResponse(f"""
Username: {u.username}<br>
Staff: {u.is_staff}<br>
Superuser: {u.is_superuser}<br>
Authenticated: {auth is not None}
""")
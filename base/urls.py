from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Authentication URLs
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/worker/', views.WorkerRegisterView.as_view(), name='worker_register'),
    
    # Profile URLs
    path('profile/professional/', views.ProfessionalProfileUpdateView.as_view(), name='professional_profile'),
    path('profile/client/', views.ClientProfileUpdateView.as_view(), name='client_profile'),
    
    # Project URLs - UUID
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<uuid:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<uuid:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<uuid:pk>/status/', views.ProjectStatusUpdateView.as_view(), name='project_status_update'),
    path('projects/<uuid:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    
    # Building Plan URLs - UUID
    path('projects/<uuid:project_id>/plans/', views.BuildingPlanListView.as_view(), name='plan_list'),
    path('projects/<uuid:project_id>/plans/upload/', views.BuildingPlanUploadView.as_view(), name='plan_upload'),
    path('plans/<uuid:pk>/approve/', views.BuildingPlanApprovalView.as_view(), name='plan_approval'),
    
    # Milestone URLs - UUID
    path('projects/<uuid:project_id>/milestones/', views.MilestoneListView.as_view(), name='milestone_list'),
    path('projects/<uuid:project_id>/milestones/create/', views.MilestoneCreateView.as_view(), name='milestone_create'),
    path('milestones/<uuid:pk>/update/', views.MilestoneUpdateView.as_view(), name='milestone_update'),
    
    # Site Update URLs - UUID
    path('projects/<uuid:project_id>/updates/', views.SiteUpdateListView.as_view(), name='site_update_list'),
    path('projects/<uuid:project_id>/updates/create/', views.SiteUpdateCreateView.as_view(), name='site_update_create'),
    
    # Worker URLs - UUID (FIXED)
    path('workers/', views.WorkerListView.as_view(), name='worker_list'),
    path('workers/create/', views.WorkerCreateView.as_view(), name='worker_create'),
    path('workers/<uuid:pk>/update/', views.WorkerUpdateView.as_view(), name='worker_update'),
    path('workers/<uuid:pk>/delete/', views.WorkerDeleteView.as_view(), name='worker_delete'),
    
    # Project Worker URLs
    path('projects/<uuid:project_id>/workers/', views.ProjectWorkerListView.as_view(), name='project_worker_list'),
    path('projects/<uuid:project_id>/workers/assign/', views.ProjectWorkerAssignView.as_view(), name='project_worker_assign'),
# Attendance URLs
path('attendance/', views.AttendanceProjectSelectView.as_view(), name='attendance_list'),
path('attendance/report/', views.MonthlyAttendanceReportView.as_view(), name='attendance_monthly_report'),
path('attendance/<uuid:project_id>/', views.WorkerAttendanceListView.as_view(), name='project_attendance_list'),
path('attendance/<uuid:project_id>/mark/', views.WorkerAttendanceMarkView.as_view(), name='attendance_mark'),
    
    # Wage Payment URLs
    path('projects/<uuid:project_id>/payments/', views.WagePaymentListView.as_view(), name='wage_payment_list'),
    path('project-workers/<int:project_worker_id>/payments/create/', views.WagePaymentCreateView.as_view(), name='wage_payment_create'),
    
    # Material URLs
    path('materials/', views.MaterialListView.as_view(), name='material_list'),
    path('projects/<uuid:project_id>/materials/', views.ProjectMaterialListView.as_view(), name='project_material_list'),
    path('projects/<uuid:project_id>/materials/add/', views.ProjectMaterialCreateView.as_view(), name='project_material_add'),
    
    # Consultation URLs - UUID
    path('consultations/', views.ConsultationRequestListView.as_view(), name='consultation_list'),
    path('consultations/create/', views.ConsultationRequestCreateView.as_view(), name='consultation_create'),
    path('consultations/<uuid:pk>/', views.ConsultationRequestDetailView.as_view(), name='consultation_detail'),
    path('consultations/<uuid:pk>/respond/', views.ConsultationResponseView.as_view(), name='consultation_respond'),
# Material URLs - ORDER MATTERS! Put specific before general
path('materials/', views.MaterialListView.as_view(), name='material_list'),
path('materials/create/', views.MaterialCreateView.as_view(), name='material_create'),
path('materials/<uuid:pk>/update/', views.MaterialUpdateView.as_view(), name='material_update'),
path('materials/<uuid:pk>/delete/', views.MaterialDeleteView.as_view(), name='material_delete'),

# Project Material URLs
path('projects/<uuid:project_id>/materials/', views.ProjectMaterialListView.as_view(), name='project_material_list'),
path('projects/<uuid:project_id>/materials/add/', views.ProjectMaterialCreateView.as_view(), name='project_material_add'),
path('projects/<uuid:project_id>/materials/<int:pk>/update/', views.ProjectMaterialUpdateView.as_view(), name='project_material_update'),
path('projects/<uuid:project_id>/materials/<int:pk>/delete/', views.ProjectMaterialDeleteView.as_view(), name='project_material_delete'),

 # API URLs - Notifications
path('api/notifications/', views.get_notifications_api, name='api_notifications'),
path('api/notifications/<uuid:notification_id>/read/', views.mark_notification_read_api, name='api_notification_read'),
path('api/notifications/mark-all-read/', views.mark_all_notifications_read_api, name='api_notifications_read_all'),
]


path("debug/", views.debug),

from base import views
path("test-admin/", views.test_admin),

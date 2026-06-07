import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class UUIDTimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        ARCHITECT = "ARCHITECT", "Architect"
        CIVIL_ENGINEER = "CIVIL_ENGINEER", "Civil Engineer"
        CONTRACTOR = "CONTRACTOR", "Contractor"
        WORKER = "WORKER", "Worker"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.CLIENT)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to="users/profile_images/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.get_full_name() or self.username


class ProfessionalProfile(UUIDTimeStampedModel):
    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professional_profile",
    )
    firm_name = models.CharField(max_length=180, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=180, blank=True)
    experience_years = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal("0.0"),
        validators=[MinValueValidator(0)],
    )
    bio = models.TextField(blank=True)
    service_locations = models.JSONField(default=list, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("0.00"))
    total_projects = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user} Professional Profile"


class ClientProfile(UUIDTimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    preferred_project_type = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Client Profile - {self.user}"


class ProjectCategory(UUIDTimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ConstructionProject(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        ENQUIRY = "ENQUIRY", "Enquiry"
        PLANNING = "PLANNING", "Planning"
        DESIGNING = "DESIGNING", "Designing"
        APPROVED = "APPROVED", "Approved"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        ON_HOLD = "ON_HOLD", "On Hold"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_projects",
    )
    architect = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="architecture_projects",
    )
    civil_engineer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="engineering_projects",
    )
    contractor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracted_projects",
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    site_address = models.TextField()
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    plot_area_sqft = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    estimated_budget = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    actual_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.ENQUIRY)
    progress_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    is_public_portfolio = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["architect", "status"]),
            models.Index(fields=["civil_engineer", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return self.title


class BuildingPlan(UUIDTimeStampedModel):
    class PlanType(models.TextChoices):
        # Architect plans
        FLOOR_PLAN = "FLOOR_PLAN", "🏠 Floor Plan"
        ELEVATION = "ELEVATION", "🏢 Elevation"
        INTERIOR = "INTERIOR", "🛋️ Interior Design"
        _3D_RENDER = "3D_RENDER", "🎨 3D Rendering"
        
        # Engineer plans
        STRUCTURAL = "STRUCTURAL", "🏗️ Structural Plan"
        FOUNDATION = "FOUNDATION", "📐 Foundation Plan"
        LOAD_CALC = "LOAD_CALC", "⚖️ Load Calculation"
        
        # Contractor plans
        SITE_PLAN = "SITE_PLAN", "📍 Site Plan"
        ESTIMATE = "ESTIMATE", "💰 Cost Estimate"
        SCHEDULE = "SCHEDULE", "📅 Construction Schedule"
        
        # General
        ELECTRICAL = "ELECTRICAL", "⚡ Electrical Plan"
        PLUMBING = "PLUMBING", "💧 Plumbing Plan"
        OTHER = "OTHER", "📄 Other"


    class ApprovalStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        REVISION_REQUESTED = "REVISION_REQUESTED", "Revision Requested"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    project = models.ForeignKey(ConstructionProject, on_delete=models.CASCADE, related_name="building_plans")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    plan_type = models.CharField(max_length=30, choices=PlanType.choices)
    title = models.CharField(max_length=180)
    file = models.FileField(upload_to="projects/plans/")
    version = models.PositiveIntegerField(default=1)
    approval_status = models.CharField(max_length=30, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)
    client_notes = models.TextField(blank=True)
    professional_notes = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["project", "-version"]
        indexes = [models.Index(fields=["project", "plan_type", "approval_status"])]

    def __str__(self):
        return f"{self.title} v{self.version}"


class ProjectMilestone(UUIDTimeStampedModel):
    project = models.ForeignKey(ConstructionProject, on_delete=models.CASCADE, related_name="milestones")
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    planned_start_date = models.DateField(null=True, blank=True)
    planned_end_date = models.DateField(null=True, blank=True)
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    progress_percent = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_completed = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "planned_start_date"]

    def __str__(self):
        return f"{self.project} - {self.title}"


class SiteUpdate(UUIDTimeStampedModel):
    project = models.ForeignKey(ConstructionProject, on_delete=models.CASCADE, related_name="site_updates")
    milestone = models.ForeignKey(ProjectMilestone, on_delete=models.SET_NULL, null=True, blank=True, related_name="site_updates")
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=180)
    description = models.TextField()
    progress_percent = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    update_date = models.DateField(default=timezone.localdate)
    weather_note = models.CharField(max_length=160, blank=True)
    is_visible_to_client = models.BooleanField(default=True)

    class Meta:
        ordering = ["-update_date", "-created_at"]

    def __str__(self):
        return self.title


class SiteUpdateImage(UUIDTimeStampedModel):
    site_update = models.ForeignKey(SiteUpdate, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/site_updates/")
    caption = models.CharField(max_length=180, blank=True)

    def __str__(self):
        return f"Image for {self.site_update}"


class CCTVCamera(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    project = models.ForeignKey(ConstructionProject, on_delete=models.CASCADE, related_name="cctv_cameras")
    name = models.CharField(max_length=120)
    location_note = models.CharField(max_length=180, blank=True)
    stream_url = models.URLField(max_length=700)
    snapshot_image = models.ImageField(upload_to="projects/cctv_snapshots/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.project} - {self.name}"


class Worker(UUIDTimeStampedModel):
    class WorkerType(models.TextChoices):
        MASON = "MASON", "Mason"
        CARPENTER = "CARPENTER", "Carpenter"
        ELECTRICIAN = "ELECTRICIAN", "Electrician"
        PLUMBER = "PLUMBER", "Plumber"
        PAINTER = "PAINTER", "Painter"
        LABOUR = "LABOUR", "Labour"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        OTHER = "OTHER", "Other"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="worker_profile",
    )
    full_name = models.CharField(max_length=160)
    phone_number = models.CharField(max_length=20, blank=True)
    worker_type = models.CharField(max_length=30, choices=WorkerType.choices)
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    address = models.TextField(blank=True)
    id_proof = models.FileField(upload_to="workers/id_proofs/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name


class ProjectWorker(UUIDTimeStampedModel):
    project = models.ForeignKey(ConstructionProject, on_delete=models.CASCADE, related_name="project_workers")
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="project_assignments")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField(null=True, blank=True)
    custom_daily_wage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "worker"], name="unique_worker_per_project")
        ]

    def __str__(self):
        return f"{self.worker} assigned to {self.project}"


class WorkerAttendance(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        HALF_DAY = "HALF_DAY", "Half Day"
        PAID_LEAVE = "PAID_LEAVE", "Paid Leave"

    project_worker = models.ForeignKey(ProjectWorker, on_delete=models.CASCADE, related_name="attendance_records")
    attendance_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project_worker", "attendance_date"], name="unique_worker_attendance_per_day")
        ]
        indexes = [models.Index(fields=["attendance_date", "status"])]

    def __str__(self):
        return f"{self.project_worker.worker} - {self.attendance_date}"


class WagePayment(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    project_worker = models.ForeignKey(ProjectWorker, on_delete=models.CASCADE, related_name="wage_payments")
    period_start = models.DateField()
    period_end = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    wage_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=120, blank=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.total_days * self.wage_per_day
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Wage payment for {self.project_worker.worker}"


class Material(UUIDTimeStampedModel):
    name = models.CharField(max_length=160, unique=True)
    unit = models.CharField(max_length=40, default="pcs")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ProjectMaterial(UUIDTimeStampedModel):
    project = models.ForeignKey(ConstructionProject, on_delete=models.CASCADE, related_name="materials")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="project_usages")
    quantity_required = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    quantity_used = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    @property
    def estimated_cost(self):
        return self.quantity_required * self.unit_cost

    def __str__(self):
        return f"{self.material} for {self.project}"


class ConsultationRequest(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consultation_requests")
    professional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_consultation_requests")
    project_category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, blank=True)
    requirement = models.TextField()
    preferred_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    response_message = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.client} -> {self.professional}"


class Conversation(UUIDTimeStampedModel):
    project = models.ForeignKey(ConstructionProject, on_delete=models.CASCADE, null=True, blank=True, related_name="conversations")
    consultation_request = models.OneToOneField(
        ConsultationRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversation",
    )
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="archify_conversations")

    def __str__(self):
        return f"Conversation {self.id}"


class Message(UUIDTimeStampedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="archify_messages")
    body = models.TextField()
    attachment = models.FileField(upload_to="messages/attachments/", blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender}"


class ProjectReview(UUIDTimeStampedModel):
    project = models.OneToOneField(ConstructionProject, on_delete=models.CASCADE, related_name="review")
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="given_project_reviews")
    professional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_project_reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.project} - {self.rating}/5"


class PortfolioProject(UUIDTimeStampedModel):
    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolio_projects",
    )
    project = models.OneToOneField(
        ConstructionProject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="portfolio_entry",
    )
    title = models.CharField(max_length=180)
    description = models.TextField()
    location = models.CharField(max_length=180, blank=True)
    cover_image = models.ImageField(upload_to="portfolio/covers/", blank=True, null=True)
    completion_year = models.PositiveIntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class PortfolioImage(UUIDTimeStampedModel):
    portfolio_project = models.ForeignKey(PortfolioProject, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="portfolio/images/")
    caption = models.CharField(max_length=180, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"Image for {self.portfolio_project}"


class Notification(UUIDTimeStampedModel):
    class Type(models.TextChoices):
        CONSULTATION_REQUEST = "CONSULTATION_REQUEST", "Consultation Request"
        PROJECT_UPDATE = "PROJECT_UPDATE", "Project Update"
        PLAN_APPROVED = "PLAN_APPROVED", "Plan Approved"
        PLAN_REVISION = "PLAN_REVISION", "Plan Revision Requested"
        WORKER_ATTENDANCE = "WORKER_ATTENDANCE", "Worker Attendance"
        WAGE_PAYMENT = "WAGE_PAYMENT", "Wage Payment"
        NEW_MESSAGE = "NEW_MESSAGE", "New Message"
        CCTV_ALERT = "CCTV_ALERT", "CCTV Alert"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=40, choices=Type.choices)
    project = models.ForeignKey(ConstructionProject, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    title = models.CharField(max_length=180)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipient", "is_read"])]

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at", "updated_at"])

    def __str__(self):
        return self.title


class ActivityLog(UUIDTimeStampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=120, db_index=True)
    object_type = models.CharField(max_length=120, blank=True)
    object_id = models.CharField(max_length=120, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.action 
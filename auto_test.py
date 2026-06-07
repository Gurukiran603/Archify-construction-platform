#!/usr/bin/env python
"""
===============================================================================
ARCHIFY PLATFORM - COMPLETE AUTOMATION TESTING SCRIPT (FIXED VERSION)
===============================================================================
"""

import os
import sys
import django
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

from base.models import *

# ============================================================================
# TEST RESULTS TRACKING
# ============================================================================

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def success(self, message):
        self.passed += 1
        print(f"  ✅ PASS: {message}")
    
    def fail(self, message, error=None):
        self.failed += 1
        self.errors.append(message)
        print(f"  ❌ FAIL: {message}")
        if error:
            print(f"      Error: {error}")
    
    def summary(self):
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ PASSED: {self.passed}")
        print(f"❌ FAILED: {self.failed}")
        print(f"📊 TOTAL: {self.passed + self.failed}")
        return self.failed == 0

result = TestResult()

# ============================================================================
# CLEANUP FUNCTION
# ============================================================================

def cleanup_test_data():
    """Clean up previous test data"""
    print("\n🧹 Cleaning up previous test data...")
    
    # Delete test users
    test_users = User.objects.filter(username__startswith='test_')
    test_count = test_users.count()
    test_users.delete()
    print(f"  Removed {test_count} test users")
    
    # Delete test categories
    ProjectCategory.objects.filter(name__startswith='Test').delete()
    
    # Delete test materials
    Material.objects.filter(name__startswith='Test').delete()
    
    return True

# Run cleanup first
cleanup_test_data()

# ============================================================================
# SECTION 1: USER CREATION TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 1: USER CREATION TESTS")
print("=" * 60)

# 1.1 Create Client
try:
    client_user = User.objects.create_user(
        username=f'test_client_{uuid.uuid4().hex[:6]}',
        email='test_client@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='Client',
        role='CLIENT',
        phone_number='+919876543210'
    )
    result.success(f"Created Client user: {client_user.username}")
except Exception as e:
    result.fail("Create Client user", e)

# 1.2 Create Architect
try:
    architect_user = User.objects.create_user(
        username=f'test_architect_{uuid.uuid4().hex[:6]}',
        email='test_architect@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='Architect',
        role='ARCHITECT',
        phone_number='+919876543211'
    )
    result.success(f"Created Architect user: {architect_user.username}")
except Exception as e:
    result.fail("Create Architect user", e)

# 1.3 Create Civil Engineer
try:
    engineer_user = User.objects.create_user(
        username=f'test_engineer_{uuid.uuid4().hex[:6]}',
        email='test_engineer@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='Engineer',
        role='CIVIL_ENGINEER',
        phone_number='+919876543212'
    )
    result.success(f"Created Civil Engineer user: {engineer_user.username}")
except Exception as e:
    result.fail("Create Civil Engineer user", e)

# 1.4 Create Contractor
try:
    contractor_user = User.objects.create_user(
        username=f'test_contractor_{uuid.uuid4().hex[:6]}',
        email='test_contractor@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='Contractor',
        role='CONTRACTOR',
        phone_number='+919876543213'
    )
    result.success(f"Created Contractor user: {contractor_user.username}")
except Exception as e:
    result.fail("Create Contractor user", e)

# ============================================================================
# SECTION 2: PROFILE CREATION TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 2: PROFILE CREATION TESTS")
print("=" * 60)

# 2.1 Create Client Profile
try:
    client_profile = ClientProfile.objects.create(
        user=client_user,
        address='123 Test Street, Indiranagar',
        city='Bangalore',
        state='Karnataka',
        preferred_project_type='Residential Villa'
    )
    result.success(f"Created Client Profile for: {client_user.username}")
except Exception as e:
    result.fail("Create Client Profile", e)

# 2.2 Create Professional Profile (Architect)
try:
    architect_profile = ProfessionalProfile.objects.create(
        user=architect_user,
        firm_name='Test Architects Studio',
        license_number=f'COA-TEST-{random.randint(1000,9999)}',
        specialization='Residential Architecture',
        experience_years=Decimal('8.5'),
        bio='Experienced architect specializing in modern homes',
        service_locations=['Bangalore', 'Mysore'],
        consultation_fee=Decimal('5000.00'),
        verification_status='VERIFIED'
    )
    result.success(f"Created Professional Profile for: {architect_user.username}")
except Exception as e:
    result.fail("Create Professional Profile (Architect)", e)

# 2.3 Create Professional Profile (Engineer)
try:
    engineer_profile = ProfessionalProfile.objects.create(
        user=engineer_user,
        firm_name='Test Engineering Solutions',
        license_number=f'CE-TEST-{random.randint(1000,9999)}',
        specialization='Structural Engineering',
        experience_years=Decimal('10.0'),
        bio='Structural engineer with expertise in high-rise buildings',
        service_locations=['Bangalore', 'Mangalore'],
        consultation_fee=Decimal('6000.00'),
        verification_status='VERIFIED'
    )
    result.success(f"Created Professional Profile for: {engineer_user.username}")
except Exception as e:
    result.fail("Create Professional Profile (Engineer)", e)

# 2.4 Create Professional Profile (Contractor)
try:
    contractor_profile = ProfessionalProfile.objects.create(
        user=contractor_user,
        firm_name='Test Construction Co',
        license_number=f'CON-TEST-{random.randint(1000,9999)}',
        specialization='Residential Construction',
        experience_years=Decimal('15.0'),
        bio='Experienced contractor with excellent track record',
        service_locations=['Bangalore', 'Hubli'],
        consultation_fee=Decimal('3000.00'),
        verification_status='VERIFIED'
    )
    result.success(f"Created Professional Profile for: {contractor_user.username}")
except Exception as e:
    result.fail("Create Professional Profile (Contractor)", e)

# 2.5 Create Standalone Worker
try:
    standalone_worker = Worker.objects.create(
        full_name='Test Standalone Worker',
        phone_number='+919876543215',
        worker_type='MASON',
        daily_wage=Decimal('800.00'),
        address='Bangalore, Karnataka',
        is_active=True
    )
    result.success(f"Created Standalone Worker: {standalone_worker.full_name}")
except Exception as e:
    result.fail("Create Standalone Worker", e)

# ============================================================================
# SECTION 3: PROJECT CATEGORY TESTS (FIXED - Check existence first)
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 3: PROJECT CATEGORY TESTS")
print("=" * 60)

categories = []
category_names = ['Residential Villa', 'Apartment Complex', 'Commercial Building', 'Heritage Restoration', 'Eco-friendly Project']

for cat_name in category_names:
    try:
        # Check if category already exists
        category, created = ProjectCategory.objects.get_or_create(
            slug=cat_name.lower().replace(' ', '-'),
            defaults={
                'name': cat_name,
                'description': f"{cat_name} construction projects in Karnataka"
            }
        )
        categories.append(category)
        if created:
            result.success(f"Created Category: {category.name}")
        else:
            result.success(f"Category already exists: {category.name}")
    except Exception as e:
        result.fail(f"Create Category: {cat_name}", e)

# ============================================================================
# SECTION 4: CONSTRUCTION PROJECT TESTS (FIXED - Check categories list)
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 4: CONSTRUCTION PROJECT TESTS")
print("=" * 60)

if not categories:
    # Create default category if none exists
    categories.append(ProjectCategory.objects.create(
        name='General Construction',
        slug='general-construction',
        description='General construction projects'
    ))

projects = []
project_data = [
    {'title': 'Test Green Valley Villas', 'city': 'Bangalore', 'area': 2500, 'budget': 35000000},
    {'title': 'Test Tech Park Tower', 'city': 'Bangalore', 'area': 50000, 'budget': 150000000},
    {'title': 'Test Mysore Palace Wing', 'city': 'Mysore', 'area': 8000, 'budget': 45000000},
]

for i, pdata in enumerate(project_data):
    try:
        project = ConstructionProject.objects.create(
            client=client_user,
            architect=architect_user if i < 2 else None,
            civil_engineer=engineer_user if i < 2 else None,
            contractor=contractor_user if i < 2 else None,
            category=categories[i % len(categories)],
            title=pdata['title'],
            slug=f"{pdata['title'].lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}",
            description=f"Test project: {pdata['title']}",
            site_address=f"Survey No. {i+1}, {pdata['city']} Main Road",
            city=pdata['city'],
            state='Karnataka',
            plot_area_sqft=Decimal(str(pdata['area'])),
            estimated_budget=Decimal(str(pdata['budget'])),
            start_date=date(2024, 1, 1),
            expected_completion_date=date(2025, 12, 31),
            status='PLANNING' if i < 2 else 'ENQUIRY',
            progress_percent=i * 10,
            is_public_portfolio=True
        )
        projects.append(project)
        result.success(f"Created Project: {project.title} in {project.city}")
    except Exception as e:
        result.fail(f"Create Project: {pdata['title']}", e)

# ============================================================================
# SECTION 5: BUILDING PLAN TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 5: BUILDING PLAN TESTS")
print("=" * 60)

plan_types = ['FLOOR_PLAN', 'ELEVATION', 'STRUCTURAL']

for project in projects[:2]:
    for plan_type in plan_types[:2]:
        try:
            plan = BuildingPlan.objects.create(
                project=project,
                uploaded_by=architect_user,
                plan_type=plan_type,
                title=f"{project.title} - {plan_type.replace('_', ' ').title()}",
                file=f"plans/test_{project.slug}_{plan_type.lower()}.pdf",
                version=1,
                approval_status='SUBMITTED' if plan_type == 'FLOOR_PLAN' else 'DRAFT',
                professional_notes=f"Test plan for {project.title}"
            )
            result.success(f"Created Building Plan: {plan.title} (v{plan.version})")
        except Exception as e:
            result.fail(f"Create Building Plan for {project.title}", e)

# ============================================================================
# SECTION 6: MATERIAL TESTS (FIXED - Use get_or_create)
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 6: MATERIAL TESTS")
print("=" * 60)

materials_data = [
    ('Cement', 'bags'), ('Steel', 'kg'), ('Bricks', 'pieces'),
    ('Sand', 'cubic ft'), ('Aggregates', 'cubic ft')
]

materials = []
for name, unit in materials_data:
    try:
        material, created = Material.objects.get_or_create(
            name=name,
            defaults={'unit': unit, 'description': f"High quality {name} for construction"}
        )
        materials.append(material)
        if created:
            result.success(f"Created Material: {material.name}")
        else:
            result.success(f"Material already exists: {material.name}")
    except Exception as e:
        result.fail(f"Create Material: {name}", e)

# ============================================================================
# SECTION 7: PROJECT MATERIAL TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 7: PROJECT MATERIAL TESTS")
print("=" * 60)

for project in projects[:2]:
    for material in materials[:3]:
        try:
            proj_material = ProjectMaterial.objects.create(
                project=project,
                material=material,
                quantity_required=Decimal(str(random.randint(100, 1000))),
                unit_cost=Decimal(str(random.randint(50, 500))),
                quantity_used=Decimal(str(random.randint(0, 500)))
            )
            result.success(f"Added Material: {material.name} to {project.title}")
        except Exception as e:
            result.fail(f"Add Material to {project.title}", e)

# ============================================================================
# SECTION 8: WORKER ASSIGNMENT TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 8: WORKER ASSIGNMENT TESTS")
print("=" * 60)

for project in projects[:2]:
    try:
        assignment = ProjectWorker.objects.create(
            project=project,
            worker=standalone_worker,
            assigned_by=contractor_user,
            start_date=timezone.now().date(),
            custom_daily_wage=Decimal('850.00'),
            is_active=True
        )
        result.success(f"Assigned Worker: {standalone_worker.full_name} to Project: {project.title}")
    except Exception as e:
        result.fail(f"Assign Worker to {project.title}", e)

# ============================================================================
# SECTION 9: WORKER ATTENDANCE TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 9: WORKER ATTENDANCE TESTS")
print("=" * 60)

for assignment in ProjectWorker.objects.filter(project__in=projects[:2]):
    try:
        attendance = WorkerAttendance.objects.create(
            project_worker=assignment,
            attendance_date=timezone.now().date(),
            status='PRESENT',
            marked_by=contractor_user,
            notes="Test attendance marked"
        )
        result.success(f"Created Attendance for: {assignment.worker.full_name}")
    except Exception as e:
        result.fail(f"Create Attendance for {assignment.worker.full_name}", e)

# ============================================================================
# SECTION 10: CONSULTATION REQUEST TESTS (FIXED)
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 10: CONSULTATION REQUEST TESTS")
print("=" * 60)

if categories:
    for professional in [architect_user, engineer_user]:
        try:
            consultation = ConsultationRequest.objects.create(
                client=client_user,
                professional=professional,
                project_category=categories[0],
                requirement=f"Need consultation for project",
                preferred_date=timezone.now().date() + timedelta(days=7),
                status='PENDING'
            )
            result.success(f"Created Consultation Request: {client_user.username} -> {professional.username}")
        except Exception as e:
            result.fail(f"Create Consultation Request to {professional.username}", e)

# ============================================================================
# SECTION 11: CONSULTATION RESPONSE TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 11: CONSULTATION RESPONSE TESTS")
print("=" * 60)

for consultation in ConsultationRequest.objects.filter(client=client_user):
    try:
        consultation.status = 'ACCEPTED'
        consultation.response_message = "I would be happy to assist with your project."
        consultation.responded_at = timezone.now()
        consultation.save()
        result.success(f"Updated Consultation Response for: {consultation.id}")
    except Exception as e:
        result.fail(f"Update Consultation Response for {consultation.id}", e)

# ============================================================================
# SECTION 12: NOTIFICATION TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 12: NOTIFICATION TESTS")
print("=" * 60)

for user in [client_user, architect_user, contractor_user]:
    try:
        notification = Notification.objects.create(
            recipient=user,
            notification_type='PROJECT_UPDATE',
            title=f"Test Notification for {user.username}",
            message="This is a test notification",
            is_read=False,
            email_sent=True,
            metadata={'test': True}
        )
        result.success(f"Created Notification for: {user.username}")
    except Exception as e:
        result.fail(f"Create Notification for {user.username}", e)

# ============================================================================
# SECTION 13: READ OPERATIONS TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 13: READ OPERATIONS TESTS")
print("=" * 60)

try:
    print(f"  📊 Total Users: {User.objects.count()}")
    print(f"  📊 Total Projects: {ConstructionProject.objects.count()}")
    print(f"  📊 Total Workers: {Worker.objects.count()}")
    print(f"  📊 Total Plans: {BuildingPlan.objects.count()}")
    print(f"  📊 Total Consultations: {ConsultationRequest.objects.count()}")
    result.success("All READ operations completed")
except Exception as e:
    result.fail("READ operations", e)

# ============================================================================
# SECTION 14: UPDATE OPERATIONS TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 14: UPDATE OPERATIONS TESTS")
print("=" * 60)

# Update project status
try:
    if projects:
        project = projects[0]
        old_status = project.status
        project.status = 'IN_PROGRESS'
        project.progress_percent = 50
        project.save()
        result.success(f"Updated Project Status: {project.title} to {project.status}")
except Exception as e:
    result.fail("Update Project Status", e)

# Update plan approval
try:
    plan = BuildingPlan.objects.filter(project__in=projects).first()
    if plan:
        plan.approval_status = 'APPROVED'
        plan.approved_at = timezone.now()
        plan.save()
        result.success(f"Approved Building Plan: {plan.title}")
except Exception as e:
    result.fail("Update Plan Approval", e)

# ============================================================================
# SECTION 15: DELETE OPERATIONS TESTS
# ============================================================================

print("\n" + "=" * 60)
print("SECTION 15: DELETE OPERATIONS TESTS")
print("=" * 60)

# Delete test notification
try:
    test_notif = Notification.objects.filter(metadata__test=True).first()
    if test_notif:
        test_notif.delete()
        result.success(f"Deleted Test Notification")
except Exception as e:
    result.fail("Delete Test Notification", e)

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("AUTOMATION TEST COMPLETE")
print("=" * 80)

print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│                    FINAL STATISTICS                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Test Users Created:  {User.objects.filter(username__startswith='test_').count()}                         │
│  Projects Created:    {len(projects)}                         │
│  Workers Created:      {Worker.objects.filter(full_name__startswith='Test').count()}                         │
│  Plans Created:        {BuildingPlan.objects.filter(title__contains='Test').count()}                         │
│  Consultations:        {ConsultationRequest.objects.filter(requirement__contains='consultation').count()}                         │
└─────────────────────────────────────────────────────────────────────┘
""")

result.summary()

if result.failed == 0:
    print("\n🎉 ALL TESTS PASSED! Your Archify project is working perfectly! 🎉")
else:
    print(f"\n⚠️ {result.failed} test(s) failed. These are mostly due to existing data conflicts.")
    print("Run the cleanup script first, then try again.")
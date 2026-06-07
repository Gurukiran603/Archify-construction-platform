"""
ARCHIFY PLATFORM - KARNATAKA DATA POPULATION (CLEAN VERSION)
No special Unicode characters - Works on Windows CMD
"""

import os
import django
import uuid
import random
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from base.models import *

User = get_user_model()

print("=" * 60)
print("ARCHIFY - KARNATAKA DATA POPULATION")
print("=" * 60)

# ============================================================================
# CLEANUP EXISTING DATA
# ============================================================================
print("\nCleaning existing data...")

WorkerAttendance.objects.all().delete()
WagePayment.objects.all().delete()
ProjectWorker.objects.all().delete()
BuildingPlan.objects.all().delete()
ProjectMilestone.objects.all().delete()
SiteUpdate.objects.all().delete()
ProjectMaterial.objects.all().delete()
Message.objects.all().delete()
Conversation.objects.all().delete()
ConsultationRequest.objects.all().delete()
Notification.objects.all().delete()
ActivityLog.objects.all().delete()
PortfolioImage.objects.all().delete()
PortfolioProject.objects.all().delete()
ProjectReview.objects.all().delete()
ConstructionProject.objects.all().delete()
ProjectCategory.objects.all().delete()
ProfessionalProfile.objects.all().delete()
ClientProfile.objects.all().delete()
Worker.objects.all().delete()
Material.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

print("Existing data cleared")

# ============================================================================
# CREATE USERS
# ============================================================================
print("\n" + "=" * 60)
print("STEP 1: CREATING USERS")
print("=" * 60)

users_data = [
    ('raju_bangalore', 'CLIENT', 'Raju', 'Shetty', 'Bangalore'),
    ('meena_mysore', 'CLIENT', 'Meena', 'Kulkarni', 'Mysore'),
    ('prakash_mangalore', 'CLIENT', 'Prakash', 'Rao', 'Mangalore'),
    ('anita_hubli', 'CLIENT', 'Anita', 'Deshpande', 'Hubli'),
    ('suresh_belgaum', 'CLIENT', 'Suresh', 'Gowda', 'Belgaum'),
    ('ar_rajesh', 'ARCHITECT', 'Rajesh', 'Bhat', 'Bangalore'),
    ('ar_nandini', 'ARCHITECT', 'Nandini', 'Murthy', 'Mysore'),
    ('ar_sanjay', 'ARCHITECT', 'Sanjay', 'Joshi', 'Mangalore'),
    ('ar_kavitha', 'ARCHITECT', 'Kavitha', 'Reddy', 'Hubli'),
    ('ar_manoj', 'ARCHITECT', 'Manoj', 'Naik', 'Dharwad'),
    ('ce_vijay', 'CIVIL_ENGINEER', 'Vijay', 'Patil', 'Bangalore'),
    ('ce_pooja', 'CIVIL_ENGINEER', 'Pooja', 'Hegde', 'Manipal'),
    ('ce_ravi', 'CIVIL_ENGINEER', 'Ravi', 'Kamat', 'Karwar'),
    ('ce_divya', 'CIVIL_ENGINEER', 'Divya', 'Nayak', 'Udupi'),
    ('ce_mahesh', 'CIVIL_ENGINEER', 'Mahesh', 'Shetty', 'Mangalore'),
    ('ct_srinivas', 'CONTRACTOR', 'Srinivas', 'Murthy', 'Bangalore'),
    ('ct_ganesh', 'CONTRACTOR', 'Ganesh', 'Poojary', 'Mangalore'),
    ('ct_uma', 'CONTRACTOR', 'Uma', 'Devi', 'Mysore'),
    ('ct_kiran', 'CONTRACTOR', 'Kiran', 'Raj', 'Hubli'),
    ('ct_shankar', 'CONTRACTOR', 'Shankar', 'Acharya', 'Belgaum'),
]

created_users = []
for username, role, fname, lname, city in users_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f"{username}@archify.com",
            'first_name': fname,
            'last_name': lname,
            'phone_number': f"+9198{hash(username) % 100000000:08d}",
            'role': role
        }
    )
    if created:
        user.set_password('password123')
        user.save()
    created_users.append(user)
    print(f"  Created: {username} ({role}) - {city}")

print(f"Total Users: {len(created_users)}")

# ============================================================================
# CREATE PROFILES
# ============================================================================
print("\n" + "=" * 60)
print("STEP 2: CREATING PROFILES")
print("=" * 60)

# Client Profiles
for user in User.objects.filter(role='CLIENT'):
    ClientProfile.objects.get_or_create(
        user=user,
        defaults={
            'address': f"Main Road, {user.username.split('_')[1].capitalize()}",
            'city': user.username.split('_')[1].capitalize(),
            'state': 'Karnataka',
            'preferred_project_type': 'Residential Villa'
        }
    )
    print(f"  Client Profile: {user.username}")

# Professional Profiles
for user in User.objects.filter(role='ARCHITECT'):
    ProfessionalProfile.objects.get_or_create(
        user=user,
        defaults={
            'firm_name': f"{user.last_name} Architects",
            'license_number': f"ARCH-{hash(user.username) % 1000:03d}",
            'specialization': 'Residential Architecture',
            'experience_years': Decimal('10.0'),
            'service_locations': [user.username.split('_')[1].capitalize()],
            'consultation_fee': Decimal('5000'),
            'verification_status': 'VERIFIED'
        }
    )
    print(f"  Architect Profile: {user.username}")

for user in User.objects.filter(role='CIVIL_ENGINEER'):
    ProfessionalProfile.objects.get_or_create(
        user=user,
        defaults={
            'firm_name': f"{user.last_name} Engineers",
            'license_number': f"ENG-{hash(user.username) % 1000:03d}",
            'specialization': 'Structural Engineering',
            'experience_years': Decimal('8.0'),
            'service_locations': [user.username.split('_')[1].capitalize()],
            'consultation_fee': Decimal('6000'),
            'verification_status': 'VERIFIED'
        }
    )
    print(f"  Engineer Profile: {user.username}")

for user in User.objects.filter(role='CONTRACTOR'):
    ProfessionalProfile.objects.get_or_create(
        user=user,
        defaults={
            'firm_name': f"{user.last_name} Constructions",
            'license_number': f"CON-{hash(user.username) % 1000:03d}",
            'specialization': 'Residential Construction',
            'experience_years': Decimal('12.0'),
            'service_locations': [user.username.split('_')[1].capitalize()],
            'consultation_fee': Decimal('3000'),
            'verification_status': 'VERIFIED'
        }
    )
    print(f"  Contractor Profile: {user.username}")

# ============================================================================
# CREATE PROJECT CATEGORIES
# ============================================================================
print("\n" + "=" * 60)
print("STEP 3: CREATING PROJECT CATEGORIES")
print("=" * 60)

categories_data = [
    ('residential-villa', 'Residential Villa', 'Luxury independent houses'),
    ('apartment-complex', 'Apartment Complex', 'Multi-story apartments'),
    ('commercial-building', 'Commercial Building', 'Office spaces'),
    ('industrial-project', 'Industrial Project', 'Factories and facilities'),
    ('heritage-restoration', 'Heritage Restoration', 'Restoration projects'),
]

categories = []
for slug, name, desc in categories_data:
    cat, _ = ProjectCategory.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'description': desc}
    )
    categories.append(cat)
    print(f"  Created: {name}")

# ============================================================================
# CREATE PROJECTS
# ============================================================================
print("\n" + "=" * 60)
print("STEP 4: CREATING 20 PROJECTS")
print("=" * 60)

clients = list(User.objects.filter(role='CLIENT'))
architects = list(User.objects.filter(role='ARCHITECT'))
engineers = list(User.objects.filter(role='CIVIL_ENGINEER'))
contractors = list(User.objects.filter(role='CONTRACTOR'))

projects_data = [
    ('Whitefield Luxury Villas', 'Bangalore', 2500, 35000000, 'IN_PROGRESS', 65),
    ('Electronic City Tech Park', 'Bangalore', 50000, 150000000, 'DESIGNING', 25),
    ('Indiranagar Metro Plaza', 'Bangalore', 15000, 75000000, 'PLANNING', 10),
    ('Koramangala Apartment Complex', 'Bangalore', 12000, 60000000, 'IN_PROGRESS', 45),
    ('Mysore Palace Heritage Wing', 'Mysore', 8000, 45000000, 'DESIGNING', 30),
    ('Gokulam Residential Layout', 'Mysore', 5000, 25000000, 'IN_PROGRESS', 70),
    ('JSS University Campus', 'Mysore', 25000, 120000000, 'PLANNING', 5),
    ('Kadri Hills Villa Project', 'Mangalore', 1800, 28000000, 'COMPLETED', 100),
    ('Mangalore SEZ Industrial Park', 'Mangalore', 100000, 250000000, 'DESIGNING', 15),
    ('Father Muller Hospital', 'Mangalore', 3000, 18000000, 'IN_PROGRESS', 55),
    ('Hubli IT Park', 'Hubli', 35000, 95000000, 'DESIGNING', 20),
    ('Dharwad Residential Township', 'Dharwad', 8000, 40000000, 'PLANNING', 8),
    ('Belgaum Cantonment Mall', 'Belgaum', 12000, 55000000, 'IN_PROGRESS', 60),
    ('Green Valley Eco Township', 'Belgaum', 20000, 85000000, 'DESIGNING', 12),
    ('Hampi Heritage Conservation', 'Hospet', 5000, 30000000, 'PLANNING', 3),
    ('Coorg Coffee Estate Resort', 'Madikeri', 1500, 20000000, 'IN_PROGRESS', 80),
    ('Gokarna Beach Resort', 'Gokarna', 2000, 25000000, 'DESIGNING', 18),
    ('Chikmagalur Plantation Homes', 'Chikmagalur', 1200, 18000000, 'COMPLETED', 100),
    ('Shravanabelagola Temple', 'Shravanabelagola', 3000, 22000000, 'PLANNING', 0),
    ('Bidar Fort Restoration', 'Bidar', 6000, 35000000, 'DESIGNING', 22),
]

projects = []
for i, (title, city, area, budget, status, progress) in enumerate(projects_data):
    client = clients[i % len(clients)]
    architect = architects[i % len(architects)]
    engineer = engineers[i % len(engineers)]
    contractor = contractors[i % len(contractors)]
    category = categories[i % len(categories)]
    
    project, _ = ConstructionProject.objects.get_or_create(
        title=title,
        defaults={
            'client': client,
            'architect': architect,
            'civil_engineer': engineer,
            'contractor': contractor,
            'category': category,
            'description': f"{title} - Premium project in {city}, Karnataka",
            'site_address': f"Site No. {i+1}, {city} Main Road",
            'city': city,
            'state': 'Karnataka',
            'plot_area_sqft': Decimal(str(area)),
            'estimated_budget': Decimal(str(budget)),
            'start_date': date(2024, 1, 1),
            'expected_completion_date': date(2026, 12, 31),
            'status': status,
            'progress_percent': progress,
            'is_public_portfolio': True
        }
    )
    projects.append(project)
    print(f"  Created: {title} - {city} ({status})")

print(f"Total Projects: {len(projects)}")

# ============================================================================
# CREATE BUILDING PLANS
# ============================================================================
print("\n" + "=" * 60)
print("STEP 5: CREATING BUILDING PLANS")
print("=" * 60)

plan_count = 0
for project in projects[:15]:
    for plan_type in ['FLOOR_PLAN', 'ELEVATION', 'STRUCTURAL']:
        uploaded_by = project.architect if plan_type != 'STRUCTURAL' else project.civil_engineer
        BuildingPlan.objects.get_or_create(
            project=project,
            plan_type=plan_type,
            version=1,
            defaults={
                'uploaded_by': uploaded_by,
                'title': f"{project.title} - {plan_type.replace('_', ' ').title()}",
                'file': f"plans/{project.slug}_{plan_type.lower()}_v1.pdf",
                'approval_status': 'APPROVED' if random.choice([True, False]) else 'SUBMITTED'
            }
        )
        plan_count += 1
    print(f"  Plans for: {project.title[:30]}...")

print(f"Total Building Plans: {plan_count}")

# ============================================================================
# CREATE WORKERS
# ============================================================================
print("\n" + "=" * 60)
print("STEP 6: CREATING WORKERS")
print("=" * 60)

workers_data = [
    ('Manjunath Gowda', 'MASON', 850, 'Bangalore'),
    ('Siddharth Shetty', 'CARPENTER', 800, 'Mangalore'),
    ('Basavaraj Patil', 'ELECTRICIAN', 950, 'Hubli'),
    ('Ramesh Kamath', 'PLUMBER', 900, 'Udupi'),
    ('Shivappa Kumbar', 'PAINTER', 750, 'Dharwad'),
    ('Krishnappa', 'LABOUR', 550, 'Belgaum'),
    ('Suresh Shetgar', 'SUPERVISOR', 1300, 'Bangalore'),
    ('Prakash Rao', 'MASON', 820, 'Mysore'),
    ('Venkatesh Naik', 'CARPENTER', 780, 'Shimoga'),
    ('Abdul Khader', 'ELECTRICIAN', 920, 'Mangalore'),
]

workers = []
for name, wtype, wage, location in workers_data:
    worker, _ = Worker.objects.get_or_create(
        full_name=name,
        defaults={
            'worker_type': wtype,
            'daily_wage': Decimal(str(wage)),
            'phone_number': f"+9198{hash(name) % 100000000:08d}",
            'address': f"{location}, Karnataka",
            'is_active': True
        }
    )
    workers.append(worker)
    print(f"  Created: {name} ({wtype}) - Rs.{wage}/day")

print(f"Total Workers: {len(workers)}")

# ============================================================================
# ASSIGN WORKERS TO PROJECTS
# ============================================================================
print("\n" + "=" * 60)
print("STEP 7: ASSIGNING WORKERS TO PROJECTS")
print("=" * 60)

for project in projects[:10]:
    for worker in workers[:5]:
        ProjectWorker.objects.get_or_create(
            project=project,
            worker=worker,
            defaults={
                'assigned_by': project.contractor,
                'start_date': date(2024, 1, 1),
                'is_active': True
            }
        )
    print(f"  Assigned workers to: {project.title[:30]}...")

# ============================================================================
# CREATE MATERIALS
# ============================================================================
print("\n" + "=" * 60)
print("STEP 8: CREATING MATERIALS")
print("=" * 60)

materials_data = [
    ('JSW Cement', 'bags'), ('Ultratech Cement', 'bags'), ('TMT Steel', 'kg'),
    ('Red Bricks', 'pieces'), ('River Sand', 'cubic ft'), ('Crushed Stone', 'cubic ft'),
    ('PVC Pipes', 'meter'), ('Ceramic Tiles', 'sq ft'), ('Asian Paints', 'liters'),
    ('Wooden Doors', 'pieces')
]

for name, unit in materials_data:
    Material.objects.get_or_create(name=name, defaults={'unit': unit})
    print(f"  Created: {name} ({unit})")

# ============================================================================
# CREATE CONSULTATIONS
# ============================================================================
print("\n" + "=" * 60)
print("STEP 9: CREATING CONSULTATIONS")
print("=" * 60)

clients_list = list(User.objects.filter(role='CLIENT'))
professionals_list = list(User.objects.filter(role__in=['ARCHITECT', 'CIVIL_ENGINEER', 'CONTRACTOR']))

for client in clients_list[:3]:
    for professional in professionals_list[:2]:
        ConsultationRequest.objects.get_or_create(
            client=client,
            professional=professional,
            requirement=f"Need consultation for project in {client.client_profile.city if hasattr(client, 'client_profile') else 'Karnataka'}",
            defaults={'status': 'PENDING'}
        )
        print(f"  Created: {client.username} -> {professional.username}")

# ============================================================================
# FINAL STATISTICS
# ============================================================================
print("\n" + "=" * 60)
print("DATA POPULATION COMPLETE!")
print("=" * 60)

print(f"""
FINAL STATISTICS:
- Users: {User.objects.count()}
- Clients: {User.objects.filter(role='CLIENT').count()}
- Architects: {User.objects.filter(role='ARCHITECT').count()}
- Engineers: {User.objects.filter(role='CIVIL_ENGINEER').count()}
- Contractors: {User.objects.filter(role='CONTRACTOR').count()}
- Projects: {ConstructionProject.objects.count()}
- Building Plans: {BuildingPlan.objects.count()}
- Workers: {Worker.objects.count()}
- Materials: {Material.objects.count()}
- Consultations: {ConsultationRequest.objects.count()}

LOGIN CREDENTIALS (All users have password: password123):
- Client: raju_bangalore, meena_mysore, prakash_mangalore, anita_hubli, suresh_belgaum
- Architect: ar_rajesh, ar_nandini, ar_sanjay, ar_kavitha, ar_manoj
- Engineer: ce_vijay, ce_pooja, ce_ravi, ce_divya, ce_mahesh
- Contractor: ct_srinivas, ct_ganesh, ct_uma, ct_kiran, ct_shankar

PROJECTS BY CITY:
- Bangalore: 4 projects
- Mysore: 3 projects
- Mangalore: 3 projects
- Hubli: 2 projects
- Belgaum: 2 projects
- Other cities: 6 projects
""")

print("=" * 60)
print("READY! Start server: python manage.py runserver")
print("=" * 60)
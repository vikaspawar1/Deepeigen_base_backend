#!/usr/bin/env python
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deepeigen.settings')
django.setup()

from course.models import Course, Section
from accounts.models import Account

print("=" * 60)
print("Loading test data into database...")
print("=" * 60)

try:
    # Create course
    course, created = Course.objects.get_or_create(
        url_link_name='ai-basics',
        defaults={
            'title': 'AI Basics',
            'category': 'AI',
            'level': 'Advanced',
            'duration': 12,
            'meta_description': 'Introduction to AI Basics',
            'course_description': 'Learn the fundamentals of Artificial Intelligence',
            'indian_fee': 999,
            'foreign_fee': 49,
            'is_featured': True,
            'entire_overview': 'This is a comprehensive course on AI Basics covering all fundamental concepts.',
            'brief_overview': 'Quick overview of AI Basics',
            'enrolled_users': 0,   # ✅ REQUIRED
        }
    )

    print("✓ Course created!" if created else "✓ Course already exists")

    # Create section
    section, created = Section.objects.get_or_create(
        url_name='intro',
        course=course,   # ✅ correct FK usage
        defaults={
            'name': 'Section 1',
            'title': 'Introduction',
            'part_number': 1,
            'module_overview': 'Introduction module covering basic concepts',
            'topics_covered': 'AI History, Basic Concepts, Applications',
            'estimated_time': '2 hours',
            'total_assignments': 3,
        }
    )

    print("✓ Section created!" if created else "✓ Section already exists")

    # Create test user
    user, created = Account.objects.get_or_create(
        email='john@example.com',
        defaults={
            'username': 'johndoe',
            'first_name': 'John',
            'last_name': 'Doe',
        }
    )

    print("✓ User created!" if created else "✓ User already exists")

    print("\n" + "=" * 60)
    print("✅ Test data loaded successfully!")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error loading data: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

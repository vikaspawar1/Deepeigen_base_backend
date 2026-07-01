# Converting HTML Endpoints to JSON - Step-by-Step Guide

## EXAMPLE 1: HTML ENDPOINT → JSON ENDPOINT

### HTML ENDPOINT: `/courses/` (Renders courses listing page)

```python
# FILE: course/views.py
# Current HTML version
def courses(request):
    courses = Course.objects.order_by('id').filter(is_featured=True)
   
    data = {
        'courses': courses,
        'title': 'Courses | Deep Eigen',
        'description': "Deep eigen offers Category-I (Cat-I) and Category-II courses...",
        'canonical_url' : request.build_absolute_uri(request.path),
        'course_flag': True,
    }
    return render(request, 'courses/courses.html', data)  # ← Returns HTML template
```

**What it does:**
- Fetches all featured courses from database
- Packs them in a data dictionary with SEO metadata
- Renders HTML template with that data
- Returns: HTML page rendered to browser

---

### EXAMPLE 2: JSON ENDPOINT - Reference Pattern

```python
# FILE: dashboard/views/users.py
# Already converted to JSON
def users_api(request):
    try:
        # Step 1: Get and validate query parameters
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                raise ValueError("Page number must be >= 1")
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid page number'}, status=400)

        try:
            limit = int(request.GET.get('limit', 10))
            if limit < 1:
                raise ValueError("Limit must be >= 1")
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid limit value'}, status=400)

        # Step 2: Get filter parameter (optional)
        is_active = request.GET.get('is_active')

        # Step 3: Query database with filters
        users = Account.objects.all().order_by('-date_joined')
        
        if is_active in ['true', 'false']:
            users = users.filter(is_active=(is_active == 'true'))

        # Step 4: Apply pagination
        paginator = Paginator(users, limit)

        try:
            users_page = paginator.page(page)
        except PageNotAnInteger:
            return JsonResponse({'error': 'Page is not an integer'}, status=400)
        except EmptyPage:
            return JsonResponse({'error': 'Page out of range', 'total_pages': paginator.num_pages}, status=404)

        # Step 5: Convert QuerySet to JSON-serializable data
        users_data = list(users_page.object_list.values())

        # Step 6: Return JSON response with metadata
        return JsonResponse({
            'all_users': users_data,
            'total_pages': paginator.num_pages,
            'current_page': page,
        }, status=200)

    except Exception as e:
        logger.exception("Unhandled error in users_api view")
        return JsonResponse({
            'error': 'Something went wrong. Please try again later.'
        }, status=500)
```

**What it does:**
- Validates query parameters (page, limit, filters)
- Queries database
- Paginates results
- Converts data to serializable format
- Returns: JSON data with status code

---

## KEY DIFFERENCES: HTML vs JSON

| Aspect | HTML Endpoint | JSON Endpoint |
|--------|--------------|---------------|
| **Import** | `from django.shortcuts import render` | `from django.http import JsonResponse` |
| **Return Statement** | `render(request, 'template.html', data)` | `JsonResponse({...}, status=200)` |
| **Error Handling** | `messages.error()` or redirect | `JsonResponse({'error': '...'}, status=400/500)` |
| **Pagination** | Optional (handled in template) | **Mandatory** (handled in view) |
| **Data Format** | Python dict/QuerySet → Template renders | QuerySet → `.values()` → JSON |
| **Query Params** | Usually POST form data | GET params: `?page=1&limit=10` |
| **CORS Issues** | No (same-domain rendering) | Yes (may need CORS headers) |
| **Response Type** | Content-Type: text/html | Content-Type: application/json |

---

## STEP-BY-STEP CONVERSION TEMPLATE

Use this template to convert ANY HTML endpoint to JSON:

### STEP 1: Add imports at top of file
```python
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

logger = logging.getLogger(__name__)
```

### STEP 2: Create a new API function (keep HTML version intact initially)
```python
def courses_api(request):  # ← Add "_api" suffix to function name
    try:
        # STEP 3: Validate query parameters
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                raise ValueError("Page number must be >= 1")
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid page number'}, status=400)

        try:
            limit = int(request.GET.get('limit', 10))
            if limit < 1:
                raise ValueError("Limit must be >= 1")
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid limit value'}, status=400)

        # STEP 4: Get optional filters
        is_featured = request.GET.get('is_featured', 'true')  # default to featured

        # STEP 5: Query database (same logic as HTML version)
        courses_query = Course.objects.order_by('id')
        
        if is_featured in ['true', 'false']:
            courses_query = courses_query.filter(is_featured=(is_featured == 'true'))

        # STEP 6: Apply pagination
        paginator = Paginator(courses_query, limit)

        try:
            courses_page = paginator.page(page)
        except PageNotAnInteger:
            return JsonResponse({'error': 'Page is not an integer'}, status=400)
        except EmptyPage:
            return JsonResponse({'error': 'Page out of range', 'total_pages': paginator.num_pages}, status=404)

        # STEP 7: Convert to JSON-serializable format
        # Option A: Using .values() for quick conversion
        courses_data = list(courses_page.object_list.values(
            'id', 'title', 'description', 'price', 'url_link_name', 'is_featured'
        ))
        
        # Option B: Manual serialization (for complex objects)
        # courses_data = []
        # for course in courses_page.object_list:
        #     courses_data.append({
        #         'id': course.id,
        #         'title': course.title,
        #         'price': str(course.price),  # Convert Decimal to string
        #         'url': course.url_link_name,
        #     })

        # STEP 8: Return JSON with pagination metadata
        return JsonResponse({
            'courses': courses_data,
            'total_count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'page_size': limit,
        }, status=200)

    except Exception as e:
        logger.exception("Unhandled error in courses_api view")
        return JsonResponse({
            'error': 'Something went wrong. Please try again later.'
        }, status=500)
```

### STEP 3: Add URL route
```python
# In urls.py
from . import views

urlpatterns = [
    path('', views.courses, name='courses'),  # Keep existing
    path('api/', views.courses_api, name='courses_api'),  # Add JSON version
]
```

### STEP 4: Test the endpoint
```bash
# Without pagination
curl "http://localhost:8000/courses/api/"

# With pagination
curl "http://localhost:8000/courses/api/?page=1&limit=5"

# With filters
curl "http://localhost:8000/courses/api/?is_featured=true&page=1&limit=10"
```

---

## COMMON PATTERNS & TIPS

### ✅ DO:
```python
# ✓ Serialize Decimal values to string
'price': str(course.price),

# ✓ Use default=str in JsonResponse for datetime
return JsonResponse(data, default=str, safe=False)

# ✓ Return meaningful status codes
return JsonResponse({...}, status=200)  # Success
return JsonResponse({'error': '...'}, status=400)  # Bad request
return JsonResponse({'error': '...'}, status=404)  # Not found
return JsonResponse({'error': '...'}, status=500)  # Server error

# ✓ Always paginate for large datasets
paginator = Paginator(queryset, limit)

# ✓ Validate user input
page = int(request.GET.get('page', 1))
if page < 1:
    return JsonResponse({'error': 'Invalid page'}, status=400)
```

### ❌ DON'T:
```python
# ✗ Return raw QuerySet - it's not JSON serializable
return JsonResponse(queryset)  # ERROR!

# ✗ Forget to convert to list/values()
return JsonResponse(queryset, safe=False)  # Works but inefficient

# ✗ Return without pagination (for large datasets)
return JsonResponse(list(Course.objects.all().values()), safe=False)  # Memory bomb!

# ✗ Forget error handling
return JsonResponse(data)  # What if data is None? Crash!

# ✗ Return Django model objects directly
return JsonResponse({'course': course_object})  # ERROR - not serializable
```

---

## SERIALIZATION METHODS COMPARISON

### Method 1: Using .values() (FASTEST)
```python
courses_data = list(courses_page.object_list.values('id', 'title', 'price'))
# Returns: [{'id': 1, 'title': 'AI', 'price': Decimal('99.99')}, ...]
# Use when: You only need simple fields
# Drawback: Decimal/DateTime not serialized, need special handling
```

### Method 2: Manual Loop (MOST CONTROL)
```python
courses_data = []
for course in courses_page.object_list:
    courses_data.append({
        'id': course.id,
        'title': course.title,
        'price': float(course.price),  # Explicit conversion
        'sections_count': course.section_set.count(),  # Related counts
        'created': course.created_date.isoformat(),  # DateTime to ISO string
    })
# Use when: You need custom fields, related data, or transformations
```

### Method 3: Using Django Serializers (MOST FLEXIBLE)
```python
from django.core import serializers
import json

courses_data = json.loads(
    serializers.serialize('json', courses_page.object_list)
)
# Use when: You need automatic handling of all field types
# Note: Includes pk and model metadata in output
```

---

## REAL EXAMPLE: CONVERTING `/accounts/mycourses/`

### Current HTML Version:
```python
@login_required(login_url='login')
def mycourses(request):
    enrolled_courses = EnrolledUser.objects.filter(user=request.user, enrolled=True)
    
    data = {
        'enrolled_courses': enrolled_courses,
        'title': 'My Courses | Deep Eigen',
    }
    return render(request, 'accounts/mycourses.html', data)
```

### Converted to JSON Version:
```python
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

logger = logging.getLogger(__name__)

@login_required(login_url='login')
def mycourses_api(request):
    try:
        # Get pagination params
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        
        if page < 1 or limit < 1:
            return JsonResponse({'error': 'Invalid page or limit'}, status=400)

        # Query user's enrolled courses
        enrolled_courses = EnrolledUser.objects.filter(
            user=request.user, 
            enrolled=True
        ).select_related('course', 'user').order_by('-created_at')

        # Paginate
        paginator = Paginator(enrolled_courses, limit)
        try:
            courses_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage) as e:
            return JsonResponse({'error': 'Invalid page'}, status=400)

        # Serialize data
        courses_data = []
        for enrollment in courses_page.object_list:
            courses_data.append({
                'id': enrollment.course.id,
                'title': enrollment.course.title,
                'url': enrollment.course.url_link_name,
                'description': enrollment.course.description,
                'price': float(enrollment.course.price),
                'enrolled_date': enrollment.created_at.isoformat(),
                'end_date': enrollment.end_at.isoformat() if enrollment.end_at else None,
                'progress': enrollment.full_access_flag,  # Boolean
                'installments': {
                    'total': enrollment.no_of_installments,
                    'first': enrollment.first_installments,
                    'second': enrollment.second_installments,
                    'third': enrollment.third_installments,
                }
            })

        return JsonResponse({
            'courses': courses_data,
            'total_count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
        }, status=200)

    except Exception as e:
        logger.exception("Error in mycourses_api")
        return JsonResponse({'error': 'Internal server error'}, status=500)
```

### Add to urls.py:
```python
path('mycourses/', views.mycourses, name='mycourses'),  # Keep HTML
path('mycourses_api/', views.mycourses_api, name='mycourses_api'),  # Add JSON
```

---

## TESTING YOUR CONVERSIONS

Use this simple test format:
```bash
# Test 1: Basic call
curl "http://localhost:8000/dashboard/users_api/"

# Test 2: With pagination
curl "http://localhost:8000/dashboard/users_api/?page=1&limit=5"

# Test 3: With filters
curl "http://localhost:8000/dashboard/users_api/?is_active=true&page=1&limit=10"

# Test 4: Invalid page (should return error)
curl "http://localhost:8000/dashboard/users_api/?page=abc"

# Test 5: Using Python
python manage.py shell
>>> import requests
>>> response = requests.get('http://localhost:8000/dashboard/users_api/?page=1&limit=5')
>>> print(response.json())
```

---

## SUMMARY

**HTML Endpoint Pattern:**
```
Query DB → Pack in dict → Render template → Return HTML
```

**JSON Endpoint Pattern:**
```
Validate params → Query DB → Paginate → Serialize to JSON → Return JsonResponse
```

**Key Things to Remember:**
1. Always validate user input (page, limit)
2. Always paginate large datasets
3. Always handle exceptions
4. Always convert QuerySets/objects to serializable formats
5. Always return proper HTTP status codes
6. Use `.values()` for simple cases, manual loop for complex data
7. Keep HTML and JSON versions separate initially

---

Now you have the complete pattern! Apply these steps to convert any HTML endpoint to JSON.

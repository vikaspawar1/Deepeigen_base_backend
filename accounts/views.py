from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserForm, UserProfileForm
from .models import *
from course.models import *
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpRequest,JsonResponse
from utils.decorators import api_login_required
from datetime import datetime, date,timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from django.db.models import Exists,Count
# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
import requests
from django.template import RequestContext
from django import template
# from Invoice.models import *
# from django.views.decorators.csrf import csrf_protect
from django.db import connection, transaction

#### Invoice as pdf 
from django.http import FileResponse

import inflect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import io
import reportlab
from django.conf import settings
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from deepeigen import *
from reportlab.lib.units import *
from django.core.files import File as DjangoFile
from django.core.files.base import ContentFile
from django.db.models import Q
from django.db.models import Sum

from course.models import EnrolledUser, Course, Payment, Order
from course.invoice_generator import generate_professional_invoice


# for changing to json output
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from types import SimpleNamespace
from decimal import Decimal
from django.utils.timezone import now
# from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework import status
from .utils import get_tokens_for_user


# ==================== END OF NEW JSON VERSION ====================


# ==================== NEW JSON VERSION ====================
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    API endpoint for user registration
    Returns JSON response with user details and status
    Matches Account model fields: first_name, last_name, username, email, password, phone_number, profession, country
    """
    data = request.data
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    phone_number = data.get('phone_number', '').strip() or None
    profession = data.get('profession', '').strip()
    country = data.get('country', '').strip()

    # Validation: Check required fields
    required_fields = ['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password', 'profession', 'country']
    for field in required_fields:
        val = data.get(field, '').strip()
        if not val:
            return Response({
                'success': False,
                'message': f'{field.replace("_", " ").title()} is required',
                'status': 400
            }, status=status.HTTP_400_BAD_REQUEST)

    # Validation: Password match
    if password != confirm_password:
        return Response({
            'success': False,
            'message': 'Password does not match',
            'status': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validation: Username already exists
    if Account.objects.filter(username=username).exists():
        return Response({
            'success': False,
            'message': 'Username already exists',   
            'status': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validation: Email already exists
    if Account.objects.filter(email=email).exists():
        return Response({
            'success': False,
            'message': 'Email already exists',
            'status': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create user with all Account model fields
    try:
        with transaction.atomic():
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                profession=profession,
                country=country
            )
            user.save()

            # Create user profile with default picture
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default_user.png'
            profile.save()

            # Generate activation token
            current_site = get_current_site(request)
            mail_subject = 'Please activate your Deep Eigen account'
            email_context = {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }

            # Send activation email
            plain_message = render_to_string('accounts/account_verification_email.txt', email_context)
            html_message = render_to_string('accounts/account_verification_email.html', email_context)
            to_email = email
            from_email = settings.EMAIL_HOST_USER
            send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)

        # Return success response with user details
        return Response({
            'success': True,
            'message': 'Registration successful. Verification email sent to your email address.',
            'status': 201,
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'profession': user.profession,
                'country': user.country,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat()
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Registration failed: {str(e)}',
            'status': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ==================== END OF NEW JSON VERSION ====================
# ==================== END OF NEW JSON VERSION ====================

@api_view(['POST'])
def register_mannual(request):
    data = {
        'title': 'User Registration | Deep Eigen',
        'description': "Deep Eigen course enrollment is easy by registering as a user by inputting few basic information.",
        'canonical_url' : request.build_absolute_uri(request.path)
    }
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        phone_number = request.POST.get('phone_number')
        profession = request.POST['profession']
        country = request.POST['country']
        
        if password == confirm_password:
            if Account.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('manual_registration')
            elif Account.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists') 
                return redirect('manual_registration')
            else:
                try:
                    with transaction.atomic():
                        user = Account.objects.create_user(
                            first_name=first_name, last_name=last_name,
                            username=username, email=email, password=password,
                            phone_number=phone_number, profession=profession,
                            country=country
                        )
                        user.is_active = True
                        user.save()

                        # Create a user profile
                        profile = UserProfile()
                        profile.user_id = user.id
                        profile.profile_picture = 'default/default_user.png'
                        profile.save()
                except Exception as e:
                    messages.error(request, f'Registration failed: {str(e)}')
                    return redirect('manual_registration')

        else:
            messages.error(request, 'Password do not match')
            return redirect('manual_registration')

        messages.success(request, 'Registration Successfull')
        return redirect('manual_registration')
    return render(request, 'courses/manual_registration.html', data)


# ==================== NEW JSON VERSION ====================
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    API endpoint for user login
    Returns JSON response with user details, authentication token, and pending course installments
    """
    # try:
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '').strip()

    # Validation: Check required fields
    if not email or not password:
        return Response({
            'success': False,
            'message': 'Email and password are required',
            'status': 400
        }, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate user with email and password
    user = authenticate(email=email, password=password)

    if user is not None:
        # Check if user is active (email verified)
        if not user.is_active:
            return Response({
                'success': False,
                'message': 'Account not activated. Please verify your email first.',
                'status': 403
            }, status=status.HTTP_403_FORBIDDEN)

        # Generate JWT tokens
        tokens = get_tokens_for_user(user)

        # Fetch enrolled users and pending installments
        enrolled_users = EnrolledUser.objects.filter(user=user)
        course_data = []

        if enrolled_users.exists():
            for enrolled_user in enrolled_users:
                course_section = []

                # Check for pending installments (2nd, 3rd)
                if enrolled_user.no_of_installments > 1:
                    if enrolled_user.no_of_installments == 2:
                        if not enrolled_user.second_installments:
                            course_section.append({
                                'course_name': enrolled_user.course.title,
                                'course_price': round(enrolled_user.course_price/2, 2),
                                'course_id': enrolled_user.course.id,
                                'course_link': enrolled_user.course.url_link_name,
                                'installment': 'Second Installment'
                            })

                    elif enrolled_user.no_of_installments == 3:
                        if not enrolled_user.second_installments:
                            course_section.append({
                                'course_name': enrolled_user.course.title,
                                'course_price': round(enrolled_user.course_price/3, 2),
                                'course_id': enrolled_user.course.id,
                                'course_link': enrolled_user.course.url_link_name,
                                'installment': 'Second Installment'
                            })

                        elif enrolled_user.second_installments and not enrolled_user.third_installments:
                            course_section.append({
                                'course_name': enrolled_user.course.title,
                                'course_price': round(enrolled_user.course_price/3, 2),
                                'course_id': enrolled_user.course.id,
                                'course_link': enrolled_user.course.url_link_name,
                                'installment': 'Third Installment'
                            })

                course_data.extend(course_section)

        # Store course data in session (optional, but kept for logic)
        # request.session['course_data'] = course_data

        # Return success response with user, tokens, and course details
        return Response({
            'success': True,
            'message': 'Login successful',
            'status': 200,
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'profession': user.profession,
                'country': user.country,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superadmin': user.is_superadmin,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'pending_courses': course_data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'Invalid email or password',
            'status': 401
        }, status=status.HTTP_401_UNAUTHORIZED)







def login_mannual(request):
    data = {
        'title': 'User Login | Deep Eigen',
        'description': "Deep Eigen course access is easy by logging in as a user.",
        'canonical_url': request.build_absolute_uri(request.path)
    }
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            # Check if the user is staff or super admin
            if not (user.is_staff or user.is_superadmin):
                messages.error(request, 'You must be a staff member or super admin to access this page.')
                return redirect('login_mannual')

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')

            # Since you want to remove the enrolled_users related logic, we don't process courses anymore
            # You can directly redirect to the dashboard or any other page
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login_mannual')

    return render(request, 'accounts/mannual_login.html', data)





# ==================== NEW JSON VERSION ====================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    API endpoint for user logout
    Returns JSON response confirming logout and clears session
    POST only - GET not allowed for security
    """
    # if request.method != 'POST':
    #     return JsonResponse({
    #         'success': False,
    #         'message': 'Method not allowed. Please send a POST request.',
    #         'status': 405,
    #         'allowed_methods': ['POST']
    #     }, status=405)
    
    try:
            # Get user info before logout for response
            user_email = request.user.email if request.user.is_authenticated else None
            
            # Clear session and logout user
            auth.logout(request)
            
            return Response({
                'success': True,
                'message': 'Logged out successfully',
                'status': 200,
                'user_email': user_email,
                'session_cleared': True
            }, status=status.HTTP_200_OK)

    except Exception as e:
            return Response({
                'success': False,
                'message': f'Logout failed: {str(e)}',
                'status': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ==================== END OF NEW JSON VERSION ====================




# ==================== NEW JSON VERSION ====================
@api_view(['GET'])
@permission_classes([])
def activate(request, uidb64, token):
    """
    API endpoint for email account activation
    Returns JSON response confirming account activation status
    Takes URL parameters: uidb64 (user id encoded), token (verification token)
    """
    try:
        # Decode the user ID from the base64 encoded string
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist) as e:
        # Invalid or expired activation link
        return JsonResponse({
            'success': False,
            'message': 'Invalid or expired activation link',
            'status': 400,
            'error_type': 'invalid_token'
        }, status=400)

    # Verify the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # Token is valid, activate the user
        user.is_active = True
        user.save()

        return JsonResponse({
            'success': True,
            'message': 'Congratulations! Your account has been activated successfully.',
            'status': 200,
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'profession': user.profession,
                'country': user.country,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat()
            }
        }, status=200)
    else:
        # Token is invalid or expired
        return JsonResponse({
            'success': False,
            'message': 'Invalid or expired activation link. Please request a new verification email.',
            'status': 401,
            'error_type': 'invalid_or_expired_token'
        }, status=401)
# ==================== END OF NEW JSON VERSION ====================





    # New Code written by khilesh (Date - 31_Dec_2024) 
def Admin_verfiy(admin):

    if admin.is_superadmin:
        courses=Course.objects.all()
        userprofile=Account.objects.get(id=admin.id)
    
    elif not admin.is_superadmin and admin.is_staff:
        ta_admin=TeachingAssistant.objects.filter(email=admin.email)
        courses=ta_admin[0].course_set.all()
        userprofile=Account.objects.get(id=admin.id)
    else:
        # Use filter().first() so missing UserProfile won't raise
        userprofile = UserProfile.objects.filter(user_id=admin.id).first()
        # Use timezone-aware datetime to avoid comparison errors
        now = timezone.now()
        
        # 1. Directly enrolled courses
        enrolled_users = EnrolledUser.objects.filter(user=admin, enrolled=True, end_at__gt=now).order_by('-created_at')
        course_ids = [e.course_id for e in enrolled_users]
        
        # Get unique courses
        courses = Course.objects.filter(id__in=list(set(course_ids)))

    
    return [courses,userprofile]





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """
    API endpoint for user dashboard
    Returns JSON response with user profile data and enrolled courses
    Handles different user types: superadmin, staff/TA, and regular users
    Matches Account and UserProfile model fields
    """

    # 🔐 AUTHENTICATION GUARD (FIXED INDENTATION)


    if request.method == 'GET':
        try:
            # Use timezone-aware now to avoid naive/aware datetime errors
            now = datetime.now(timezone.utc)

            # Get user profile and courses based on user type
            courses, userprofile = Admin_verfiy(request.user)
            courses_count = courses.count()

            # Retrieve pending course data from session (from login)
            course_data = request.session.get('course_data', [])

            # Clear the session data after retrieving it
            if 'course_data' in request.session:
                del request.session['course_data']

            # HIDE pending payments for admins/staff
            if request.user.is_superadmin or request.user.is_staff:
                course_data = []

            # Build user profile response
            if isinstance(userprofile, Account):
                # For superadmin and staff
                user_data = {
                    'id': userprofile.id,
                    'first_name': userprofile.first_name,
                    'last_name': userprofile.last_name,
                    'username': userprofile.username,
                    'email': userprofile.email,
                    'phone_number': userprofile.phone_number,
                    'profession': userprofile.profession,
                    'country': userprofile.country,
                    'is_active': userprofile.is_active,
                    'is_staff': userprofile.is_staff,
                    'is_superadmin': userprofile.is_superadmin,
                    'date_joined': userprofile.date_joined.isoformat(),
                    'user_type': 'superadmin' if userprofile.is_superadmin else 'staff'
                }
            else:
                # For regular users — handle missing UserProfile gracefully
                user_data = {
                    'id': request.user.id,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'username': request.user.username,
                    'email': request.user.email,
                    'phone_number': request.user.phone_number,
                    'profession': request.user.profession,
                    'country': request.user.country,
                    'is_active': request.user.is_active,
                    'is_staff': request.user.is_staff,
                    'is_superadmin': request.user.is_superadmin,
                    'date_joined': request.user.date_joined.isoformat(),
                    'user_type': 'user',
                    'profile': {
                        'address_line_1': userprofile.address_line_1 if userprofile else '',
                        'address_line_2': userprofile.address_line_2 if userprofile else '',
                        'city': userprofile.city if userprofile else '',
                        'state': userprofile.state if userprofile else '',
                        'country': userprofile.country if userprofile else '',
                        'postal_code': userprofile.postal_code if userprofile else '',
                        'profile_picture': (
                            userprofile.profile_picture.url if (userprofile and userprofile.profile_picture) else None
                        )
                    }
                }

            # Build courses response with progress data
            courses_list = []
            
            user_categories_subs = {}

            for course in courses:
                # Fetch progress for this course
                progress = OverallProgress.objects.filter(
                    user=request.user,
                    course=course
                ).first()
                
                completion = float(progress.progress) if progress else 0.0
                
                # Fetch enrolled user to get validity and assignments info
                enrolled_user = EnrolledUser.objects.filter(
                    user=request.user,
                    course=course,
                    enrolled=True
                ).first()
                
                # Calculate validity and enrollment type
                validity = "N/A"
                enrollment_type = "purchased"  # Default for regular users

                if request.user.is_superadmin or request.user.is_staff:
                    validity = "Lifetime Admin Access"
                    enrollment_type = "admin_access"
                elif enrolled_user and enrolled_user.end_at and enrolled_user.end_at > now:
                    days_remaining = (enrolled_user.end_at - now).days
                    validity = f"{days_remaining} days"
                elif course.category in user_categories_subs:
                    sub_end_date = user_categories_subs[course.category]
                    if sub_end_date > now:
                        days_remaining = (sub_end_date - now).days
                        validity = f"{days_remaining} days"
                else:
                    validity = "Expired"
                
                courses_list.append({
                    'id': course.id,
                    'title': course.title,
                    'category': course.category,
                    'url_link_name': course.url_link_name,
                    'description': course.description[:200]
                    if hasattr(course, 'description') else None,
                    'completion': completion,
                    'validity': validity,
                    'enrollment_type': enrollment_type,
                    'course_image': request.build_absolute_uri(course.course_image.url) if course.course_image else None,
                    'assignments': course.assignments if hasattr(course, 'assignments') else 0
                })

            return JsonResponse({
                'success': True,
                'message': 'Dashboard data retrieved successfully',
                'status': 200,
                'user': user_data,
                'courses': {
                    'total_count': courses_count,
                    'courses_list': courses_list
                },
                'pending_payments': course_data,
                'timestamp': now.isoformat()
            }, status=200)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Failed to retrieve dashboard data: {str(e)}',
                'status': 500
            }, status=500)

    elif request.method in ['POST', 'PUT', 'DELETE']:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed. Please send a GET request.',
            'status': 405,
            'allowed_methods': ['GET']
        }, status=405)

    else:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed',
            'status': 405
        }, status=405)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Payment_due(request):
    """
    API endpoint to retrieve payment due information for enrolled courses
    """
   
    now = timezone.now()

    enroll_users = EnrolledUser.objects.filter(
        user=request.user,
        enrolled=True,
        end_at__gt=now
    ).select_related("course").distinct("course")

    # HIDE payment due for admins/staff
    if request.user.is_superadmin or request.user.is_staff:
        return JsonResponse({"success": True, "count": 0, "data": []})

    response_data = []

    for enroll_user in enroll_users:

        course = enroll_user.course
        
        user_country = getattr(request.user, 'country', '') or ''
        if user_country.lower() == 'india' or user_country.upper() == 'IN':
            total_fee = Decimal(course.indian_fee or 0)
            currency = '₹'
            currency_code = 'INR'
        else:
            total_fee = Decimal(course.foreign_fee or course.indian_fee or 0)
            currency = '$'
            currency_code = 'USD'
        
        installments = enroll_user.no_of_installments or 1
        per_installment = total_fee / installments if installments > 0 else total_fee
        
        course_duration = course.duration or 6  # Default to 6 months
        second_installment_due_date = enroll_user.created_at + relativedelta(months=max(1, course_duration//3))
        third_installment_due_date = enroll_user.created_at + relativedelta(months=max(1, (2*course_duration)//3))
        second_paid = Decimal(0)
        second_due = Decimal(0)

        if installments >= 2 and not enroll_user.second_installments:
            second_due = per_installment
        elif installments >= 2 and enroll_user.second_installments:
            # If flag=True, payment should exist; fetch it safely
            if enroll_user.installment_id_2:
                payment_2nd = Payment.objects.filter(
                    payment_id=enroll_user.installment_id_2
                ).only("amount_paid").first()
                second_paid = Decimal(payment_2nd.amount_paid) if payment_2nd else per_installment
            else:
                # Flag is True but no payment_id: mark as fully paid
                second_paid = per_installment

        # ✅ FIX 4: Correct logic - if third_installments=False, it's DUE
        third_paid = Decimal(0)
        third_due = Decimal(0)

        if installments == 3 and not enroll_user.third_installments:
            third_due = per_installment
        elif installments == 3 and enroll_user.third_installments:
            # If flag=True, payment should exist; fetch it safely
            if enroll_user.installment_id_3:
                payment_3rd = Payment.objects.filter(
                    payment_id=enroll_user.installment_id_3
                ).only("amount_paid").first()
                third_paid = Decimal(payment_3rd.amount_paid) if payment_3rd else per_installment
            else:
                # Flag is True but no payment_id: mark as fully paid
                third_paid = per_installment

        response_data.append({
            "course_id": course.id,
            "course_title": course.title,
            "no_of_installments": installments,
            "currency": currency,
            "currency_code": currency_code,
            "total_fee": float(total_fee),
            "per_installment": float(per_installment),
            "course_duration_months": course_duration,
            "end_at": enroll_user.end_at.isoformat() if enroll_user.end_at else None,
            "second_installment_paid": float(second_paid),
            "second_installment_due": float(second_due),
            "second_installment_due_date": second_installment_due_date.isoformat() if second_due > 0 else None,
            "third_installment_paid": float(third_paid),
            "third_installment_due": float(third_due),
            "third_installment_due_date": third_installment_due_date.isoformat() if third_due > 0 else None,
        })

    return JsonResponse({
        "success": True,
        "message": "Payment due data retrieved successfully",
        "status": 200,
        "data": response_data,
        "timestamp": now.isoformat()
    }, status=200)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def playlists(request):
    """
    API endpoint for user playlists
    Returns playlists (sections) from enrolled courses
    """

    # if request.method != 'GET':
    #     return JsonResponse({
    #         'success': False,
    #         'message': 'Method not allowed. Please send a GET request.',
    #         'status': 405
    #     }, status=405)

    enrolled_courses = EnrolledUser.objects.filter(
        user=request.user,
        enrolled=True
    ).values_list('course_id', flat=True)

    playlists_list = []
    playlist_id = 1

    for course_id in enrolled_courses:
        sections = Section.objects.filter(course_id=course_id).order_by('id')
        for section in sections:
            assignments_count = Assignment.objects.filter(section=section).count()
            lectures_count = Video.objects.filter(section=section).count() if hasattr(Video, 'section') else 0
            
            playlists_list.append({
                'id': str(playlist_id),
                'title': section.title or section.name,
                'lectures': max(lectures_count, 1),  # At least 1 to match mock data
                'assignments': max(assignments_count, 1)
            })
            playlist_id += 1

    # If no playlists found, return mock data
    if not playlists_list:
        from .data.loggedInData import loggedInData  # Can't import, so use fallback
        playlists_list = [
            {'id': '1', 'title': 'Getting Started', 'lectures': 10, 'assignments': 2},
            {'id': '2', 'title': 'Advanced Topics', 'lectures': 20, 'assignments': 3},
        ]

    return JsonResponse({
        'success': True,
        'message': 'Playlists retrieved successfully',
        'status': 200,
        'playlists': playlists_list,
        'timestamp': datetime.now().isoformat()
    }, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def certificates(request):
    """
    API endpoint for user certificates
    Returns completed courses (completion = 100%) as certificates
    """

    # if request.method != 'GET':
    #     return JsonResponse({
    #         'success': False,
    #         'message': 'Method not allowed. Please send a GET request.',
    #         'status': 405
    #     }, status=405)

    # Get all courses with 100% completion (certificates)
    completed_courses = OverallProgress.objects.filter(
        user=request.user,
        progress=100
    ).select_related('course')

    certificates_list = []
    for progress in completed_courses:
        course = progress.course
        certificates_list.append({
            'id': str(progress.id),
            'title': course.title,
            'completionDate': progress.created_at.strftime('%d %B %y'),
            'grade': '100%',
            'image': course.course_image.url if course.course_image else '',
        })

    # If no certificates, return empty list
    return JsonResponse({
        'success': True,
        'message': 'Certificates retrieved successfully',
        'status': 200,
        'certificates': certificates_list,
        'timestamp': datetime.now().isoformat()
    }, status=200)



# ==================== NEW JSON VERSION ====================
@api_view(['POST'])
@permission_classes([AllowAny])
def forgotPassword(request):
    """
    API endpoint for forgot password email
    Returns JSON response confirming if reset email was sent
    Matches Account model field: email
    """
    # if request.method == 'POST':
    try:
        # data = request.data
        email = request.data.get('email', '').strip()

        # Validation: Check required field
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required',
                'status': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if account with this email exists
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Generate password reset token
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            email_context = {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }

            # Send password reset email
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
            email_context.update({
                'frontend_url': frontend_url,
                'uid': email_context['uid'],
                'token': email_context['token'],
            })

            plain_message = render_to_string('accounts/reset_password_email.txt', email_context)
            html_message = render_to_string('accounts/reset_password_email.html', email_context)
            to_email = email
            from_email = settings.EMAIL_HOST_USER
            send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)

            # Return success response
            return Response({
                'success': True,
                'message': 'Password reset email has been sent to your email address. Please check your inbox.',
                'status': 200,
                'email_sent': True,
                'email': email  # For confirmation display
            }, status=status.HTTP_200_OK)
        else:
            # Account doesn't exist
            return Response({
                'success': False,
                'message': 'Account with this email address does not exist.',
                'status': 404,
                'email_found': False
            }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to send reset email: {str(e)}',
            'status': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ==================== NEW JSON VERSION ====================
def resetpassword_validate(request, uidb64, token):
    """
    API endpoint to validate password reset link
    Returns JSON response confirming if reset token is valid
    Takes URL parameters: uidb64 (user id encoded), token (reset token)
    """
    try:
        # Decode the user ID from the base64 encoded string
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist) as e:
        # Invalid or expired reset link
        return JsonResponse({
            'success': False,
            'message': 'Invalid or expired password reset link',
            'status': 400,
            'error_type': 'invalid_link'
        }, status=400)

    # Verify the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # Token is valid, store in session for next step
        request.session['uid'] = uid
        
        return JsonResponse({
            'success': True,
            'message': 'Password reset link is valid. You can now reset your password.',
            'status': 200,
            'token_valid': True,
            'uid': uid,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=200)
    else:
        # Token is invalid or expired
        return JsonResponse({
            'success': False,
            'message': 'This password reset link has expired or is invalid. Please request a new one.',
            'status': 401,
            'error_type': 'expired_token'
        }, status=401)



@api_view(['POST'])
@permission_classes([AllowAny])
def resetPassword(request):
    """
    API endpoint to reset user password
    Returns JSON response confirming password reset
    Matches Account model field: password
    Expects: password, confirm_password
    """
    try:
        data = request.data
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        uid = data.get('uid', '').strip()

        # Validation: Check required fields
        if not password or not confirm_password:
            return Response({
                'success': False,
                'message': 'Password and confirm password are required',
                'status': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validation: Passwords match
        if password != confirm_password:
            return Response({
                'success': False,
                'message': 'Passwords do not match',
                'status': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validation: Password length (minimum 6 characters)
        if len(password) < 6:
            return Response({
                'success': False,
                'message': 'Password must be at least 6 characters long',
                'status': 400
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get uid from session or request
        if not uid:
            uid = request.session.get('uid', '')
        
        # Also try to get from data if provided by frontend
        if not uid:
            uid = data.get('uid', '')

        if not uid:
            return Response({
                'success': False,
                'message': 'Invalid session. Please request a new password reset link.',
                'status': 401
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Get user and update password
        try:
            # Decode the user ID from the base64 encoded string
            decoded_uid = urlsafe_base64_decode(uid).decode()
            user = Account.objects.get(pk=decoded_uid)
        except (TypeError, ValueError, OverflowError, Account.DoesNotExist):

            return Response({
                'success': False,
                'message': 'User not found',
                'status': 404
            }, status=status.HTTP_404_NOT_FOUND)

        # Set new password
        user.set_password(password)
        user.save()

        # Clear session uid after successful reset
        if 'uid' in request.session:
            del request.session['uid']

        return Response({
            'success': True,
            'message': 'Password has been reset successfully. You can now login with your new password.',
            'status': 200,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Password reset failed: {str(e)}',
            'status': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ==================== END OF NEW JSON VERSION ====================


        enrolled_user=EnrolledUser.objects.filter(user=admin, enrolled=True, end_at__gt=now).order_by('-created_at')



    # New Code written by khilesh (Date - 31_Dec_2024) 
def Admin_courses(admin):
    if admin.is_superadmin:
        courses=Course.objects.all()
    elif admin.is_staff and not admin.is_superadmin:
        ta_admin=TeachingAssistant.objects.filter(email=admin.email)
        courses=ta_admin[0].course_set.all()
    else:
        now = timezone.now()
        
        # 1. Directly enrolled courses
        enrolled_user=EnrolledUser.objects.filter(user=admin, enrolled=True, end_at__gt=now).order_by('-created_at')
        course_ids = [e.course_id for e in enrolled_user]
        
        # Get unique courses
        courses = Course.objects.filter(id__in=list(set(course_ids)))
        
    return courses
    
    



# ==================== NEW JSON VERSION ====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mycourses(request):
    """
    API endpoint for listing user's courses
    Returns JSON response with user's enrolled courses based on user type
    Handles different user types: superadmin, staff/TA, and regular users
    Matches Course model fields
    
    Now returns prices based on user's country:
    - Indian users (country='India' or 'IN'): Shows INR prices (₹)
    - Other users: Shows USD prices ($)
    """
    # 🔐 AUTHENTICATION GUARD (API-SAFE)

    
    if request.method == 'GET':
        try:
            # Use timezone-aware datetime to avoid comparison errors with end_at field
            now = timezone.now()
            
            # Get courses based on user type
            courses = Admin_courses(request.user)
            courses_count = courses.count()
            
            # Determine user country for currency selection
            user_country = getattr(request.user, 'country', '') or ''
            is_indian_user = user_country.lower() == 'india' or user_country.upper() == 'IN'

            # 💎 ADMIN SPECIAL: Show 'Access to all courses' instead of the list
            if request.user.is_superadmin or request.user.is_staff:
                courses_list = [{
                    'id': 0,
                    'title': 'You have access to all courses',
                    'category': 'Admin Access',
                    'url_link_name': None,
                    'price': 0.0,
                    'currency': '₹' if is_indian_user else '$',
                    'currency_code': 'INR' if is_indian_user else 'USD',
                    'purchaseDate': timezone.now().isoformat(),
                    'accessTill': 'Lifetime',
                    'is_admin_access': True,
                    'is_playlist': False,
                    'is_sub_plan': False,
                    'is_subscription': False
                }]
                return JsonResponse({
                    'success': True,
                    'message': 'Admin Access Confirmed',
                    'status': 200,
                    'user_type': 'superadmin' if request.user.is_superadmin else 'staff',
                    'courses': {
                        'total_count': 1,
                        'courses_list': courses_list
                    },
                    'timestamp': datetime.now().isoformat()
                }, status=200)

            # Build courses response for regular users
            courses_list = []
            for course in courses:
                # Check if this course is accessed via subscription vs direct enrollment
                is_sub_course = False
                sub_at_hand = None

                # Set price and currency based on user's country
                if is_indian_user:
                    if is_sub_course and sub_at_hand:
                        course_price = float(sub_at_hand.plan.indian_price or 0)
                    else:
                        course_price = float(course.indian_fee or 0)
                    course_currency = '₹'
                    course_currency_code = 'INR'
                else:
                    if is_sub_course and sub_at_hand:
                        course_price = float(sub_at_hand.plan.foreign_price or 0)
                    else:
                        course_price = float(course.foreign_fee or course.indian_fee or 0)
                    course_currency = '$'
                    course_currency_code = 'USD'
                
                course_data = {
                    'id': course.id,
                    'title': course.title,
                    'category': course.category,
                    'url_link_name': course.url_link_name,
                    'description': course.description if hasattr(course, 'description') else None,
                    # Country-based pricing fields
                    'price': course_price,
                    'currency': course_currency,
                    'currency_code': course_currency_code,
                    'is_subscription': is_sub_course,
                    'original_indian_fee': float(course.indian_fee or 0) if hasattr(course, 'indian_fee') else None,
                    'original_foreign_fee': float(course.foreign_fee or 0) if hasattr(course, 'foreign_fee') else None,
                }
                
                # Add additional fields if they exist in the model
                # if hasattr(course, 'price'):
                #     course_data['price'] = course.price

                if hasattr(course, 'duration'):
                    course_data['duration'] = course.duration
                instructor = course.instructor.first()
                if instructor:
                    course_data['instructor'] = instructor.first_name
                else:
                    course_data['instructor'] = None
                if hasattr(course, 'created_at'):
                    course_data['created_at'] = course.created_at.isoformat()
                if hasattr(course, 'updated_at'):
                    course_data['updated_at'] = course.updated_at.isoformat()
                if hasattr(course, 'is_active'):
                    course_data['is_active'] = course.is_active
                if hasattr(course, 'thumbnail'):
                    course_data['thumbnail'] = course.thumbnail.url if course.thumbnail else None
                
                courses_list.append(course_data)
            
            # Determine user type
            user_type = 'user'
            if request.user.is_superadmin:
                user_type = 'superadmin'
            elif request.user.is_staff:
                user_type = 'staff'
            
            return JsonResponse({
                'success': True,
                'message': 'Courses retrieved successfully',
                'status': 200,
                'user_type': user_type,
                'user_country': user_country or 'Not set',
                'pricing_mode': 'INR' if is_indian_user else 'USD',
                'courses': {
                    'total_count': courses_count,
                    'courses_list': courses_list
                },
                'timestamp': datetime.now().isoformat()
            }, status=200)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Failed to retrieve courses: {str(e)}',
                'status': 500
            }, status=500)

    elif request.method in ['POST', 'PUT', 'DELETE']:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed. Please send a GET request.',
            'status': 405,
            'allowed_methods': ['GET']
        }, status=405)

    else:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed',
            'status': 405
        }, status=405)
# ==================== END OF NEW JSON VERSION ====================
  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    API endpoint to fetch logged-in user's profile
    GET only
    Combines Account + UserProfile models
    """

    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed',
            'status': 405,
            'allowed_methods': ['GET']
        }, status=405)

    user = request.user
    userprofile, created = UserProfile.objects.get_or_create(user=user)

    profile_data = {
        # Account fields
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'name': f"{user.first_name} {user.last_name}",
        'username': user.username,
        'email': user.email,
        'phone': user.phone_number,
        'profession': user.profession,
        'country': user.country,
        'is_active': user.is_active,
        'created_at': user.date_joined.isoformat(),

        # UserProfile fields
        'address': {
            'address_line_1': userprofile.address_line_1,
            'address_line_2': userprofile.address_line_2,
            'city': userprofile.city,
            'state': userprofile.state,
            'country': userprofile.country,
            'postal_code': userprofile.postal_code,
        },
        'profile_picture': (
            userprofile.profile_picture.url
            if userprofile.profile_picture
            else None
        )
    }

    return JsonResponse({
        'success': True,
        'status': 200,
        'data': profile_data
    }, status=200)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    """
    API endpoint for updating user profile
    POST only
    Updates Account + UserProfile fields
    """

    # ---- Parse JSON safely ----
    try:
        import json
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        print("JSON ERROR:", e)
        return JsonResponse(
            {"success": False, "message": "Invalid JSON"},
            status=400
        )

    print("PARSED DATA:", data)

    try:
        user = request.user
        userprofile, created = UserProfile.objects.get_or_create(user=user)

        # ---- Update User fields ----
        if "first_name" in data:
            user.first_name = data["first_name"].strip()

        if "last_name" in data:
            user.last_name = data["last_name"].strip()

        if "phone_number" in data:
            user.phone_number = data["phone_number"].strip()

        if "profession" in data:
            user.profession = data["profession"].strip()

        if "country" in data:
            user.country = data["country"].strip()

        user.save()

        # ---- Update Profile fields ----
        userprofile.address_line_1 = data.get("address_line_1", userprofile.address_line_1)
        userprofile.address_line_2 = data.get("address_line_2", userprofile.address_line_2)
        userprofile.city = data.get("city", userprofile.city)
        userprofile.state = data.get("state", userprofile.state)
        userprofile.country = data.get("country", userprofile.country)
        userprofile.postal_code = data.get("postal_code", userprofile.postal_code)

        userprofile.save()

        return JsonResponse({
            "success": True,
            "message": "Profile updated successfully",
            "data": {
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "profession": user.profession,
                    "country": user.country,
                },
                "profile": {
                    "address_line_1": userprofile.address_line_1,
                    "address_line_2": userprofile.address_line_2,
                    "city": userprofile.city,
                    "state": userprofile.state,
                    "country": userprofile.country,
                    "postal_code": userprofile.postal_code,
                    "profile_picture": (
                        userprofile.profile_picture.url
                        if userprofile.profile_picture else None
                    ),
                },
            }
        }, status=200)

    except Exception as e:
        print("UPDATE ERROR:", e)
        return JsonResponse({
            "success": False,
            "message": f"Failed to update profile: {str(e)}",
        }, status=400)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    """
    API endpoint for uploading user profile picture
    POST only with multipart/form-data
    """

    try:
        userprofile, created = UserProfile.objects.get_or_create(user=request.user)

        # Check if file was uploaded
        if 'profile_picture' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': 'No profile picture uploaded',
                'status': 400
            }, status=400)

        profile_picture = request.FILES['profile_picture']

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if profile_picture.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'message': 'Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed.',
                'status': 400
            }, status=400)

        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if profile_picture.size > max_size:
            return JsonResponse({
                'success': False,
                'message': 'File too large. Maximum size is 5MB.',
                'status': 400
            }, status=400)

        # Delete old profile picture if exists and not default
        if userprofile.profile_picture:
            old_picture = userprofile.profile_picture.path
            if hasattr(userprofile.profile_picture, 'name') and 'default' not in userprofile.profile_picture.name:
                try:
                    import os
                    if os.path.exists(old_picture):
                        os.remove(old_picture)
                except Exception:
                    pass  # Ignore errors deleting old picture

        # Save new profile picture
        userprofile.profile_picture = profile_picture
        userprofile.save()

        return JsonResponse({
            "success": True,
            "message": "Profile picture uploaded successfully",
            "status": 200,
            "data": {
                "profile_picture": userprofile.profile_picture.url if userprofile.profile_picture else None
            }
        }, status=200)

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return JsonResponse({
            "success": False,
            "message": f"Failed to upload profile picture: {str(e)}",
            'status': 500
        }, status=500)


# ==================== END OF NEW JSON VERSION ====================





# ==================== NEW JSON VERSION ====================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    API endpoint for changing user password (logged in users)
    Returns JSON response confirming password change
    Requires current password for verification before change
    Matches Account model field: password
    """
    if request.method == 'POST':
        try:
            import json
            
            # Handle both JSON and form-data requests
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                current_password = data.get('current_password', '').strip()
                new_password = data.get('new_password', '').strip()
                confirm_password = data.get('confirm_password', '').strip()
            else:
                current_password = request.POST.get('current_password', '').strip()
                new_password = request.POST.get('new_password', '').strip()
                confirm_password = request.POST.get('confirm_password', '').strip()

            # Validation: Check required fields
            if not current_password or not new_password or not confirm_password:
                return JsonResponse({
                    'success': False,
                    'message': 'Current password, new password, and confirm password are required',
                    'status': 400
                }, status=400)

            # Validation: New passwords match
            if new_password != confirm_password:
                return JsonResponse({
                    'success': False,
                    'message': 'New password and confirm password do not match',
                    'status': 400
                }, status=400)

            # Validation: New password length (minimum 6 characters)
            if len(new_password) < 6:
                return JsonResponse({
                    'success': False,
                    'message': 'New password must be at least 6 characters long',
                    'status': 400
                }, status=400)

            # Validation: Current password is not same as new password
            if current_password == new_password:
                return JsonResponse({
                    'success': False,
                    'message': 'New password cannot be the same as current password',
                    'status': 400
                }, status=400)

            # Get the current user
            user = Account.objects.get(username__exact=request.user.username)

            # Verify current password is correct
            password_valid = user.check_password(current_password)
            if not password_valid:
                return JsonResponse({
                    'success': False,
                    'message': 'Current password is incorrect',
                    'status': 401
                }, status=401)

            # Set new password
            user.set_password(new_password)
            user.save()

            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Password changed successfully. Please login again with your new password.',
                'status': 200,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'password_changed_at': datetime.now().isoformat()
                },
                'action': 'login_required'  # Frontend should redirect to login
            }, status=200)

        except Account.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found',
                'status': 404
            }, status=404)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Failed to change password: {str(e)}',
                'status': 500
            }, status=500)

    elif request.method == 'GET':
        # Return allowed methods info
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed. Please send a POST request.',
            'status': 405,
            'allowed_methods': ['POST']
        }, status=405)

    else:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed',
            'status': 405
        }, status=405)
# ==================== END OF NEW JSON VERSION ====================

# ==================== TEMPORARY DEBUG ENDPOINT ====================
# This is a temporary debug endpoint to diagnose enrollment issues
# Remove this after fixing the enrollment problems
# @login_required(login_url='login')
# def debug_enrollments(request):
    """
    TEMPORARY DEBUG ENDPOINT - TO BE REMOVED AFTER FIXING ISSUES
    
    This endpoint provides detailed debug information about:
    - User account status
    - All EnrolledUser records (including expired ones)
    - All Order records
    - All Payment records
    - Any data inconsistencies
    """
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed. Please send a GET request.',
            'status': 405,
            'allowed_methods': ['GET']
        }, status=405)

    try:
        user = request.user
        now = timezone.now()
        
        debug_info = {
            'user_info': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superadmin': user.is_superadmin,
                'country': user.country,
                'courses_enrolled_count': getattr(user, 'courses_enrolled', 0),
            },
            'current_time': now.isoformat(),
            'timezone_info': {
                'using': 'django.utils.timezone.now',
                'is_aware': True
            },
            'analysis': {}
        }
        
        # 1. CHECK ALL ENROLLED USER RECORDS
        all_enrolled = EnrolledUser.objects.filter(user=user).order_by('-created_at')
        
        enrolled_data = []
        valid_enrolled = []
        expired_enrolled = []
        
        for enroll in all_enrolled:
            is_valid = enroll.enrolled and enroll.end_at > now
            
            enroll_info = {
                'id': enroll.id,
                'course_id': enroll.course.id if enroll.course else None,
                'course_title': str(enroll.course) if enroll.course else 'UNKNOWN',
                'enrolled': enroll.enrolled,
                'end_at': enroll.end_at.isoformat() if enroll.end_at else None,
                'is_valid_now': is_valid,
                'days_remaining': (enroll.end_at - now).days if enroll.end_at and is_valid else None,
                'no_of_installments': enroll.no_of_installments,
                'first_installments': enroll.first_installments,
                'second_installments': enroll.second_installments,
                'third_installments': enroll.third_installments,
                'created_at': enroll.created_at.isoformat() if enroll.created_at else None,
            }
            
            enrolled_data.append(enroll_info)
            
            if is_valid:
                valid_enrolled.append(enroll_info)
            else:
                expired_enrolled.append(enroll_info)
        
        debug_info['enrolled_users'] = {
            'total_count': all_enrolled.count(),
            'valid_count': len(valid_enrolled),
            'expired_or_invalid_count': len(expired_enrolled),
            'valid_enrollments': valid_enrolled,
            'expired_enrollments': expired_enrolled
        }
        
        # 2. CHECK ALL ORDER RECORDS
        orders = Order.objects.filter(user=user).order_by('-created_at')
        
        order_data = []
        completed_orders = []
        pending_orders = []
        
        for order in orders:
            order_info = {
                'id': order.id,
                'order_number': order.order_number,
                'course_id': order.course.id if order.course else None,
                'course_title': str(order.course) if order.course else 'UNKNOWN',
                'total_amount': order.total_amount,
                'is_ordered': order.is_ordered,
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None,
            }
            
            order_data.append(order_info)
            
            if order.is_ordered:
                completed_orders.append(order_info)
            else:
                pending_orders.append(order_info)
        
        debug_info['orders'] = {
            'total_count': orders.count(),
            'completed_count': len(completed_orders),
            'pending_count': len(pending_orders),
            'completed_orders': completed_orders,
            'pending_orders': pending_orders
        }
        
        # 3. CHECK ALL PAYMENT RECORDS
        payments = Payment.objects.filter(user=user).order_by('-created_at')
        
        payment_data = []
        completed_payments = []
        
        for payment in payments:
            payment_info = {
                'id': payment.id,
                'payment_id': payment.payment_id,
                'amount_paid': payment.amount_paid,
                'status': payment.status,
                'payment_method': payment.payment_method,
                'created_at': payment.created_at.isoformat() if payment.created_at else None,
            }
            
            payment_data.append(payment_info)
            
            if payment.status == 'Completed':
                completed_payments.append(payment_info)
        
        debug_info['payments'] = {
            'total_count': payments.count(),
            'completed_count': len(completed_payments),
            'completed_payments': completed_payments
        }
        
        # 4. ANALYSIS: FIND MISMATCHES
        issues = []
        
        # Check: Orders without enrollment
        order_course_ids = set(o['course_id'] for o in completed_orders if o['course_id'])
        enrolled_course_ids = set(e['course_id'] for e in valid_enrolled if e['course_id'])
        
        missing_enrollments = order_course_ids - enrolled_course_ids
        if missing_enrollments:
            issues.append({
                'type': 'COMPLETED_ORDERS_WITHOUT_VALID_ENROLLMENT',
                'description': 'Orders exist but no valid enrollment record found',
                'course_ids': list(missing_enrollments),
                'severity': 'HIGH'
            })
        
        # Check: Valid enrollments without orders
        orphaned_enrollments = enrolled_course_ids - order_course_ids
        if orphaned_enrollments:
            issues.append({
                'type': 'VALID_ENROLLMENTS_WITHOUT_ORDERS',
                'description': 'Valid enrollment exists but no order found',
                'course_ids': list(orphaned_enrollments),
                'severity': 'MEDIUM'
            })
        
        # Check: Expired enrollments
        if expired_enrolled:
            issues.append({
                'type': 'EXPIRED_ENROLLMENTS',
                'description': 'Some enrollments have expired',
                'count': len(expired_enrolled),
                'severity': 'LOW'
            })
        
        # Check: User courses_enrolled count mismatch
        actual_count = len(valid_enrolled)
        stored_count = getattr(user, 'courses_enrolled', 0)
        if actual_count != stored_count:
            issues.append({
                'type': 'COUNT_MISMATCH',
                'description': 'User.courses_enrolled does not match actual valid enrollment count',
                'stored_count': stored_count,
                'actual_count': actual_count,
                'severity': 'LOW'
            })
        
        debug_info['analysis'] = {
            'issues_found': len(issues),
            'issues': issues,
            'summary': {
                'total_orders': orders.count(),
                'total_payments': payments.count(),
                'total_enrollments': all_enrolled.count(),
                'valid_enrollments': len(valid_enrolled),
                'user_stored_course_count': stored_count
            }
        }
        
        # 5. WHAT MYCOURSES ENDPOINT WOULD RETURN
        if user.is_superadmin:
            courses_qs = Course.objects.all()
            visible_courses_count = courses_qs.count()
        elif user.is_staff:
            ta_admin = TeachingAssistant.objects.filter(email=user.email)
            if ta_admin.exists():
                courses_qs = ta_admin[0].course_set.all()
                visible_courses_count = courses_qs.count()
            else:
                courses_qs = Course.objects.none()
                visible_courses_count = 0
        else:
            # Regular user - only sees VALID enrollments
            courses_qs = Course.objects.filter(
                id__in=[e['course_id'] for e in valid_enrolled if e['course_id']]
            )
            visible_courses_count = courses_qs.count()
        
        debug_info['mycourses_simulation'] = {
            'user_type': 'superadmin' if user.is_superadmin else ('staff' if user.is_staff else 'regular_user'),
            'courses_visible_to_user': visible_courses_count,
            'note': 'Regular users only see courses with valid (non-expired) enrollments'
        }
        
        # 6. RECOMMENDATIONS
        recommendations = []
        
        if missing_enrollments:
            recommendations.append({
                'issue': 'Missing enrollment records',
                'action': 'Create EnrolledUser records for completed orders',
                'api': '/courses/place_order_mannualy/'
            })
        
        if orphaned_enrollments:
            recommendations.append({
                'issue': 'Orphaned enrollments',
                'action': 'Verify these enrollments are intentional or create orders',
            })
        
        if expired_enrolled:
            recommendations.append({
                'issue': 'Expired enrollments',
                'action': 'Extend end_at date if payments were completed',
            })
        
        debug_info['recommendations'] = recommendations
        
        return JsonResponse({
            'success': True,
            'message': 'Debug enrollment data retrieved successfully',
            'status': 200,
            'debug': debug_info,
            'note': 'This is a temporary debug endpoint. Remove after fixing issues.',
            'timestamp': now.isoformat()
        }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Debug failed: {str(e)}',
            'status': 500,
            'error_type': type(e).__name__
        }, status=500)

# ==================== END OF TEMPORARY DEBUG ENDPOINT ====================


# ============================================================
# Payment History Endpoint
# ============================================================
# Purpose: Get payment history for a specific course enrollment
# Route: GET /accounts/payment_history/{course_id}/
# Returns: All payments made for that course with details
# Added: 10 Feb 2026
# ============================================================

def generate_invoice_for_payment(payment_id, course_id, order_id, installment_number=None):
    """
    Helper function to generate and send invoice for a completed payment
    Called from payment_verify webhook
    
    Parameters:
    - payment_id: Razorpay payment ID
    - course_id: Course ID
    - order_id: Order ID
    - installment_number: Which installment (1, 2, or 3)
    
    Returns: True if successful, False otherwise
    """
    try:
        from django.template.loader import render_to_string
        from django.core.mail import EmailMessage
        from course.models import Order, Course
        from django.conf import settings
        
        # Get order and payment details
        order = Order.objects.filter(id=order_id).first()
        if not order:
            print(f"⚠️ Order {order_id} not found for invoice generation")
            return False
        
        payment = Payment.objects.filter(payment_id=payment_id).first()
        if not payment:
            print(f"⚠️ Payment {payment_id} not found for invoice generation")
            return False
        
        # Get enrollment for installment info
        enrollment = EnrolledUser.objects.filter(user=order.user, course_id=course_id).first()
        if not enrollment:
            print(f"⚠️ Enrollment not found for invoice generation")
            return False
        
        # Determine installment text
        installment_text = "Payment Received"
        if installment_number:
            if installment_number == 1:
                installment_text = f"First installment paid (1 of {enrollment.no_of_installments})"
            elif installment_number == 2:
                installment_text = f"Second installment paid (2 of {enrollment.no_of_installments})"
            elif installment_number == 3:
                installment_text = f"Final installment paid ({enrollment.no_of_installments} of {enrollment.no_of_installments})"
        
        # Get course
        course = Course.objects.filter(id=course_id).first()
        course_name = course.title if course else "Unknown Course"
        
        # Prepare email
        mail_list = ['sunil.roat@deepeigen.com']
        
        title_heading = "Payment Received" if installment_number and installment_number > 1 else "New User Enrollment"
        top_heading = f"A user has successfully paid for {course_name}." if installment_number and installment_number > 1 else f"A new user has enrolled in {course_name}."
        
        mail_subject = f"Invoice Generated - {course_name} - Payment {installment_number or 1}"
        
        message = render_to_string('invoice/invoice_mail.html', {
            'title_heading': title_heading,
            'top_heading': top_heading,
            'firstname': order.first_name,
            'lastname': order.last_name,
            'course': course_name,
            'orderid': payment_id,
            'installment_info': installment_text
        })
        
        email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER, mail_list)
        email.content_subtype = "html"
        email.send()
        
        print(f"✅ Invoice email sent for payment {payment_id} (Installment {installment_number or 1})")
        return True
        
    except Exception as e:
        print(f"⚠️ Error generating invoice for payment {payment_id}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request, course_id):
    """
    API endpoint to retrieve payment history for a specific course or custom playlist
    """
    try:
        from course.models import Course, EnrolledUser, Payment

        # ---------------- ORIGINAL COURSE LOGIC ----------------
        # ---------------- GET COURSE ----------------
        course = Course.objects.filter(id=course_id).first()
        if not course:
            return JsonResponse({"success": False}, status=404)

        # ---------------- GET ENROLLMENT ----------------
        enrollment = EnrolledUser.objects.filter(
            user=request.user,
            course=course,
            enrolled=True
        ).first()

        if not enrollment:
            # For admins, return a successful but empty history if no real enrollment exists
            if request.user.is_superadmin or request.user.is_staff:
                return JsonResponse({
                    "success": True, 
                    "message": "Admin view: No purchase required", 
                    "payments": []
                })
            return JsonResponse({"success": False, "message": "No active enrollment found"}, status=403)

        # ---------------- CURRENCY ----------------
        user_country = (getattr(request.user, 'country', '') or '').upper()

        if user_country in ["INDIA", "IN"]:
            currency = "₹"
            currency_code = "INR"
            total_fee = enrollment.course.indian_fee or 0
        else:
            currency = "$"
            currency_code = "USD"
            total_fee = enrollment.course.foreign_fee or enrollment.course.indian_fee or 0

        # ---------------- COLLECT PAYMENTS ----------------
        payments = []

        # 1st installment
        if enrollment.payment and enrollment.payment.status.capitalize() == "Completed":
            payments.append(enrollment.payment)

        # 2nd installment
        if enrollment.installment_id_2:
            p2 = Payment.objects.filter(
                user=request.user,
                payment_id=enrollment.installment_id_2,
                status__iexact="Completed"
            ).first()
            if p2:
                payments.append(p2)

        # 3rd installment
        if enrollment.installment_id_3:
            p3 = Payment.objects.filter(
                user=request.user,
                payment_id=enrollment.installment_id_3,
                status__iexact="Completed"
            ).first()
            if p3:
                payments.append(p3)

        # ---------------- BUILD RESPONSE ----------------
        payment_list = []
        total_paid = 0

        if payments:
            for idx, payment in enumerate(payments):
                if enrollment.payment and enrollment.payment.id == payment.id:
                    installment_num = 1
                elif enrollment.installment_id_2 == payment.payment_id:
                    installment_num = 2
                elif enrollment.installment_id_3 == payment.payment_id:
                    installment_num = 3
                else:
                    installment_num = idx + 1

                payment_amount = float(payment.amount_paid or 0)
                total_paid += payment_amount

                order = enrollment.order
                order_number = order.order_number if order else "None"
                order_id = order.id if order else None

                payment_list.append({
                    "invoice_id": idx + 1,
                    "order_id": order_id,
                    "payment_id": payment.payment_id,
                    "payment_method": payment.payment_method or "unknown",
                    "currency": currency,
                    "currency_code": currency_code,
                    "status": payment.status.lower() if payment.status else "pending",
                    "installment_number": installment_num,
                    "no_of_installments": enrollment.no_of_installments,
                    "download_url": f"/accounts/invoice/{payment.payment_id}/{course_id}/{order_number}/",
                    "amount": round(payment_amount, 2),
                    "paid_at": payment.created_at.isoformat() if payment.created_at else None
                })
        elif enrollment.enrolled:
            # Virtual row fallback for courses with no linked payment records
            payment_list.append({
                "invoice_id": 1,
                "order_id": enrollment.order.id if enrollment.order else None,
                "payment_id": enrollment.payment.payment_id if enrollment.payment else "Manual",
                "payment_method": "enrollment",
                "currency": currency,
                "currency_code": currency_code,
                "status": "completed",
                "installment_number": 1,
                "no_of_installments": enrollment.no_of_installments or 1,
                "download_url": f"/accounts/invoice/{enrollment.payment.payment_id}/{course_id}/{enrollment.order.order_number}/" if enrollment.payment and enrollment.order else "#",
                "amount": float(total_fee),
                "paid_at": enrollment.created_at.isoformat() if enrollment.created_at else None
            })
            total_paid = float(total_fee)

        payment_list.sort(key=lambda x: x["installment_number"])
        
        # Force remaining due to 0 if all installments are paid
        # This handles small rounding differences (e.g. 19666.66 * 3 = 58999.98)
        is_fully_paid = enrollment.no_of_installments and len(payment_list) >= enrollment.no_of_installments
        
        if is_fully_paid:
            remaining_due = 0.0
            display_total_paid = float(total_fee)
        else:
            remaining_due = max(0, float(total_fee) - total_paid)
            display_total_paid = total_paid

        return JsonResponse({
            "success": True,
            "data": {
                "course_id": course_id,
                "course_name": course.title,
                "total_fee": round(float(total_fee), 2),
                "total_paid": round(display_total_paid, 2),
                "remaining_due": round(remaining_due, 2),
                "currency": currency,
                "currency_code": currency_code,
                "no_of_installments": enrollment.no_of_installments,
                "payments": payment_list
            }
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)
    

#added 13 feb 26 vikas
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_watch(request):
    """
    API endpoint for user's most recently watched video OR last accessed course
    Returns the video details with course and section information
    If no video progress, returns the last accessed course from session
    """
    # if not request.user.is_authenticated:
    #     return JsonResponse({
    #         'success': False,
    #         'message': 'Authentication required',
    #         'status': 403
    #     }, status=403)

    # if request.method != 'GET':
    #     return JsonResponse({
    #         'success': False,
    #         'message': 'Method not allowed. Please send a GET request.',
    #         'status': 405
    #     }, status=405)

    recent_progress = UserVideoProgress.objects.filter(
        user=request.user
    ).select_related('video', 'course', 'section').order_by('-created_at').first()

    if recent_progress:
        video = recent_progress.video
        course = recent_progress.course
        section = recent_progress.section

        module = video.module if video else None
        module_name = module.title if module and hasattr(module, 'title') else module.name if module and hasattr(module, 'name') else ''

        recent_watch_data = {
            'id': recent_progress.id,
            'video_id': video.id if video else None,
            'video_title': video.title if video else '',
            'video_link': video.link if video else '',
            'video_duration': video.duration if video else '',
            'course_id': course.id if course else None,
            'course_title': course.title if course else '',
            'course_url': course.url_link_name if course else '',
            'section_id': section.id if section else None,
            'section_title': section.title if section else section.name if section else '',
            'section_url': section.url_name if section else '',
            'module_name': module_name,
            'completed': recent_progress.completed,
            'watched_at': recent_progress.created_at.isoformat() if recent_progress.created_at else None,
        }

        return JsonResponse({
            'success': True,
            'message': 'Recent watch data retrieved successfully',
            'status': 200,
            'recent_watch': recent_watch_data,
            'timestamp': datetime.now().isoformat()
        }, status=200)

    last_accessed_course_id = request.session.get('last_accessed_course_id')
    last_accessed_course_title = request.session.get('last_accessed_course_title')
    last_accessed_course_url = request.session.get('last_accessed_course_url')
    last_accessed_at = request.session.get('last_accessed_at')

    if last_accessed_course_id:
        recent_watch_data = {
            'id': None,
            'video_id': None,
            'video_title': None,
            'video_link': None,
            'video_duration': None,
            'course_id': last_accessed_course_id,
            'course_title': last_accessed_course_title,
            'course_url': last_accessed_course_url,
            'section_id': None,
            'section_title': None,
            'section_url': 'overview',
            'module_name': None,
            'completed': False,
            'watched_at': last_accessed_at,
        }

        return JsonResponse({
            'success': True,
            'message': 'Last accessed course retrieved from session',
            'status': 200,
            'recent_watch': recent_watch_data,
            'timestamp': datetime.now().isoformat()
        }, status=200)

    return JsonResponse({
        'success': True,
        'message': 'No recent watch history found',
        'status': 200,
        'recent_watch': None,
        'timestamp': datetime.now().isoformat()
    }, status=200)





#added 13 feb vikas
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_last_accessed_course(request):
    """
    API endpoint to track the last accessed course
    When user visits a course, this saves the course as last accessed course
    """
    # if not request.user.is_authenticated:
    #     return JsonResponse({
    #         'success': False,
    #         'message': 'Authentication required',
    #         'status': 403
    #     }, status=403)

    # if request.method != 'POST':
    #     return JsonResponse({
    #         'success': False,
    #         'message': 'Method not allowed. Please send a POST request.',
    #         'status': 405
    #     }, status=405)

    try:
        import json
        data = json.loads(request.body)
        
        course_id = data.get('course_id')
        
        if not course_id:
            return JsonResponse({
                'success': False,
                'message': 'course_id is required',
                'status': 400
            }, status=400)
        
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Course not found',
                'status': 404
            }, status=404)
        
        request.session['last_accessed_course_id'] = course_id
        request.session['last_accessed_course_title'] = course.title
        request.session['last_accessed_course_url'] = course.url_link_name
        request.session['last_accessed_at'] = datetime.now().isoformat()
        
        return Response({
            'success': True,
            'message': 'Last accessed course updated',
            'status': 200,
            'data': {
                'course_id': course.id,
                'course_title': course.title,
                'course_url': course.url_link_name,
            },
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error tracking course: {str(e)}',
            'status': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Invoice_section(request):

    # HIDE invoices for admins/staff
    if request.user.is_superadmin or request.user.is_staff:
        return JsonResponse({"success": True, "data": []})

    enrollments = EnrolledUser.objects.filter(
        user=request.user,
        enrolled=True
    ).select_related("course", "payment")

    data = []

    user_country = (getattr(request.user, "country", "") or "").upper()
    is_indian = user_country in ["INDIA", "IN"]

    currency = "₹" if is_indian else "$"
    currency_code = "INR" if is_indian else "USD"

    for enroll in enrollments:

        payment_ids = []

        if enroll.payment:
            payment_ids.append(enroll.payment.payment_id)

        if enroll.installment_id_2:
            payment_ids.append(enroll.installment_id_2)

        if enroll.installment_id_3:
            payment_ids.append(enroll.installment_id_3)

        payments = Payment.objects.filter(
            payment_id__in=payment_ids,
            status="Completed"
        ).order_by("-created_at")

        for payment in payments:

            if enroll.payment and enroll.payment.payment_id == payment.payment_id:
                installment_number = 1
            elif enroll.installment_id_2 == payment.payment_id:
                installment_number = 2
            elif enroll.installment_id_3 == payment.payment_id:
                installment_number = 3
            else:
                installment_number = 1

            data.append({
                "invoice_id": payment.id,
                "payment_id": payment.payment_id,
                "order_id": enroll.order.razorpay_order_id if enroll.order else None, # Added for frontend status checks
                "course_id": enroll.course.id,
                "date": payment.created_at.isoformat(),
                "created_at": payment.created_at.isoformat(),
                "end_at": enroll.end_at.isoformat() if getattr(enroll, 'end_at', None) else None,
                # "amount": float(payment.amount_paid),
                "amount_paid": float(payment.amount_paid or 0),
                "status": "paid",
                "download_url": f"/accounts/invoice/{payment.payment_id}/{enroll.course.id}/None/",
                "currency": currency,
                "currency_code": currency_code,
                "installment_number": installment_number,
                "no_of_installments": enroll.no_of_installments,
                "course": enroll.course.title,
            })

    pass

    return JsonResponse({
        "success": True,
        "data": data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_status(request, order_id):
    """
    Check if an invoice is ready for download based on order/payment status.
    """
    from course.models import Order
    
    order = Order.objects.filter(
        Q(razorpay_order_id=order_id) | Q(order_number=order_id),
        user=request.user
    ).first()

    if order:
        if order.status == 'Completed' or order.is_ordered:
            return JsonResponse({
                "success": True,
                "can_download": True,
                "message": "Invoice is ready",
                "invoice_status": "ready"
            })
        else:
            return JsonResponse({
                "success": False,
                "can_download": False,
                "message": f"Order status is {order.status}. Payment might be pending.",
                "invoice_status": "pending_payment"
            })

    return JsonResponse({
        "success": False,
        "can_download": False,
        "message": "Order record not found",
        "invoice_status": "not_found"
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Invoice(request, payment_id, course_id, orderNumber):
    from course.models import Order
    # Get enrollment
    enrollment = EnrolledUser.objects.filter(
        user=request.user,
        course_id=course_id,
        enrolled=True
    ).first()

    if not enrollment:
        print(f"DEBUG 404: Enrollment not found for user {request.user.email} and course {course_id}")
        return JsonResponse({"success": False, "message": "Enrollment not found"}, status=404)

    # Get payment
    payment = Payment.objects.filter(
        user=request.user,
        payment_id=payment_id,
        status="Completed"
    ).first()

    if not payment:
        print(f"DEBUG 404: Payment not found for user {request.user.email} and payment_id {payment_id}")
        return JsonResponse({"success": False, "message": "Payment not found"}, status=404)

    # Detect installment number
    if enrollment.payment and enrollment.payment.payment_id == payment.payment_id:
        installment_number = 1
    elif enrollment.installment_id_2 == payment.payment_id:
        installment_number = 2
    elif enrollment.installment_id_3 == payment.payment_id:
        installment_number = 3
    else:
        installment_number = 1

    # Get order
    order = None
    if orderNumber and orderNumber != "None":
        order = Order.objects.filter(order_number=orderNumber, user=request.user).first()
    
    if not order:
        order = Order.objects.filter(
            payment__payment_id=payment_id,
            user=request.user
        ).first()

    if not order or getattr(order, 'address', '') == "Installment Payment" or getattr(order, 'state', '') == "Online":
        # Fallback to enrollment order (first payment / original order)
        better_order = enrollment.order
        if better_order and better_order.address != "Installment Payment" and better_order.state != "Online":
            order = better_order
        elif not order:
            order = enrollment.order
    
    if not order or getattr(order, 'address', '') == "Installment Payment":
        # Final fallback: search for ANY order for this user and course that has a real address
        fallback_order = Order.objects.filter(
            user=request.user, 
            course_id=course_id
        ).exclude(address="Installment Payment").exclude(state="Online").first()
        if fallback_order:
            order = fallback_order

    if not order:
        print(f"DEBUG 404: Order not found for payment_id {payment_id} or orderNumber {orderNumber}")
        return JsonResponse({"success": False, "message": "Order details not found for invoice"}, status=404)

    # ✅ REGENERATION FORCED: Temporarily bypassing stored invoice check to sync designs
    # invoice_reg = Invoice_Registrant.objects.filter(
    #     name=enrollment,
    #     order=order
    # ).first()
    # 
    # if invoice_reg and invoice_reg.invoice:
    #     try:
    #         return FileResponse(invoice_reg.invoice.open('rb'), content_type="application/pdf")
    #     except:
    #         pass 

    # Determine currency
    user_country = (getattr(request.user, "country", "") or "").upper()
    is_indian = user_country in ["INDIA", "IN"]

    # Build PDF dynamically
    try:
        pdf_content = generate_professional_invoice(order, enrollment, payment, installment_number)
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="Invoice-{payment.payment_id}.pdf"'
        response['Content-Length'] = len(pdf_content)
        return response
    except Exception as e:
        import traceback
        print(f"❌ Invoice generation error for payment {payment_id}:")
        print(traceback.format_exc())
        return JsonResponse({
            "success": False, 
            "message": "Error generating invoice PDF",
            "error": str(e)
        }, status=500)






def Invoice_manual(request, userId, payment_id, course_id, orderNumber):

    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"success": False}, status=403)

    from django.contrib.auth import get_user_model
    User = get_user_model()

    user = User.objects.filter(id=userId).first()
    if not user:
        return JsonResponse({"success": False}, status=404)

    enroll = EnrolledUser.objects.filter(
        user=user,
        course=course_id
    ).first()

    if not enroll:
        return JsonResponse({"success": False}, status=404)

    payment = Payment.objects.filter(
        user=user,
        payment_id=payment_id
    ).first()

    if not payment or payment.status != "Completed":
        return JsonResponse({"success": False}, status=400)

    # Call same Invoice logic but impersonate user
    request.user = user
    return Invoice(request, payment_id, course_id, orderNumber)

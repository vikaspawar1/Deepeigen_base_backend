from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from course.models import Course, Section, EnrolledUser
from accounts.models import Account
from .models import Question, Reply, SubReply
from django.contrib.auth.decorators import login_required
from utils.decorators import api_login_required

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Q

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_exempt



def installment_Checker(enrolled_user,course):
     if enrolled_user and enrolled_user.no_of_installments >1:
        count= course.section_set.all().count()
        if enrolled_user.no_of_installments==2:
            if enrolled_user.second_installments!=True:
              sections=course.section_set.all().order_by('id')[0:int(count/2)]
            else:
                sections=course.section_set.all().order_by('id')
            
        elif enrolled_user.no_of_installments==3:
            if enrolled_user.second_installments!=True:
                sections=course.section_set.all().order_by('id')[0:int(count/3)]
            elif enrolled_user.second_installments==True and enrolled_user.third_installments!=True:
                sections=course.section_set.all().order_by('id')[0:int(2*count/3)]
            else:
                sections=course.section_set.all().order_by('id')
     else:
         sections=course.section_set.all().order_by('id')

     return sections




def Admin_access_discussion_forum(admin,course):
    if admin.is_superadmin or admin.is_staff:
        enrolled_user=Account.objects.filter(id=admin.id)[0]
        sections=course.section_set.all().order_by('id')
    else:
        enrolled_user= EnrolledUser.objects.filter(course_id=course.id, user=admin, enrolled=True, end_at__gt=timezone.now()).first()
        sections=installment_Checker(enrolled_user,course)
    
    return (sections,enrolled_user)



# @login_required(login_url='login')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def discussion_forum(request, id, course_url):
    course = get_object_or_404(Course, pk=id, url_link_name=course_url)

    sections, enrolled_user = Admin_access_discussion_forum(request.user, course)

    sections_data = []
    for section in sections:
        sections_data.append({
            "id": section.id,
            "name": section.name,
            "url": section.url_name
        })

    return JsonResponse({
        "success": True,
        "course": {
            "id": course.id,
            "title": course.title,
            "slug": course.url_link_name
        },
        "sections": sections_data,
        "enrolled_user": {
            "id": enrolled_user.id if enrolled_user else None,
            "is_admin": request.user.is_staff or request.user.is_superadmin
        },
        "canonical_url": request.build_absolute_uri(request.path)
    }
    )


#10 feb chnage code 
# @login_required(login_url='login')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_forum(request, id, course_url, section_url):
    course = get_object_or_404(Course, pk=id, url_link_name=course_url)
    sections, enrolled_user = Admin_access_discussion_forum(request.user, course)
    section = get_object_or_404(Section, course_id=id, url_name=section_url)

    # Show all approved questions + user's own unapproved questions
    # This allows users to see their newly created posts immediately
    questions = Question.objects.filter(
        course_id=id,
        section_id=section.id
    ).filter(
        Q(approval_flag=True) | Q(user=request.user)
    ).order_by('-id')

    # filters
    if request.GET.get('sort') == 'top':
        questions = questions.order_by('id')

    if request.GET.get('filter') == 'byyou':
        questions = questions.filter(user=request.user)

    # pagination
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    questions_data = []
    for q in page_obj:
        # Get replies with sub_replies - show approved replies + user's own unapproved replies
        replies = q.reply_set.filter(
            Q(approval_flag=True) | Q(user=request.user)
        ).order_by('-id')
        replies_data = []
        for r in replies:
            # Get subreplies - show approved subreplies + user's own unapproved subreplies
            sub_replies = r.subreply_set.filter(
                Q(approval_flag=True) | Q(user=request.user)
            )
            sub_replies_data = []
            for sr in sub_replies:
                sub_replies_data.append({
                    "id": sr.id,
                    "sub_reply": sr.sub_reply,
                    "user_name": sr.user.first_name if sr.user else sr.user.username if sr.user else "User",
                    "user_email": sr.user.email if sr.user else "",
                    "created_date": sr.created_date
                })
            replies_data.append({
                "id": r.id,
                "reply": r.reply,
                "user_name": r.user.first_name if r.user else r.user.username if r.user else "User",
                "user_email": r.user.email if r.user else "",
                "created_date": r.created_date,
                "sub_replies": sub_replies_data
            })
        
        questions_data.append({
            "id": q.id,
            "title": q.title,
            "question": q.question,
            "user_name": q.user.first_name if q.user else q.user.username if q.user else "User",
            "user_email": q.user.email if q.user else "",
            "created_date": q.created_date,
            "reply_count": q.reply_set.filter(approval_flag=True).count(),
            "replies": replies_data,
            "week": f"Week {section.week_number}" if hasattr(section, 'week_number') else section.name
        })

    return JsonResponse({
        "success": True,
        "course": {
            "id": course.id,
            "title": course.title,
            "slug": course.url_link_name
        },
        "section": {
            "id": section.id,
            "name": section.name,
            "slug": section.url_name
        },
        "questions": questions_data,
        "pagination": {
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }
    })





# @login_required(login_url='login')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request, id, course_url, section_url):
    course = get_object_or_404(Course, pk=id, url_link_name=course_url)
    teaching_assistants = course.teaching_assistant.all().values_list('email')
    ta_list = [ta[0] for ta in teaching_assistants]
    
    # Check if this is an AJAX/API request - DRF handle this mostly, but keeping for logic
    is_ajax = True 

    if request.method == 'POST':
        # Use DRF's request.data (already parsed — avoids "cannot access body after reading stream" error)
        title = request.data.get('title') or request.POST.get('title')
        question_text = request.data.get('question') or request.POST.get('question')
        section_id = request.data.get('section_id') or request.POST.get('section_id')
        
        if not title or not question_text or not section_id:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Title, question, and section_id are required'}, status=400)
            return HttpResponseBadRequest('Title, question, and section_id are required')
        
        # Log each field for debugging
        print("Title:", title)
        print("Question:", question_text)
        print("Section ID:", section_id)
        
        new_question = Question(
                            title = title,
                            question = question_text,
                            section_id = section_id,
                            user = request.user,
                            course_id = course.id
                        )
        
        new_question.save()
        
        all_questions = Question.objects.all()
        print("All Questions in the Database:")
        for q in all_questions:
            print(f"ID: {q.id}")
            print(f"Title: {q.title}")
            print(f"Question: {q.question}")
            print(f"Section ID: {q.section_id}")
            print(f"User: {q.user}")
            print(f"Course ID: {q.course_id}")
            print(f"Created At: {q.created_date}")
        
        # Send email notification (skip if template doesn't exist)
        try:
            mail_subject = "A New Question has been asked by {}".format(request.user.email)
            message = render_to_string('discussion_forum/question_notification_email.html', {
                    'user_email': request.user.email,
                    'course_title': course.title,
                    'section': Section.objects.get(pk=section_id)
                })
            send_email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER ,to=ta_list)
            send_email.send()
        except Exception as email_error:
            print(f"Failed to send email notification: {email_error}")
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Your response has been submitted successfully!',
                'question': {
                    'id': new_question.id,
                    'title': new_question.title,
                    'question': new_question.question,
                    'user_name': new_question.user.first_name if new_question.user else new_question.user.username if new_question.user else "User",
                    'user_email': new_question.user.email if new_question.user else "",
                    'created_date': new_question.created_date.isoformat() if new_question.created_date else "",
                    'reply_count': 0,
                    'replies': [],
                    'week': f"Week {Section.objects.get(pk=section_id).week_number}" if hasattr(Section.objects.get(pk=section_id), 'week_number') else Section.objects.get(pk=section_id).name
                }
            })
        
        messages.success(request, 'Your response has been submitted successfully, our team will resolve your query!')
        return redirect('weekly_forum', id, course_url, section_url)
    else:
       # if other than POST request is made.
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Only POST method is allowed'}, status=405)
        return HttpResponseBadRequest()





# @login_required(login_url='login')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def question_search(request, id, course_url, section_url):
    print("question_search__lucky")

    now = timezone.now()
    course = get_object_or_404(Course, pk=id, url_link_name=course_url)
    sections,enrolled_user=Admin_access_discussion_forum(request.user,course)
    section = get_object_or_404(Section, course_id=id, url_name=section_url)
    
    # Check if this is an AJAX/API request
    is_ajax = True
    
    # Show all approved questions + user's own unapproved questions
    # This allows users to search their own newly created posts
    questions = Question.objects.filter(
        course_id=id, 
        section_id=section.id
    ).filter(
        Q(approval_flag=True) | Q(user=request.user)
    ).order_by('-id')
    
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            questions = questions.filter(Q(title__icontains=keyword) | Q(question__icontains=keyword))
    print("Question hai bhai___", questions)
    
    if is_ajax:
        # Return JSON response for API calls
        questions_data = []
        for q in questions:
            # Get replies - show approved replies + user's own unapproved replies
            replies = q.reply_set.filter(
                Q(approval_flag=True) | Q(user=request.user)
            ).order_by('-id')
            replies_data = []
            for r in replies:
                # Get subreplies - show approved subreplies + user's own unapproved subreplies
                sub_replies = r.subreply_set.filter(
                    Q(approval_flag=True) | Q(user=request.user)
                )
                sub_replies_data = []
                for sr in sub_replies:
                    sub_replies_data.append({
                        "id": sr.id,
                        "sub_reply": sr.sub_reply,
                        "user_name": sr.user.first_name if sr.user else sr.user.username if sr.user else "User",
                        "user_email": sr.user.email if sr.user else "",
                        "created_date": sr.created_date
                    })
                replies_data.append({
                    "id": r.id,
                    "reply": r.reply,
                    "user_name": r.user.first_name if r.user else r.user.username if r.user else "User",
                    "user_email": r.user.email if r.user else "",
                    "created_date": r.created_date,
                    "sub_replies": sub_replies_data
                })
            
            questions_data.append({
                "id": q.id,
                "title": q.title,
                "question": q.question,
                "user_name": q.user.first_name if q.user else q.user.username if q.user else "User",
                "user_email": q.user.email if q.user else "",
                "created_date": q.created_date,
                "reply_count": q.reply_set.filter(approval_flag=True).count(),
                "replies": replies_data,
                "week": f"Week {section.week_number}" if hasattr(section, 'week_number') else section.name
            })
        
        return JsonResponse({
            "success": True,
            "questions": questions_data,
            "count": len(questions_data)
        })
    
    # Default: return HTML template for non-AJAX requests
    modules = section.module_set.all().order_by('id')
    url_last_parameter = request.path.split('/')[5]
    context = {
        'questions': questions,
        'course': course,
        'sections': sections,
        'enrolled_user': enrolled_user,
        'section': section,
        'modules': modules,
        'title': "{} | {} Discussion Forum".format(course.title, section.name),
        'canonical_url' : request.build_absolute_uri(request.path),
        'url_last_parameter' : url_last_parameter,
    }
    return render(request, 'discussion_forum/weekly_forum.html', context)




# @login_required(login_url='login')
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def individual_question(request, id, course_url, section_url, qid):
    print("Individual__lucky", course_url)

    # Check if this is an AJAX/API request
    is_ajax = request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    now = timezone.now()
    course = get_object_or_404(Course, pk=id, url_link_name=course_url)
    enrolled_user = EnrolledUser.objects.filter(course_id=course.id, user=request.user, enrolled=True, end_at__gt=now).first()
    section = get_object_or_404(Section, course_id=id, url_name=section_url)
    question = get_object_or_404(Question, pk=qid)
    questioned_user = get_object_or_404(Account, pk=question.user_id)
    replies = question.reply_set.all().filter(approval_flag=True).order_by('-id')
    if request.GET.get('filter') == 'byyou':
        replies = replies.filter(user=request.user)

    print("courLucky_:", course)

    # Return JSON for API calls
    if is_ajax:
        replies_data = []
        for r in replies:
            # Get subreplies - show approved subreplies + user's own unapproved subreplies
            sub_replies = r.subreply_set.filter(
                Q(approval_flag=True) | Q(user=request.user)
            )
            sub_replies_data = []
            for sr in sub_replies:
                sub_replies_data.append({
                    "id": sr.id,
                    "sub_reply": sr.sub_reply,
                    "user_name": sr.user.first_name if sr.user else sr.user.username if sr.user else "User",
                    "user_email": sr.user.email if sr.user else "",
                    "created_date": sr.created_date
                })
            replies_data.append({
                "id": r.id,
                "reply": r.reply,
                "user_name": r.user.first_name if r.user else r.user.username if r.user else "User",
                "user_email": r.user.email if r.user else "",
                "created_date": r.created_date,
                "sub_replies": sub_replies_data
            })

        return JsonResponse({
            "success": True,
            "question": {
                "id": question.id,
                "title": question.title,
                "question": question.question,
                "user_name": question.user.first_name if question.user else question.user.username if question.user else "User",
                "user_email": question.user.email if question.user else "",
                "created_date": question.created_date,
                "replies": replies_data
            },
            "course": {
                "id": course.id,
                "title": course.title,
                "slug": course.url_link_name
            },
            "section": {
                "id": section.id,
                "name": section.name,
                "slug": section.url_name
            }
        })

    # For non-AJAX requests, redirect to the frontend discussion forum
    # The template doesn't exist, so redirect to the main forum page
    from django.urls import reverse
    try:
        return redirect(f'/courses/{id}/{course_url}/discussionforum/{section_url}/#question-{qid}')
    except Exception:
        # Fallback: redirect to the main discussion forum
        return redirect(f'/courses/{id}/{course_url}/discussionforum/{section_url}/')



# @login_required(login_url='login')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reply(request, id, course_url, section_url, qid):
    course = get_object_or_404(Course, pk=id, url_link_name=course_url)
    question = get_object_or_404(Question, pk=qid)
    section = get_object_or_404(Section, course_id=id, url_name=section_url)
    teaching_assistants = course.teaching_assistant.all().values_list('email')
    ta_list = [ta[0] for ta in teaching_assistants]
    
    # Check if this is an AJAX/API request - use both request.headers and request.META for compatibility
    accept_header = request.headers.get('Accept', '')
    x_requested_with = request.headers.get('X-Requested-With', '')
    http_accept = request.META.get('HTTP_ACCEPT', '')
    is_ajax = 'application/json' in accept_header or 'XMLHttpRequest' in x_requested_with or 'application/json' in http_accept
    
    # Debug log
    print(f"[create_reply] Accept: {accept_header}, X-Requested-With: {x_requested_with}, is_ajax: {is_ajax}")
    
    if request.method == 'POST':
        reply_text = None
        
        # Get content type from headers
        content_type = request.headers.get('Content-Type', '') or request.META.get('CONTENT_TYPE', '')
        print(f"[create_reply] Content-Type: {content_type}")
        
        # First try JSON body (since frontend sends JSON)
        if 'application/json' in content_type:
            import json
            try:
                body_data = json.loads(request.body.decode('utf-8'))
                reply_text = body_data.get('reply')
                print(f"[create_reply] Parsed JSON body: {reply_text}")
            except Exception as e:
                print(f"Error parsing JSON body: {e}")
        # Then try POST data (form data)
        elif request.POST.get('reply'):
            reply_text = request.POST.get('reply')
        
        if not reply_text:
            print(f"[create_reply] No reply text found, reply_text: {reply_text}")
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Reply content is required'}, status=400)
            return HttpResponseBadRequest('Reply content is required')
        
        reply = Reply(
            reply = reply_text,
            question_id = qid,
            user = request.user
        )
        
        reply.save()
        print(f"[create_reply] Reply saved with ID: {reply.id}")
        
        # Send email notification (skip for specific user)
        if request.user.id != 2: 
            try:
                mail_subject = "A New reply has been submitted by {}".format(request.user.email)
                message = render_to_string('discussion_forum/reply_notification_email.html', {
                    'user_email': request.user.email,
                    'course_title': course.title,
                    'section': section,
                    'question': question
                })
                send_email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER ,to=ta_list)
                send_email.send()
            except Exception as email_error:
                print(f"Failed to send email notification: {email_error}")
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Reply submitted successfully!',
                'reply': {
                    'id': reply.id,
                    'reply': reply.reply,
                    'user_name': reply.user.first_name if reply.user else reply.user.username if reply.user else "User",
                    'user_email': reply.user.email if reply.user else "",
                    'created_date': reply.created_date.isoformat() if reply.created_date else "",
                    'sub_replies': []
                }
            })
        
        messages.success(request, 'Your response has been submitted successfully!')
        return redirect('individual_question', id, course_url, section_url, qid)
    else:
       # if other than POST request is made.
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Only POST method is allowed'}, status=405)
        return HttpResponseBadRequest()


#chnage code 10feb vikas
# @login_required(login_url='login')
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subreply(request, id, course_url, section_url, qid, rid):
    course = get_object_or_404(Course, pk=id, url_link_name=course_url)
    section = get_object_or_404(Section, course_id=id, url_name=section_url)
    reply = get_object_or_404(Reply, pk=rid)
    question = get_object_or_404(Question, pk=qid)
    teaching_assistants = course.teaching_assistant.all().values_list('email')
    ta_list = [ta[0] for ta in teaching_assistants]
    
    # Check if this is an AJAX/API request - use both request.headers and request.META for compatibility
    accept_header = request.headers.get('Accept', '')
    x_requested_with = request.headers.get('X-Requested-With', '')
    http_accept = request.META.get('HTTP_ACCEPT', '')
    is_ajax = 'application/json' in accept_header or 'XMLHttpRequest' in x_requested_with or 'application/json' in http_accept
    
    # Debug log
    print(f"[create_subreply] Accept: {accept_header}, X-Requested-With: {x_requested_with}, is_ajax: {is_ajax}")
    
    if request.method == 'POST':
        sub_reply_text = None
        
        # Get content type from headers
        content_type = request.headers.get('Content-Type', '') or request.META.get('CONTENT_TYPE', '')
        print(f"[create_subreply] Content-Type: {content_type}")
        
        # First try JSON body (since frontend sends JSON)
        if 'application/json' in content_type:
            import json
            try:
                body_data = json.loads(request.body.decode('utf-8'))
                sub_reply_text = body_data.get('sub_reply')
                print(f"[create_subreply] Parsed JSON body: {sub_reply_text}")
            except Exception as e:
                print(f"Error parsing JSON body: {e}")
        # Then try POST data (form data)
        elif request.POST.get('sub_reply'):
            sub_reply_text = request.POST.get('sub_reply')
        
        if not sub_reply_text:
            print(f"[create_subreply] No sub_reply text found, sub_reply_text: {sub_reply_text}")
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Sub-reply content is required'}, status=400)
            return HttpResponseBadRequest('Sub-reply content is required')
        
        sub_reply = SubReply(
            sub_reply = sub_reply_text,
            reply_id = rid,
            user = request.user
        )
        
        sub_reply.save()
        print(f"[create_subreply] SubReply saved with ID: {sub_reply.id}")
        
        # Send email notification (skip for specific user)
        if request.user.id != 2: 
            try:
                mail_subject = "A New sub reply has been submitted by {}".format(request.user.email)
                message = render_to_string('discussion_forum/subreply_notification_email.html', {
                    'user_email': request.user.email,
                    'course_title': course.title,
                    'section': section,
                    'question': question,
                    'reply': reply,
                })
                send_email = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER ,to=ta_list)
                send_email.send()
            except Exception as email_error:
                print(f"Failed to send email notification: {email_error}")
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Sub-reply submitted successfully!',
                'subreply': {
                    'id': sub_reply.id,
                    'sub_reply': sub_reply.sub_reply,
                    'user_name': sub_reply.user.first_name if sub_reply.user else sub_reply.user.username if sub_reply.user else "User",
                    'user_email': sub_reply.user.email if sub_reply.user else "",
                    'created_date': sub_reply.created_date.isoformat() if sub_reply.created_date else ""
                }
            })
        
        messages.success(request, 'Your response has been submitted successfully!')
        return redirect('individual_question', id, course_url, section_url, qid)
    else:
       # if other than POST request is made.
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Only POST method is allowed'}, status=405)
        return HttpResponseBadRequest()

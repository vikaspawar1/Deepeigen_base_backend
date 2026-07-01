from .models import Course, EnrolledUser

def course_list(request):
    courses_list = Course.objects.order_by('id').filter(is_featured=True)
    return dict(courses_list=courses_list)

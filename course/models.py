from django.db import models
from datetime import datetime
from ckeditor.fields import RichTextField
from accounts.models import Account
from django.http import HttpRequest
from django.utils.timezone import now as date_now

# Create your models here.
class Instructor(models.Model):

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    socialaccount_link = models.CharField(max_length=255, blank=True)
    role = models.TextField()
    profile_picture = models.ImageField(upload_to='course/instructors', default='')
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.email

class TeachingAssistant(models.Model):

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    socialaccount_link = models.CharField(max_length=255, blank=True)
    role = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='course/teaching-assistant', default='')
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.email

class Course(models.Model):

    title = models.CharField(max_length=255)
    meta_description = models.TextField(blank=True)
    url_link_name = models.CharField(max_length=255)
    duration = models.IntegerField(default=0, blank=True)
    category = models.CharField(max_length=255, blank=True)
    course_description = models.TextField(blank=True)
    course_image = models.ImageField(upload_to='course/courses', default='')
    indian_fee = models.IntegerField(blank=True)
    foreign_fee = models.IntegerField(blank=True, null=False)
    # # Added - 
    # foreign_fee = models.IntegerField(blank=True, null=False)
    level = models.CharField(max_length=255)
    #in the course detail page
    entire_overview = RichTextField(blank=True)
    access_description = RichTextField(blank=True)
    refund_description = RichTextField(blank=True)
    assignment_description = RichTextField(blank=True)
    brief_overview = RichTextField(blank=True)

    course_type = models.CharField(max_length=255, blank=True)
    teaching_assistant = models.ManyToManyField(TeachingAssistant, blank=True)
    instructor = models.ManyToManyField(Instructor, blank=True)
    first_offered = models.CharField(max_length=255, blank=True)
    current_status = models.CharField(max_length=255, blank=True)
    user_engagement_per_week = models.CharField(max_length=255, blank=True, default='')
    free_videos_link = models.CharField(max_length=255, blank=True)
    optional_assignment_flg = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    enrolled_users = models.IntegerField(blank=True)
    total_videos = models.IntegerField(blank=True, default=0)
    assignments = models.IntegerField(blank=True, default=0)
    discussion_forum_text = models.TextField(blank=True)
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    def professional_tax(self):
        return self.indian_fee * .18

    def total(self):
        return self.indian_fee * .18 + self.indian_fee

    def __str__(self):
        return self.title

class Section(models.Model):
    name = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(max_length=255, blank=True, default='')
    title = models.CharField(max_length=255, blank=True)
    module_overview = RichTextField(blank=True)
    part_number = models.IntegerField(blank=True, default=0)
    welcome_description = RichTextField(blank=True)
    topics_covered = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    total_assignments = models.IntegerField(blank=True, default=0)
    estimated_time = models.TextField(blank=True, default='')
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f'{self.name} -> {self.course}'

class Outline(models.Model):
    title = models.CharField(max_length=355, blank=True)
    sub_topics = RichTextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f'{self.title} -> {self.course}'
    
    class Meta:
        ordering = ['id']

class Module(models.Model):
    name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    def get_main_lectures(self):
        return self.video_set.filter(type="main_lectures").order_by('id')

    def get_ta_lectures(self):
        return self.video_set.filter(type="ta_lectures").order_by('id')
    
    def get_programming_lectures(self):
        return self.video_set.filter(type="programming_lectures").order_by('id')
    
    def mandatory_assignments(self):
        return self.assignment_set.filter(assignment_type="mandatory").order_by('id')
    
    def optional_assignments(self):
        return self.assignment_set.filter(assignment_type="mandatory").order_by('id')

    def __str__(self):
        return f'{self.title} -> {self.section}'

    class Meta:
        ordering = ['id']

class Assignment(models.Model):
    assignment_type = (
        ('mandatory', 'mandatory'),
        ('optional', 'optional'),
    )
    name = models.CharField(max_length=255, blank=True)
    pdf = models.FileField(upload_to='course/assignments')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=2)
    assignment_type = models.CharField(max_length=20, choices=assignment_type, default='mandatory')
    created_date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f'{self.name} -> {self.module}'

class Video(models.Model):
    video_choices = (
        ('main_lectures', 'main_lectures'),
        ('ta_lectures', 'ta_lectures'),
        ('programming_lectures', 'programming_lectures'),
    )
    title = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=255, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    type = models.CharField(choices=video_choices, max_length=255, default='main_lectures')
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    duration = models.CharField(max_length=255, default='')

    def __str__(self):
        return f'{self.module}'

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.FloatField() # this is the total amount paid
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name}->{self.payment_id}"

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded')
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=25)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=50, default='')
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    course_amount = models.FloatField()
    tax = models.FloatField()
    total_amount = models.FloatField()
    no_of_installments = models.IntegerField(default=1)  # Store chosen installment plan (1, 2, or 3)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)  # Razorpay order ID for installments
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=date_now)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return self.address

    def __str__(self):
        return f"{self.first_name}-{self.order_number}"

class EnrolledUser(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=0)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_price = models.FloatField()
    enrolled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=date_now)
    updated_at = models.DateTimeField(auto_now=True)
    end_at    = models.DateTimeField(default=datetime.now, blank=True)
    full_access_flag = models.BooleanField(default=False)
    installment_id_2=models.CharField(blank=True, null=True,max_length=500)
    installment_id_3=models.CharField(blank=True, null=True,max_length=500)
    no_of_installments=models.IntegerField(default=1)
    first_installments=models.BooleanField(default=False)
    second_installments=models.BooleanField(default=False)
    third_installments=models.BooleanField(default=False)
    serial_number = models.CharField(default='',blank=True, max_length=500)
    invoice=models.FileField(upload_to="Enroll_user/Invoice/",default="",blank=True)
    

    def __str__(self):
        return f"{self.user.first_name}->{self.course.title}"

class UserVideoProgress(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name

class OverallProgress(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.DecimalField(max_digits = 5, default=0, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name

class AssignmentEvaluation(models.Model):
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=2)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits = 5, default=0, decimal_places=2)
    submitted_file = models.FileField(upload_to='course/submitted_assignments', default='')
    submit_flag = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'assignment',)

    def __str__(self):
        return self.user.first_name

class PaymentMethod(models.Model):
    razorpay_flag = models.BooleanField(default=False)

    def __str__(self):
        return f'Razorpay Payment -> {self.razorpay_flag}'
    



class Failed_Assignments(models.Model):
    module = models.ForeignKey(Module,on_delete=models.CASCADE,null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=2)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits = 2, default=0, decimal_places=1)
    submitted_file = models.FileField(upload_to='course/submitted_assignments', default='')
    created_at = models.DateTimeField(default=datetime.now)
    submission_count = models.IntegerField(default=0)



    def __str__(self):
        return self.user.first_name


class Invoice_Registrant(models.Model):
    name=models.ForeignKey(EnrolledUser,on_delete=models.CASCADE,null=True,blank=True)
    order=models.ForeignKey(Order,on_delete=models.CASCADE,null=True,blank=True)
    serial_no=models.CharField(max_length=500,blank=True,null=True)
    invoice=models.FileField(upload_to="Invoice_users/",blank=True)
     
    def __str__(self):
        if self.name and self.name.user:
            return self.name.user.first_name
        return f"Invoice Registrant #{self.id}"
    

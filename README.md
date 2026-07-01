# DeepEigen Backend

## Fix: Prevent Duplicate Course Purchases (09 Feb 2025)

### Problem
Users were able to purchase the same course multiple times even after already being enrolled.

### Solution Implemented

1. **New Helper Function: can_user_purchase_course()**
   - File: backend/course/views.py
   - Uses timezone.now() for proper comparison
   - Returns (can_purchase, reason, enrollment) tuple

2. **Enrollment Check in place_order() Endpoint**
   - Added validation before order creation
   - Returns HTTP 400 if already enrolled with expiration date

3. **Enrollment Check in cart_summary() Endpoint**
   - Same validation for PayU payment gateway

4. **Enhanced course_enrollment() Response**
   - Added enrollment_details with end_at, is_expired, can_repurchase

5. **Frontend Error Handling**
   - File: frontend/src/components/userDashboard/UI/Payment.tsx
   - Shows alert with expiration date
   - Redirects to dashboard

### Behavior After Fix
- Active Enrollment: User CANNOT purchase again
- Expired Enrollment: User CAN purchase again
- New User: User CAN purchase normally

## Other Features
- Course management and enrollment
- Payment processing (Razorpay, PayU)
- Installment support (1, 2, 3 payments)
- Assignment submission and auto-evaluation
- Invoice generation
- Student progress tracking






API for Dedicated "Already Enrolled" Page:
When creating a dedicated page later, use:

Endpoint: GET /courses/{id}/{slug}/enroll

Response:


{
  "data": {
    "course": { "id": 6, "title": "...", "slug": "..." },
    "enrolled": true,
    "enrollment_details": {
      "end_at": "2026-08-09",
      "is_expired": false,
      "can_repurchase": false
    }
  }
}
Display:

enrollment_details.end_at → "Access expires on: [DATE]"
enrollment_details.is_expired → Allow repurchase if true
course.title → Course name
Link to course: /courses/{id}/{slug}/overview

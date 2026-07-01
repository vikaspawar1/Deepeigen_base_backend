# Backend API Audit - HTML vs JSON Output

## Overview
This document lists all APIs/endpoints in the Deep Eigen backend, categorizes them by output type (HTML or JSON), and describes their functions.

---

## MAIN APPLICATION ENDPOINTS (deepeigen/urls.py)

### 1. **HOME PAGE** - `(/)`
- **Endpoint**: `/`
- **Function**: `views.home`
- **Output Type**: **HTML** ✓
- **Purpose**: Renders the homepage with SEO metadata

### 2. **FAQS** - `(/faqs/)`
- **Endpoint**: `/faqs/`
- **Function**: `views.faqs`
- **Output Type**: **HTML** ✓
- **Purpose**: Renders FAQ page

### 3. **ROBOTS.TXT** - `(/robots.txt/)`
- **Endpoint**: `/robots.txt/`
- **Function**: `views.robots_seo`
- **Output Type**: **TEXT**
- **Purpose**: SEO robots file for search engines

### 4. **SITEMAP (HTML)** - `(/sitemap/)`
- **Endpoint**: `/sitemap/`
- **Function**: `views.html_sitemap`
- **Output Type**: **HTML** ✓
- **Purpose**: HTML sitemap of all important pages

### 5. **SITEMAP (XML)** - `(/sitemap.xml/)`
- **Endpoint**: `/sitemap.xml/`
- **Function**: `views.xml_sitemap`
- **Output Type**: **XML**
- **Purpose**: XML sitemap for SEO

### 6. **CAREERS** - `(/careers/)`
- **Endpoint**: `/careers/`
- **Function**: `views.careers`
- **Output Type**: **HTML** ✓
- **Purpose**: Renders careers page

### 7. **TERMS OF SERVICE** - `(/terms/)`
- **Endpoint**: `/terms/`
- **Function**: `views.terms`
- **Output Type**: **HTML** ✓
- **Purpose**: Renders terms of service page

### 8. **PRIVACY POLICY** - `(/privacypolicy/)`
- **Endpoint**: `/privacypolicy/`
- **Function**: `views.privacypolicy`
- **Output Type**: **HTML** ✓
- **Purpose**: Renders privacy policy page

### 9. **PRIVACY POLICY GDPR** - `(/privacypolicygdpr/)`
- **Endpoint**: `/privacypolicygdpr/`
- **Function**: `views.privacypolicygdpr`
- **Output Type**: **HTML** ✓
- **Purpose**: Renders GDPR privacy policy page

### 10. **MAINTENANCE PAGE** - `(/maintenance/)`
- **Endpoint**: `/maintenance/`
- **Function**: `views.maintenance`
- **Output Type**: **HTML** ✓
- **Purpose**: Renders maintenance mode page

---

## ACCOUNTS ENDPOINTS (accounts/urls.py)

### 11. **USER REGISTRATION** - `(/accounts/register/)`
- **Endpoint**: `/accounts/register/`
- **Function**: `views.register`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays registration form and handles user registration with email verification

### 12. **USER LOGIN** - `(/accounts/login/)`
- **Endpoint**: `/accounts/login/`
- **Function**: `views.login`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays login form and handles user authentication

### 13. **MANUAL REGISTRATION** - `(/accounts/register_mannual/)`
- **Endpoint**: `/accounts/register_mannual/`
- **Function**: `views.register_mannual`
- **Output Type**: **HTML** ✓
- **Purpose**: Manual user registration without email verification

### 14. **MANUAL LOGIN** - `(/accounts/login_mannual/)`
- **Endpoint**: `/accounts/login_mannual/`
- **Function**: `views.login_mannual`
- **Output Type**: **HTML** ✓
- **Purpose**: Manual login process

### 15. **USER LOGOUT** - `(/accounts/logout/)`
- **Endpoint**: `/accounts/logout/`
- **Function**: `views.logout`
- **Output Type**: **REDIRECT**
- **Purpose**: Logs out user and redirects to home page

### 16. **DASHBOARD** - `(/accounts/dashboard/)` or `(/accounts/)`
- **Endpoint**: `/accounts/dashboard/` or `/accounts/`
- **Function**: `views.dashboard`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays user dashboard (default/home after login)

### 17. **ACCOUNT ACTIVATION** - `(/accounts/activate/<uidb64>/<token>/)`
- **Endpoint**: `/accounts/activate/<uidb64>/<token>/`
- **Function**: `views.activate`
- **Output Type**: **REDIRECT/HTML**
- **Purpose**: Email verification link for account activation

### 18. **FORGOT PASSWORD** - `(/accounts/forgotPassword/)`
- **Endpoint**: `/accounts/forgotPassword/`
- **Function**: `views.forgotPassword`
- **Output Type**: **HTML** ✓
- **Purpose**: Forgot password form and email sending

### 19. **RESET PASSWORD VALIDATION** - `(/accounts/resetpassword_validate/<uidb64>/<token>/)`
- **Endpoint**: `/accounts/resetpassword_validate/<uidb64>/<token>/`
- **Function**: `views.resetpassword_validate`
- **Output Type**: **HTML** ✓
- **Purpose**: Password reset token validation

### 20. **RESET PASSWORD** - `(/accounts/resetPassword/)`
- **Endpoint**: `/accounts/resetPassword/`
- **Function**: `views.resetPassword`
- **Output Type**: **HTML** ✓
- **Purpose**: Password reset form

### 21. **MY COURSES** - `(/accounts/mycourses/)`
- **Endpoint**: `/accounts/mycourses/`
- **Function**: `views.mycourses`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays all enrolled courses for the user

### 22. **EDIT PROFILE** - `(/accounts/edit_profile/)`
- **Endpoint**: `/accounts/edit_profile/`
- **Function**: `views.edit_profile`
- **Output Type**: **HTML** ✓
- **Purpose**: User profile editing form

### 23. **CHANGE PASSWORD** - `(/accounts/change_password/)`
- **Endpoint**: `/accounts/change_password/`
- **Function**: `views.change_password`
- **Output Type**: **HTML** ✓
- **Purpose**: Change password form for logged-in users

### 24. **INVOICE SECTION** - `(/accounts/invoice/)`
- **Endpoint**: `/accounts/invoice/`
- **Function**: `views.Invoice_section`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays user invoices

### 25. **INVOICE DETAILS** - `(/accounts/invoice/<payment_id>/<course_id>/<orderNumber>)`
- **Endpoint**: `/accounts/invoice/<str:payment_id>/<int:course_id>/<str:orderNumber>`
- **Function**: `views.Invoice`
- **Output Type**: **HTML** ✓ (PDF or HTML)
- **Purpose**: Renders individual invoice for enrollment

### 26. **PAYMENT DUE** - `(/accounts/payment_due/)`
- **Endpoint**: `/accounts/payment_due/`
- **Function**: `views.Payment_due`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays pending payments

### 27. **MANUAL INVOICE** - `(/accounts/invoice_manual/<userId>/<payment_id>/<course_id>/<orderNumber>)`
- **Endpoint**: `/accounts/invoice_manual/<str:userId>/<str:payment_id>/<int:course_id>/<str:orderNumber>`
- **Function**: `views.Invoice_manual`
- **Output Type**: **HTML** ✓ (PDF)
- **Purpose**: Renders manually created invoice

---

## CONTACT ENDPOINTS (contact/urls.py)

### 28. **CONTACT PAGE** - `(/contact/)`
- **Endpoint**: `/contact/`
- **Function**: `views.contact`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays contact form page

---

## COURSES ENDPOINTS (course/urls.py)

### 29. **ALL COURSES** - `(/courses/)`
- **Endpoint**: `/courses/`
- **Function**: `views.courses`
- **Output Type**: **HTML** ✓
- **Purpose**: Lists all available courses

### 30. **COURSE DETAIL** - `(/courses/<id>/<course_url>)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>`
- **Function**: `views.course_detail`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays detailed course information

### 31. **COURSE OVERVIEW** - `(/courses/<id>/<course_url>/overview)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/overview`
- **Function**: `views.course_overview`
- **Output Type**: **HTML** ✓
- **Purpose**: Shows course overview and structure

### 32. **COURSE ENROLLMENT** - `(/courses/<id>/<course_url>/enroll)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/enroll`
- **Function**: `views.course_enrollment`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays enrollment page for a course

### 33. **PLACE ORDER** - `(/courses/<id>/<course_url>/place_order)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/place_order`
- **Function**: `views.place_order`
- **Output Type**: **HTML** ✓
- **Purpose**: Creates order and renders payment page

### 34. **CART SUMMARY** - `(/courses/<id>/<course_url>/cart_summary)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/cart_summary`
- **Function**: `views.cart_summary`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays payment options and cart summary

### 35. **PAYMENT DONE** - `(/courses/<id>/<course_url>/payment_done/<order_id>)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/payment_done/<str:order_id>`
- **Function**: `views.payment_done`
- **Output Type**: **HTML** ✓
- **Purpose**: Payment success confirmation page

### 36. **PAYMENT SUCCESS** - `(/courses/<id>/<course_url>/payment_success/<order_id>)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/payment_success/<str:order_id>`
- **Function**: `views.payment_success`
- **Output Type**: **HTML** ✓
- **Purpose**: Final payment success page with enrollment confirmation

### 37. **COURSE PROGRESS** - `(/courses/<id>/<course_url>/<section_url>/<assignment_id>)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/<str:section_url>/<int:assignment_id>`
- **Function**: `views.course_progress`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays assignment and course progress tracking

### 38. **OPTIONAL ASSIGNMENTS** - `(/courses/<id>/<course_url>/optional_assignments)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/optional_assignments`
- **Function**: `views.optional_assignments`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays optional assignments for a course

### 39. **COURSE SECTION** - `(/courses/<id>/<course_url>/<section_url>)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/<str:section_url>`
- **Function**: `views.course_section`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays course section content and assignments

### 40. **PAYMENT FAILED** - `(/courses/payment_failed/<order_id>)`
- **Endpoint**: `/courses/payment_failed/<str:order_id>`
- **Function**: `views.payment_failed`
- **Output Type**: **HTML** ✓
- **Purpose**: Payment failure page

### 41. **MANUAL USER REGISTRATION** - `(/courses/manual_registration)`
- **Endpoint**: `/courses/manual_registration`
- **Function**: `views.manual_user_registration`
- **Output Type**: **HTML** ✓
- **Purpose**: Manual user registration form (alternative flow)

### 42. **PLACE ORDER MANUALLY** - `(/courses/place_order_mannualy)`
- **Endpoint**: `/courses/place_order_mannualy`
- **Function**: `views.place_order_mannualy`
- **Output Type**: **HTML** ✓
- **Purpose**: Manual order placement without normal enrollment flow

### 43. **GET ORDERS** - `(/courses/get_orders)`
- **Endpoint**: `/courses/get_orders`
- **Function**: `views.get_orders`
- **Output Type**: **LIKELY HTML/JSON** (Needs verification)
- **Purpose**: Retrieves user orders (possibly data endpoint)

---

## DISCUSSION FORUM ENDPOINTS (discussion_forum/urls.py)

### 44. **DISCUSSION FORUM** - `(/courses/<id>/<course_url>/discussionforum/)`
- **Endpoint**: `/courses/<int:id>/<str:course_url>/discussionforum/`
- **Function**: `views.discussion_forum`
- **Output Type**: **HTML** ✓
- **Purpose**: Main discussion forum page for a course

### 45. **WEEKLY FORUM** - `(/courses/<id>/<course_url>/discussionforum/<section_url>/)`
- **Endpoint**: `<str:section_url>/`
- **Function**: `views.weekly_forum`
- **Output Type**: **HTML** ✓
- **Purpose**: Weekly forum for specific course section

### 46. **CREATE POST** - `(/courses/<id>/<course_url>/discussionforum/<section_url>/create_post/)`
- **Endpoint**: `<str:section_url>/create_post/`
- **Function**: `views.create_post`
- **Output Type**: **HTML** ✓
- **Purpose**: Create new post in discussion forum

### 47. **QUESTION SEARCH** - `(/courses/<id>/<course_url>/discussionforum/<section_url>/search/)`
- **Endpoint**: `<str:section_url>/search/`
- **Function**: `views.question_search`
- **Output Type**: **HTML** ✓
- **Purpose**: Search forum questions

### 48. **INDIVIDUAL QUESTION** - `(/courses/<id>/<course_url>/discussionforum/<section_url>/<qid>/)`
- **Endpoint**: `<str:section_url>/<int:qid>/`
- **Function**: `views.individual_question`
- **Output Type**: **HTML** ✓
- **Purpose**: Displays individual question with all replies

### 49. **CREATE REPLY** - `(/courses/<id>/<course_url>/discussionforum/<section_url>/<qid>/create_reply/)`
- **Endpoint**: `<str:section_url>/<int:qid>/create_reply/`
- **Function**: `views.create_reply`
- **Output Type**: **HTML** ✓
- **Purpose**: Create reply to a question

### 50. **CREATE SUB-REPLY** - `(/courses/<id>/<course_url>/discussionforum/<section_url>/<qid>/<rid>/create_subreply/)`
- **Endpoint**: `<str:section_url>/<int:qid>/<int:rid>/create_subreply/`
- **Function**: `views.create_subreply`
- **Output Type**: **HTML** ✓
- **Purpose**: Create sub-reply/comment to a reply

---

## DASHBOARD API ENDPOINTS (dashboard/urls.py) - ALL JSON

### 51. **USERS API** - `(/dashboard/users/)`
- **Endpoint**: `/dashboard/users/`
- **Function**: `views.users_api`
- **Output Type**: **JSON** ✓
- **Query Params**: `page`, `limit`, `is_active` (filter)
- **Purpose**: Retrieves paginated list of all users with optional active filter
- **Returns**: User data (id, username, email, date_joined, etc.), total_pages, current_page

### 52. **ENROLLED USERS API** - `(/dashboard/enrolledUsers/)`
- **Endpoint**: `/dashboard/enrolledUsers/`
- **Function**: `views.enrolledUsers_api`
- **Output Type**: **JSON** ✓
- **Query Params**: `page`, `limit`
- **Purpose**: Retrieves paginated list of all enrolled users
- **Returns**: Enrolled user data (user info, course info, payment info, installments, etc.), total_pages, current_page

### 53. **ASSIGNMENT API** - `(/dashboard/assignment_api/)`
- **Endpoint**: `/dashboard/assignment_api/`
- **Function**: `views.assignment_api`
- **Output Type**: **JSON** ✓
- **Query Params**: `page`, `limit`
- **Purpose**: Retrieves paginated list of all assignments
- **Returns**: Assignment data (id, name, type, module, course, created_date, pdf, etc.), total_pages, current_page

### 54. **ASSIGNMENT EVALUATION API** - `(/dashboard/assignmentEvaluation_api/)`
- **Endpoint**: `/dashboard/assignmentEvaluation_api/`
- **Function**: `views.assignmentEvaluation_api`
- **Output Type**: **JSON** ✓
- **Query Params**: `page`, `limit`
- **Purpose**: Retrieves paginated list of assignment evaluations
- **Returns**: Evaluation data

### 55. **INVOICE REGISTRANT API** - `(/dashboard/invoiceRegistrant_api/)`
- **Endpoint**: `/dashboard/invoiceRegistrant_api/`
- **Function**: `views.invoiceRegistrant_api`
- **Output Type**: **JSON** ✓
- **Query Params**: `page`, `limit`
- **Purpose**: Retrieves paginated list of invoice registrants
- **Returns**: Invoice registrant data (user email, order number, serial no, invoice, etc.), total_pages, current_page

### 56. **OVERALL PROGRESS API** - `(/dashboard/overallProgress_api/)`
- **Endpoint**: `/dashboard/overallProgress_api/`
- **Function**: `views.overallProgress_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves overall course progress metrics
- **Returns**: Progress aggregated data

### 57. **QUESTIONS API** - `(/dashboard/questions_api/)`
- **Endpoint**: `/dashboard/questions_api/`
- **Function**: `views.questions_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves all discussion forum questions
- **Returns**: Question data with pagination

### 58. **REPLIES API** - `(/dashboard/replys_api/)`
- **Endpoint**: `/dashboard/replys_api/`
- **Function**: `views.replys_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves all discussion forum replies
- **Returns**: Reply data with pagination

### 59. **SUB-REPLIES API** - `(/dashboard/subReplys_api/)`
- **Endpoint**: `/dashboard/subReplys_api/`
- **Function**: `views.subReplys_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves all discussion forum sub-replies
- **Returns**: Sub-reply data with pagination

---

## GRAPH/ANALYTICS ENDPOINTS (dashboard/views/graphs/) - ALL JSON

### 60. **ENROLLED USERS GRAPH API** - `(/dashboard/graph_enrolledUsers_api/)`
- **Endpoint**: `/dashboard/graph_enrolledUsers_api/`
- **Function**: `views.graph_enrolledUsers_api`
- **Output Type**: **JSON** ✓
- **Query Params**: `start_date`, `end_date` (format: YYYY-MM-DD)
- **Purpose**: Retrieves enrollment data within date range for graph visualization
- **Returns**: List of enrolled users data filtered by date range

### 61. **TOTAL INCOME GRAPH API** - `(/dashboard/graph_total_income_api/)`
- **Endpoint**: `/dashboard/graph_total_income_api/`
- **Function**: `views.graph_total_income_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves total income metrics for graph
- **Returns**: Income data aggregated

### 62. **NEW ORDER GRAPH API** - `(/dashboard/graph_new_order_api/)`
- **Endpoint**: `/dashboard/graph_new_order_api/`
- **Function**: `views.graph_new_order_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves new orders data for graph visualization
- **Returns**: New orders data

### 63. **SALES TODAY GRAPH API** - `(/dashboard/graph_sales_today_api/)`
- **Endpoint**: `/dashboard/graph_sales_today_api/`
- **Function**: `views.graph_sales_today_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves today's sales data
- **Returns**: Sales data for current day

### 64. **PENDING ORDERS GRAPH API** - `(/dashboard/graph_pending_orders_api/)`
- **Endpoint**: `/dashboard/graph_pending_orders_api/`
- **Function**: `views.graph_pending_orders_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves pending orders data for graph
- **Returns**: Pending orders data

### 65. **REGISTERED USERS GRAPH API** - `(/dashboard/graph_registeredUser_api/)`
- **Endpoint**: `/dashboard/graph_registeredUser_api/`
- **Function**: `views.graph_registeredUser_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves registered users analytics data
- **Returns**: Registered users data

### 66. **MOST SELLING COURSES API** - `(/dashboard/most_selling_courses_api/)`
- **Endpoint**: `/dashboard/most_selling_courses_api/`
- **Function**: `views.most_selling_courses_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves most popular/selling courses data
- **Returns**: Course sales rankings

### 67. **FIVE YEAR SALES SUMMARY API** - `(/dashboard/five_year_sales_summary_api/)`
- **Endpoint**: `/dashboard/five_year_sales_summary_api/`
- **Function**: `views.five_year_sales_summary_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves 5-year historical sales summary
- **Returns**: Sales data aggregated by year

### 68. **OVERALL SHELL WORLD WIDE API** - `(/dashboard/overall_shell_world_wide_api/)`
- **Endpoint**: `/dashboard/overall_shell_world_wide_api/`
- **Function**: `views.overall_shell_world_wide_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves worldwide sales/shell data
- **Returns**: Global sales metrics

### 69. **MONTHLY SHELL WORLD WIDE API** - `(/dashboard/monthly_shell_world_wide_api/)`
- **Endpoint**: `/dashboard/monthly_shell_world_wide_api/`
- **Function**: `views.monthly_shell_world_wide_api`
- **Output Type**: **JSON** ✓
- **Purpose**: Retrieves monthly worldwide sales/shell data
- **Returns**: Monthly sales metrics by region/category

---

## SUMMARY STATISTICS

| Category | Count | Details |
|----------|-------|---------|
| **Total Endpoints** | 69 | |
| **HTML Output** | 50 | Traditional page rendering |
| **JSON Output** | 19 | Dashboard and analytics APIs |
| **Other Output** | 2 | TEXT (robots.txt), XML (sitemap.xml) |
| **HTML Pages** | 50 | User-facing pages and forms |
| **API Endpoints** | 19 | Dashboard/analytics endpoints |

---

## ENDPOINTS NEEDING CONVERSION

The following endpoints render HTML but could potentially serve JSON as alternative output:

1. **Course listings** - `/courses/` - Could return JSON with course data
2. **Course detail** - `/courses/<id>/<url>` - Could return JSON with full course details
3. **User dashboard** - `/accounts/dashboard/` - Could return JSON with user data
4. **My courses** - `/accounts/mycourses/` - Could return JSON with enrolled courses
5. **Course progress** - `/courses/<id>/<url>/<section>/<assignment>` - Could return JSON with progress metrics
6. **Invoices** - `/accounts/invoice/` - Could return JSON or PDF programmatically
7. **Discussion forum** - `/courses/.../discussionforum/` - Could return JSON with forum data
8. **Get Orders** - `/courses/get_orders` - Already appears to be a data endpoint

---

## RECOMMENDATION

The dashboard already has good JSON APIs in place. To improve the system:

1. **Migrate HTML-rendered endpoints to support both HTML and JSON** using Django content negotiation
2. **Create dedicated REST API endpoints** for frontend consumption
3. **Separate concerns**: Views for HTML, APIs for JSON
4. **Consider using Django REST Framework (DRF)** for better API structure
5. **Focus on** `/courses/`, `/accounts/mycourses/`, `/accounts/dashboard/` conversions first as these are core user-facing APIs

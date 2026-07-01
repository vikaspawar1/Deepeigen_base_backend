# Remaining Important APIs to Convert - 22 January 2026

## Summary
Total of 10 important course-related APIs remaining to be converted from HTML to JSON output. These are critical for core business functionality.

---

## High Priority APIs (Critical Business Functions)

### 1. **PLACE ORDER** - Lines TBD
**Endpoint:** `/courses/<id>/<course_url>/place_order`  
**Type:** GET/POST  
**Purpose:** Creates order and initiates payment (Razorpay integration)  
**Importance:** ⭐⭐⭐⭐⭐ **CRITICAL**  
**Current Output:** HTML (payment form page)  
**Expected Response Fields:**
- Order data (similar to cart_summary)
- Razorpay order creation response
- Payment initialization data

**Dependencies:** Razorpay API integration  
**Related to:** cart_summary(), payment_done()

---

### 2. **PAYMENT SUCCESS** - Lines TBD
**Endpoint:** `/courses/<id>/<course_url>/payment_success/<order_id>`  
**Type:** GET/POST  
**Purpose:** Final payment success confirmation & enrollment finalization  
**Importance:** ⭐⭐⭐⭐⭐ **CRITICAL**  
**Current Output:** HTML (success page)  
**Expected Response Fields:**
- Payment confirmation data
- Order finalized status
- Enrollment confirmation
- Certificate/invoice data

**Dependencies:** payment_done(), course enrollment system  
**Related to:** payment_done()

---

### 3. **COURSE PROGRESS** - Lines TBD
**Endpoint:** `/courses/<id>/<course_url>/<section_url>/<assignment_id>`  
**Type:** GET/POST  
**Purpose:** Display assignment, handle submission, track progress  
**Importance:** ⭐⭐⭐⭐⭐ **CRITICAL**  
**Current Output:** HTML (assignment page with submission form)  
**Expected Response Fields:**
- Assignment details (name, description, pdf, module)
- Course/section progress tracking
- User submission history
- Assignment feedback/grading

**Business Logic:**
- Section lock checking
- Installment verification
- Progress percentage calculation
- Submission validation

**Models Involved:** Assignment, CourseProgress, UserSubmission (if exists)

---

### 4. **PLACE ORDER MANUALLY** - Lines TBD
**Endpoint:** `/courses/place_order_mannualy`  
**Type:** POST  
**Purpose:** Manual order creation by staff/admin (alternative payment flow)  
**Importance:** ⭐⭐⭐⭐ **HIGH**  
**Current Output:** HTML response  
**Expected Response Fields:**
- Order created confirmation
- Payment method options
- Order details

**Access Control:** Staff/Admin only  
**Special Logic:** Bypass normal payment gateway, direct enrollment option

---

### 5. **GET ORDERS** - Lines TBD
**Endpoint:** `/courses/get_orders`  
**Type:** GET  
**Purpose:** Retrieve list of orders (user's or all orders)  
**Importance:** ⭐⭐⭐⭐ **HIGH**  
**Current Output:** JSON (already partially converted)  
**Status:** Likely already JSON, but verify and validate

**Expected Response Fields:**
- Orders list with pagination
- Order details (all Order model fields)
- User information
- Payment information
- Course details

---

## Medium Priority APIs (Course Management)

### 6. **PAYMENT SUCCESS (PayU)** - Lines TBD
**Endpoint:** `/courses/<id>/<course_url>/payment_success/<order_id>` (PayU variant)  
**Type:** POST  
**Purpose:** PayU payment success callback  
**Importance:** ⭐⭐⭐⭐ **HIGH**  
**Current Output:** HTML render  
**Expected Response Fields:**
- PayU verification response
- Payment success confirmation
- Enrollment data

**Payment Gateway:** PayU (different from Razorpay)  
**Related to:** cart_summary()

---

### 7. **DISCUSSION FORUM** - Lines TBD
**Endpoint:** `/courses/<id>/<course_url>/discussionforum/`  
**Type:** GET  
**Purpose:** Main discussion forum page  
**Importance:** ⭐⭐⭐ **MEDIUM**  
**Current Output:** HTML (forum page)  
**Expected Response Fields:**
- Questions list (id, title, author, replies_count, created_date, is_solved)
- User forum stats
- Pagination for questions

**Models:** DiscussionQuestion, Reply, SubReply (if exists)

---

### 8. **CREATE POST (Forum)** - Lines TBD
**Endpoint:** `/courses/<id>/<course_url>/discussionforum/<section_url>/create_post/`  
**Type:** POST  
**Purpose:** Create new forum post  
**Importance:** ⭐⭐⭐ **MEDIUM**  
**Current Output:** HTML form/redirect  
**Expected Response Fields:**
- Created post data
- Post ID
- Creation timestamp
- Author information

**Validation:** Title, content, section validation

---

### 9. **INDIVIDUAL QUESTION** - Lines TBD
**Endpoint:** `/courses/<id>/<course_url>/discussionforum/<section_url>/<qid>/`  
**Type:** GET  
**Purpose:** Display question with all replies and sub-replies  
**Importance:** ⭐⭐⭐ **MEDIUM**  
**Current Output:** HTML (question detail page)  
**Expected Response Fields:**
- Question details
- Replies array (nested)
- Sub-replies for each reply (nested)
- Author info for each post
- User voting/upvote data (if exists)

**Nested Structure:** Question → Replies[] → SubReplies[]

---

### 10. **CREATE REPLY (Forum)** - Lines TBD
**Endpoint:** `/courses/<id>/<course_url>/discussionforum/<section_url>/<qid>/create_reply/`  
**Type:** POST  
**Purpose:** Create reply to forum question  
**Importance:** ⭐⭐⭐ **MEDIUM**  
**Current Output:** HTML form/redirect  
**Expected Response Fields:**
- Created reply data
- Reply ID
- Creation timestamp
- Author information
- Associated question ID

---

## Low Priority APIs (Information/Static Pages)

### Additional Candidates (Lower Priority)
- **CREATE SUB-REPLY** - Sub-comment reply creation
- **QUESTION SEARCH** - Forum question search
- **WEEKLY FORUM** - Weekly forum for sections
- **PAYMENT DUE** - List pending payments
- **INVOICE SECTION** - List user invoices
- **INVOICE DETAILS** - Individual invoice rendering

---

## Conversion Priority Recommendation

### Phase 1 (Critical - Start Here)
1. `place_order()` - Razorpay payment initiation
2. `payment_success()` - Payment success finalization
3. `course_progress()` - Assignment submission handling
4. `place_order_mannualy()` - Manual enrollment

### Phase 2 (High Priority)
5. `payment_success()` - PayU variant
6. `get_orders()` - Verify if already JSON
7. Individual forum endpoints (create_post, individual_question, create_reply)

### Phase 3 (Medium Priority)
8. Discussion forum list endpoints
9. Remaining forum functionality

---

## Model Fields Likely Needed

### New Models to Serialize:
- **DiscussionQuestion** - id, title, content, author_id, course_id, section_id, created_at, updated_at, is_solved, replies_count
- **Reply** - id, question_id, content, author_id, created_at, updated_at, upvotes
- **SubReply** - id, reply_id, content, author_id, created_at, updated_at
- **CourseProgress/UserSubmission** - submission_date, status, file, feedback, score

---

## Estimated Total Work

- **APIs to Convert:** 10 important ones
- **Estimated Lines of Code:** 500-800 lines
- **Estimated Time:** 2-3 hours for experienced developer
- **Testing Scope:** Payment flows (2), Assignment handling (1), Forum operations (3)

---

## Next Steps

1. Prioritize `place_order()` - Most critical for payment flow
2. Then `payment_success()` - Completes payment lifecycle
3. Then `course_progress()` - Core user interaction
4. Forum endpoints can be done in parallel or after core flow

---

**Date:** 22 January 2026  
**Status:** 10 more critical APIs identified  
**Note:** These are in addition to the 10 already converted (total 20 course-related endpoints)

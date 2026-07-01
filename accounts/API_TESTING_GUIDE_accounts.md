# API Testing Guide - Complete Account APIs

This guide explains how to test all **11 converted account endpoints** using Postman.

---

## ✅ APIs Already Converted to JSON

All 11 account endpoints have been successfully converted from HTML rendering to JSON responses:

### Phase 1: Authentication (7 APIs)
| # | API Name | Method | Route | Status |
|---|----------|--------|-------|--------|
| 1 | **Register** | POST | `/accounts/register/` | ✅ Converted |
| 2 | **Login** | POST | `/accounts/login/` | ✅ Converted |
| 3 | **Logout** | POST | `/accounts/logout/` | ✅ Converted |
| 4 | **Activate** | GET | `/accounts/activate/<uidb64>/<token>/` | ✅ Converted |
| 5 | **Forgot Password** | POST | `/accounts/forgotPassword/` | ✅ Converted |
| 6 | **Validate Reset Password** | GET | `/accounts/resetpassword_validate/<uidb64>/<token>/` | ✅ Converted |
| 7 | **Reset Password** | POST | `/accounts/resetPassword/` | ✅ Converted |

### Phase 2: User Profile (4 APIs)
| # | API Name | Method | Route | Status |
|---|----------|--------|-------|--------|
| 8 | **Dashboard** | GET | `/accounts/dashboard/` | ✅ Converted |
| 9 | **My Courses** | GET | `/accounts/mycourses/` | ✅ Converted |
| 10 | **Edit Profile** | GET/POST | `/accounts/edit_profile/` | ✅ Converted |
| 11 | **Change Password** | POST | `/accounts/change_password/` | ✅ Converted |

**Status:** All 11 APIs are ready for testing with Postman ✓

---

## Table of Contents
1. [APIs Already Converted](#-apis-already-converted-to-json)
2. [Testing Phase 1: Authentication](#phase-1-testing---authentication-7-apis)
3. [Testing Phase 2: User Profile](#phase-2-testing---user-profile-4-apis)
4. [Quick Reference](#quick-reference)

---

# PHASE 1 TESTING - AUTHENTICATION (7 APIs)

---

## Testing Activation

### Overview
- **Endpoint:** `GET /accounts/activate/<uidb64>/<token>/`
- **Purpose:** Verify user email and activate account
- **Status after activation:** `is_active: true`

### Complete Flow

#### **Step 1: Register a New User**

**URL:**
```
POST http://127.0.0.1:8000/accounts/register/
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe123",
  "email": "testuser@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "phone_number": "+91-9876543210",
  "profession": "Software Engineer",
  "country": "India"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Registration successful. Verification email sent to your email address.",
  "status": 201,
  "user": {
    "id": 5,
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe123",
    "email": "testuser@example.com",
    "phone_number": "+91-9876543210",
    "profession": "Software Engineer",
    "country": "India",
    "is_active": false,
    "date_joined": "2026-01-23T10:30:00Z"
  }
}
```

⚠️ **Note:** `is_active: false` - User needs to activate via email link

---

#### **Step 2: Extract Activation Token**

The registration triggers an activation email. You need to extract `uidb64` and `token` from the email link.

##### **Option A: From Django Console (Recommended)**

Open terminal in your project and run:

```bash
python manage.py shell
```

Copy-paste this code:

```python
from accounts.models import Account
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Get the user you just registered
user = Account.objects.get(email='testuser@example.com')

# Generate token
token = default_token_generator.make_token(user)
uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()

print("=" * 60)
print("ACTIVATION TOKEN DETAILS")
print("=" * 60)
print(f"User ID: {user.id}")
print(f"Email: {user.email}")
print(f"uidb64: {uidb64}")
print(f"token: {token}")
print()
print("Full URL for Postman:")
print(f"http://127.0.0.1:8000/accounts/activate/{uidb64}/{token}/")
print("=" * 60)
```

**Example Output:**
```
============================================================
ACTIVATION TOKEN DETAILS
============================================================
User ID: 5
Email: testuser@example.com
uidb64: NQ==
token: c0pxxxxx-xxxxx-xxxxx
Full URL for Postman:
http://127.0.0.1:8000/accounts/activate/NQ==/c0pxxxxx-xxxxx/
============================================================
```

##### **Option B: From Console Email Output**

If using Django's console email backend, check your Django runserver console for email output. Look for the activation link in the email content.

---

#### **Step 3: Test Activation in Postman**

**URL:** (Use the full URL from Step 2)
```
GET http://127.0.0.1:8000/accounts/activate/NQ==/c0pxxxxx-xxxxx/
```

**Method:** GET

**Headers:** (None needed)

**Body:** (Empty)

**Click Send**

---

#### **Step 4: Check Success Response**

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Congratulations! Your account has been activated successfully.",
  "status": 200,
  "user": {
    "id": 5,
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe123",
    "email": "testuser@example.com",
    "phone_number": "+91-9876543210",
    "profession": "Software Engineer",
    "country": "India",
    "is_active": true,
    "date_joined": "2026-01-23T10:30:00Z"
  }
}
```

✅ **Success:** `is_active: true`

---

#### **Step 5: Verify by Login**

Try logging in with the activated account:

**URL:**
```
POST http://127.0.0.1:8000/accounts/login/
```

**Request Body:**
```json
{
  "email": "testuser@example.com",
  "password": "password123"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "status": 200,
  "user": {
    "id": 5,
    "is_active": true,
    ...
  }
}
```

✅ **If login succeeds, activation worked!**

---

### Error Scenarios

#### **Invalid or Expired Token (400)**
```json
{
  "success": false,
  "message": "Invalid or expired activation link",
  "status": 400,
  "error_type": "invalid_token"
}
```

**Causes:**
- Wrong uidb64 or token
- Token expired (if old user)
- User doesn't exist

---

## Testing Reset Password Validation

### Overview
- **Endpoint:** `GET /accounts/resetpassword_validate/<uidb64>/<token>/`
- **Purpose:** Validate password reset link before allowing password change
- **Returns:** User info and validation status

### Complete Flow

#### **Step 1: Request Password Reset Email**

**URL:**
```
POST http://127.0.0.1:8000/accounts/forgotPassword/
```

**Request Body:**
```json
{
  "email": "testuser@example.com"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Password reset email has been sent to your email address. Please check your inbox.",
  "status": 200,
  "email_sent": true,
  "email": "testuser@example.com"
}
```

✅ User receives reset email with token

---

#### **Step 2: Extract Reset Token**

Similar to activation, extract `uidb64` and `token` from the reset email.

##### **Option A: From Django Console (Recommended)**

```bash
python manage.py shell
```

Copy-paste this code:

```python
from accounts.models import Account
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Get the user
user = Account.objects.get(email='testuser@example.com')

# Generate token
token = default_token_generator.make_token(user)
uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()

print("=" * 60)
print("PASSWORD RESET TOKEN DETAILS")
print("=" * 60)
print(f"User ID: {user.id}")
print(f"Email: {user.email}")
print(f"uidb64: {uidb64}")
print(f"token: {token}")
print()
print("Full URL for Postman:")
print(f"http://127.0.0.1:8000/accounts/resetpassword_validate/{uidb64}/{token}/")
print("=" * 60)
```

**Example Output:**
```
============================================================
PASSWORD RESET TOKEN DETAILS
============================================================
User ID: 5
Email: testuser@example.com
uidb64: NQ==
token: c0pxxxxx-xxxxx-xxxxx
Full URL for Postman:
http://127.0.0.1:8000/accounts/resetpassword_validate/NQ==/c0pxxxxx-xxxxx/
============================================================
```

---

#### **Step 3: Test Validate Reset Password in Postman**

**URL:** (Use the full URL from Step 2)
```
GET http://127.0.0.1:8000/accounts/resetpassword_validate/NQ==/c0pxxxxx-xxxxx/
```

**Method:** GET

**Headers:** (None needed)

**Body:** (Empty)

**Click Send**

---

#### **Step 4: Check Success Response**

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Password reset link is valid. You can now reset your password.",
  "status": 200,
  "token_valid": true,
  "uid": "5",
  "user": {
    "id": 5,
    "email": "testuser@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

✅ **Link is valid and user can reset password**

---

#### **Step 5: Reset Password**

Now that we've validated the token, reset the password.

**URL:**
```
POST http://127.0.0.1:8000/accounts/resetPassword/
```

**Request Body:**
```json
{
  "password": "newpassword123",
  "confirm_password": "newpassword123",
  "uid": "5"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Password has been reset successfully. You can now login with your new password.",
  "status": 200,
  "user": {
    "id": 5,
    "email": "testuser@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

✅ **Password changed successfully**

---

#### **Step 6: Verify by Login with New Password**

Try logging in with the new password:

**URL:**
```
POST http://127.0.0.1:8000/accounts/login/
```

**Request Body:**
```json
{
  "email": "testuser@example.com",
  "password": "newpassword123"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "status": 200,
  "user": {
    "id": 5,
    ...
  }
}
```

✅ **If login succeeds with new password, password reset worked!**

---

### Error Scenarios

#### **Invalid or Expired Token (401)**
```json
{
  "success": false,
  "message": "This password reset link has expired or is invalid. Please request a new one.",
  "status": 401,
  "error_type": "expired_token"
}
```

**Causes:**
- Wrong uidb64 or token
- Token expired (regenerate new one)
- User doesn't exist

#### **Invalid Link Format (400)**
```json
{
  "success": false,
  "message": "Invalid or expired password reset link",
  "status": 400,
  "error_type": "invalid_link"
}
```

---

## Quick Reference

### Activation Endpoint
| Item | Value |
|------|-------|
| **Method** | GET |
| **URL** | `/accounts/activate/<uidb64>/<token>/` |
| **Token Source** | Activation email or Django shell |
| **Success Status** | 200 |
| **Returns** | User object with `is_active: true` |

### Reset Password Validation Endpoint
| Item | Value |
|------|-------|
| **Method** | GET |
| **URL** | `/accounts/resetpassword_validate/<uidb64>/<token>/` |
| **Token Source** | Reset email or Django shell |
| **Success Status** | 200 |
| **Next Step** | POST to `/accounts/resetPassword/` |

---

## Common Issues & Solutions

### Issue: "Invalid or expired activation link"
**Solution:** 
- Regenerate token from Django shell
- Make sure you're using correct uidb64 and token
- Token is case-sensitive

### Issue: "User not found"
**Solution:**
- Make sure user exists in database
- Check email spelling

### Issue: "Method not allowed"
**Solution:**
- Activation uses GET method
- Reset validation uses GET method
- Reset password uses POST method

---

## Environment Setup

Make sure Django server is running:

```bash
---

# PHASE 2 TESTING - USER PROFILE (4 APIs)

## Prerequisites for Phase 2
1. ✅ User must be registered and activated (from Phase 1)
2. ✅ User must be logged in (have valid session)
3. ✅ All requests require authentication (session cookie)

---

## Step 0: LOGIN (Before Testing Phase 2)

All Phase 2 APIs require an authenticated session. Login first:

```
POST http://127.0.0.1:8000/accounts/login/
```

**Request Body:**
```json
{
  "email": "testuser@example.com",
  "password": "password123"
}
```

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "status": 200,
  "user": {
    "id": 5,
    "email": "testuser@example.com",
    "is_active": true
  }
}
```

✅ Postman automatically stores session cookie. You're now ready for Phase 2 tests.

---

## Test 1: DASHBOARD

### Overview
- **Endpoint:** `GET /accounts/dashboard/`
- **Purpose:** Get user profile + courses summary
- **Returns:** User data, profile data, courses list, pending payments

### Testing

**URL:**
```
GET http://127.0.0.1:8000/accounts/dashboard/
```

**Method:** GET

**Headers:** (None needed - Postman handles session)

**Body:** Empty

**Click Send**

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Dashboard data retrieved successfully",
  "status": 200,
  "user": {
    "id": 5,
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "email": "testuser@example.com",
    "phone_number": "+91-9876543210",
    "profession": "Software Engineer",
    "country": "India",
    "is_active": true,
    "is_staff": false,
    "is_superadmin": false,
    "user_type": "user",
    "profile": {
      "address_line_1": "123 Main St",
      "address_line_2": "Apt 4B",
      "city": "Bhopal",
      "state": "Madhya Pradesh",
      "country": "India",
      "profile_picture": "/media/userprofile/pic.jpg"
    }
  },
  "courses": {
    "total_count": 3,
    "courses_list": [
      {
        "id": 1,
        "title": "Python Basics",
        "category": "Programming",
        "url_link_name": "python-basics",
        "description": "Learn Python..."
      }
    ]
  },
  "pending_payments": [
    {
      "course_name": "Python Basics",
      "course_price": 5000,
      "installment": "Second Installment"
    }
  ],
  "timestamp": "2026-01-23T10:35:00Z"
}
```

### Verification Checklist ✅
- [ ] `success: true`
- [ ] User data populated
- [ ] Profile data with picture URL
- [ ] Courses list returned
- [ ] Course count matches
- [ ] Pending payments shown (if any)

---

## Test 2: MY COURSES

### Overview
- **Endpoint:** `GET /accounts/mycourses/`
- **Purpose:** List all enrolled courses
- **Returns:** Complete course list with details

### Testing

**URL:**
```
GET http://127.0.0.1:8000/accounts/mycourses/
```

**Method:** GET

**Headers:** (None needed)

**Body:** Empty

**Click Send**

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Courses retrieved successfully",
  "status": 200,
  "user_type": "user",
  "courses": {
    "total_count": 3,
    "courses_list": [
      {
        "id": 1,
        "title": "Python Basics",
        "category": "Programming",
        "url_link_name": "python-basics",
        "description": "Learn Python fundamentals...",
        "price": 5000,
        "duration": "8 weeks",
        "instructor": "John Smith",
        "created_at": "2026-01-01T10:00:00Z",
        "updated_at": "2026-01-20T15:30:00Z",
        "is_active": true,
        "thumbnail": "/media/courses/python.jpg"
      },
      {
        "id": 2,
        "title": "Web Development",
        "category": "Web",
        "url_link_name": "web-dev",
        "description": "Master web development...",
        "price": 7000,
        "is_active": true
      },
      {
        "id": 3,
        "title": "Data Science",
        "category": "Data",
        "url_link_name": "data-science",
        "price": 8000,
        "is_active": true
      }
    ]
  },
  "timestamp": "2026-01-23T10:35:00Z"
}
```

### Verification Checklist ✅
- [ ] `success: true`
- [ ] Course count correct (3 courses)
- [ ] Course titles populated
- [ ] Course prices populated
- [ ] Thumbnail URLs present
- [ ] `user_type` shown ("user", "staff", or "superadmin")

---

## Test 3: EDIT PROFILE - GET (Retrieve Current)

### Overview
- **Endpoint:** `GET /accounts/edit_profile/`
- **Purpose:** Retrieve current profile data
- **Returns:** Account + UserProfile fields

### Testing

**URL:**
```
GET http://127.0.0.1:8000/accounts/edit_profile/
```

**Method:** GET

**Headers:** (None needed)

**Body:** Empty

**Click Send**

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Profile data retrieved successfully",
  "status": 200,
  "data": {
    "user": {
      "id": 5,
      "first_name": "John",
      "last_name": "Doe",
      "username": "johndoe",
      "email": "testuser@example.com",
      "phone_number": "+91-9876543210",
      "profession": "Software Engineer",
      "country": "India"
    },
    "profile": {
      "address_line_1": "123 Main Street",
      "address_line_2": "Apt 4B",
      "city": "Bhopal",
      "state": "Madhya Pradesh",
      "country": "India",
      "profile_picture": "/media/userprofile/pic.jpg"
    }
  }
}
```

### Verification Checklist ✅
- [ ] `success: true`
- [ ] User data populated
- [ ] Profile data populated
- [ ] Phone number format correct
- [ ] Profile picture URL present

---

## Test 4: EDIT PROFILE - POST (Update Profile)

### Overview
- **Endpoint:** `POST /accounts/edit_profile/`
- **Purpose:** Update user profile
- **Returns:** Updated profile data

### Testing - JSON Update

**URL:**
```
POST http://127.0.0.1:8000/accounts/edit_profile/
```

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+91-9999999999",
  "profession": "Senior Software Engineer",
  "country": "India",
  "address_line_1": "456 New Avenue",
  "address_line_2": "Suite 200",
  "city": "Pune",
  "state": "Maharashtra"
}
```

**Click Send**

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "status": 200,
  "data": {
    "user": {
      "id": 5,
      "first_name": "John",
      "last_name": "Smith",
      "username": "johndoe",
      "email": "testuser@example.com",
      "phone_number": "+91-9999999999",
      "profession": "Senior Software Engineer",
      "country": "India"
    },
    "profile": {
      "address_line_1": "456 New Avenue",
      "address_line_2": "Suite 200",
      "city": "Pune",
      "state": "Maharashtra",
      "country": "India",
      "profile_picture": "/media/userprofile/pic.jpg"
    }
  }
}
```

### Verification Checklist ✅
- [ ] `success: true`
- [ ] Last name changed to "Smith"
- [ ] Phone number updated to "+91-9999999999"
- [ ] Profession changed to "Senior..."
- [ ] City changed to "Pune"
- [ ] State changed to "Maharashtra"

### Verify Update with GET

Call Test 3 (GET edit_profile) again - you should see updated data:

```
GET http://127.0.0.1:8000/accounts/edit_profile/
```

✅ New data should be reflected

### Testing - File Upload (Profile Picture)

**URL:**
```
POST http://127.0.0.1:8000/accounts/edit_profile/
```

**Method:** POST

**Headers:**
```
Content-Type: multipart/form-data
```

**Body (Form-Data):**
- `first_name`: John
- `last_name`: Smith
- `profile_picture`: [Select your image file]
- `city`: Pune

**Click Send**

**Expected Response (200):** Same as JSON update, with new profile_picture URL

---

## Test 5: CHANGE PASSWORD

### Overview
- **Endpoint:** `POST /accounts/change_password/`
- **Purpose:** Change user password (logged in users)
- **Returns:** Confirmation with `action: "login_required"`

### Testing

**URL:**
```
POST http://127.0.0.1:8000/accounts/change_password/
```

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "current_password": "password123",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}
```

**Click Send**

**Expected Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully. Please login again with your new password.",
  "status": 200,
  "user": {
    "id": 5,
    "email": "testuser@example.com",
    "username": "johndoe",
    "password_changed_at": "2026-01-23T10:40:00Z"
  },
  "action": "login_required"
}
```

### Verification Checklist ✅
- [ ] `success: true`
- [ ] `action: "login_required"` (frontend should redirect to login)
- [ ] Message indicates password changed

### Verify with New Password

Try logging in with new password:

```
POST http://127.0.0.1:8000/accounts/login/
```

**Request Body:**
```json
{
  "email": "testuser@example.com",
  "password": "newpassword456"
}
```

**Expected Response (200):** Login success ✅

---

## Error Test Cases for Phase 2

### Test: Dashboard without Login
```
GET http://127.0.0.1:8000/accounts/dashboard/
```
**Expected (403):** Forbidden - "Not authenticated"

---

### Test: Change Password - Wrong Current Password
```
POST http://127.0.0.1:8000/accounts/change_password/

{
  "current_password": "wrongpassword",
  "new_password": "newpass123",
  "confirm_password": "newpass123"
}
```
**Expected (401):**
```json
{
  "success": false,
  "message": "Current password is incorrect",
  "status": 401
}
```

---

### Test: Change Password - Passwords Don't Match
```
POST http://127.0.0.1:8000/accounts/change_password/

{
  "current_password": "password123",
  "new_password": "newpass123",
  "confirm_password": "different456"
}
```
**Expected (400):**
```json
{
  "success": false,
  "message": "New password and confirm password do not match",
  "status": 400
}
```

---

### Test: Change Password - Same as Current
```
POST http://127.0.0.1:8000/accounts/change_password/

{
  "current_password": "password123",
  "new_password": "password123",
  "confirm_password": "password123"
}
```
**Expected (400):**
```json
{
  "success": false,
  "message": "New password cannot be the same as current password",
  "status": 400
}
```

---

### Test: Change Password - Too Short
```
POST http://127.0.0.1:8000/accounts/change_password/

{
  "current_password": "password123",
  "new_password": "pass",
  "confirm_password": "pass"
}
```
**Expected (400):**
```json
{
  "success": false,
  "message": "New password must be at least 6 characters long",
  "status": 400
}
```

---

## Complete Testing Checklist

### Phase 1: Authentication ✅ (Already tested)
- [x] Register
- [x] Login
- [x] Logout
- [x] Activate
- [x] Forgot Password
- [x] Reset Password Validate
- [x] Reset Password

### Phase 2: User Profile (Test Now)
- [ ] Dashboard - GET
- [ ] My Courses - GET
- [ ] Edit Profile - GET (retrieve)
- [ ] Edit Profile - POST (update JSON)
- [ ] Edit Profile - POST (file upload)
- [ ] Change Password - POST
- [ ] Change Password - Error cases

---

## Postman Collection Tips

1. **Save Environment Variables:**
   ```
   base_url: http://127.0.0.1:8000
   email: testuser@example.com
   old_password: password123
   new_password: newpassword456
   ```

2. **Use in Requests:**
   ```
   GET {{base_url}}/accounts/dashboard/
   GET {{base_url}}/accounts/mycourses/
   POST {{base_url}}/accounts/edit_profile/
   POST {{base_url}}/accounts/change_password/
   ```

3. **Save Responses:** Right-click → Save as example

4. **Organize Requests:**
   - Create folder "Phase 1 - Auth"
   - Create folder "Phase 2 - Profile"

---

## Terminal 1: Activate environment
source env/bin/activate

# Terminal 2: Run server
python manage.py runserver

# Terminal 3: Django shell (for getting tokens)
python manage.py shell
```

---

## Postman Collection Tips

1. **Save Environment Variables:**
   - `base_url`: `http://127.0.0.1:8000`
   - `email`: `testuser@example.com`
   - `password`: `password123`

2. **Use in Requests:**
   ```
   {{base_url}}/accounts/activate/{{uidb64}}/{{token}}/
   ```

3. **Save Responses:** Right-click → Save as example

---

## Need Help?

If endpoints are not working:

1. Check Django console for errors
2. Verify user exists: `Account.objects.all()`
3. Verify token format: Run Django shell code
4. Check CSRF token (usually auto-handled by Postman)

---

**Happy Testing! ✅**

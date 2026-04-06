# Python Nigeria Backend — API Reference

**Base URL:** `/api/v1/`
**Authentication:** JWT Bearer Token (except where marked Public)
**Default throttle:** 15 req/min (unauthenticated), 30 req/min (authenticated)

---

## Auth Endpoints

### POST /api/v1/authentication/register/
Register a new user account.

**Auth:** Public

**Request Body:**
| Field | Type | Required |
|---|---|---|
| email | string (email) | Yes |
| password | string (min 8 chars) | Yes |

**Success Response (201):**
```json
{
    "data": {
        "id": "string",
        "email": "user@example.com",
        "is_email_verified": false,
        "is_2fa_enabled": false,
        "auth_provider": "password",
        "created": "2026-04-05T12:00:00Z",
        "message": "Account created. Check your email to verify your account."
    }
}
```

**Error Response (400):**
```json
{
    "error": "An account with this email already exists."
}
```

---

### POST /api/v1/authentication/verify-email/begin/
Request or resend an email verification code/link.

**Auth:** Public

**Request Body:**
| Field | Type | Required |
|---|---|---|
| email | string (email) | Yes |

**Success Response (200):**
```json
{
    "data": {
        "message": "Check your email for a verification code/link."
    }
}
```

**Error Response (400):**
```json
{
    "error": "A verification link/code was already sent. Check your email."
}
```

---

### POST /api/v1/authentication/verify-email/complete/
Complete email verification using a token (query param) or OTP code.

**Auth:** Public

**Query Parameters:**
| Param | Type | Required |
|---|---|---|
| token | string | No (if using OTP) |

**Request Body:**
| Field | Type | Required |
|---|---|---|
| email | string (email) | No (required if using OTP) |
| otp_code | string | No (required if not using token) |

**Success Response (200):**
```json
{
    "data": {
        "id": "string",
        "email": "user@example.com",
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token",
        "message": "Email verified successfully. You are now logged in."
    }
}
```

**Error Response (400):**
```json
{
    "error": "Invalid OTP. Please try again."
}
```

---

### POST /api/v1/authentication/login/
Login with email and password. Sends an OTP to the user's email.

**Auth:** Public

**Request Body:**
| Field | Type | Required |
|---|---|---|
| email | string (email) | Yes |
| password | string | Yes |

**Success Response (200):**
```json
{
    "data": {
        "requires_email_otp": true,
        "requires_2fa": false,
        "email": "user@example.com",
        "message": "OTP sent to your email. Please verify to continue."
    }
}
```

**Error Response (400):**
```json
{
    "error": "Incorrect email or password."
}
```

**Error Response (401):**
```json
{
    "error": "Email is not verified."
}
```

---

### GET /api/v1/authentication/csrfToken/
Get a CSRF token for session-based requests.

**Auth:** Public

**Success Response (200):**
```json
{
    "csrfToken": "string"
}
```

---

### GET /api/v1/authentication/social/begin/google-oauth2/
Initiate Google OAuth2 login. Redirects the client to Google's consent screen.

**Auth:** Public

**Success Response:** HTTP 302 redirect to Google OAuth

---

### GET /api/v1/authentication/social/complete/google-oauth2/
OAuth2 callback. Completes social login and returns JWT tokens.

**Auth:** Public

**Query Parameters (set by OAuth provider):**
| Param | Type | Required |
|---|---|---|
| code | string | Yes |
| state | string | Yes |

**Success Response (200):**
```json
{
    "data": {
        "id": "string",
        "email": "user@example.com",
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token"
    }
}
```

---

### POST /api/v1/authentication/totp-device/create/
Create a TOTP device to begin 2FA setup. The device is unconfirmed until verified.

**Auth:** Bearer Token (IsAuthenticated)

**Request Body:** None

**Success Response (201):**
```json
{
    "data": {
        "user": "user_id",
        "name": "user@example.com",
        "confirmed": false
    }
}
```

**Error Response (400):**
```json
{
    "error": "A 2FA device is already active on this account."
}
```

---

### POST /api/v1/authentication/totp-device/qrcode/
Get a QR code image for scanning with an authenticator app.

**Auth:** Bearer Token (IsAuthenticated)

**Request Body:** None

**Success Response (200):**
- Content-Type: `image/png`
- Body: raw PNG binary

**Error Response (400):**
```json
{
    "error": "No pending 2FA setup found. Please start 2FA setup first."
}
```

---

### POST /api/v1/authentication/totp-device/verify/
Confirm a TOTP device by submitting a code from the authenticator app. Enables 2FA.

**Auth:** Bearer Token (IsAuthenticated)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| otp_token | string (6 digits) | Yes |

**Success Response (200):**
```json
{
    "data": {
        "user": "user_id",
        "name": "user@example.com",
        "confirmed": true,
        "message": "2FA enabled successfully."
    }
}
```

**Error Response (400):**
```json
{
    "error": "Invalid TOTP code. Try again."
}
```

---

## User / Profile Endpoints

> **Note:** The users app URLs are defined but not yet registered in the root URL config. These endpoints are not currently accessible.

### GET /api/v1/users/
List all user profiles. Supports filtering.

**Auth:** Bearer Token (IsAuthenticated)

**Query Parameters:**
| Param | Type | Required |
|---|---|---|
| skills | string | No |
| location | string | No |
| experience_level | string | No |

**Success Response (200):**
```json
[
    {
        "id": 1,
        "user": "username",
        "bio": "Developer bio...",
        "skills": "python,django,react",
        "github": "https://github.com/username",
        "portfolio": "https://portfolio.com",
        "location": "Lagos, Nigeria",
        "experience_level": "Senior",
        "avatar": "http://example.com/avatars/photo.jpg",
        "whatsapp_username": "username",
        "created_at": "2026-04-05T12:00:00Z"
    }
]
```

---

### GET /api/v1/users/\<int:pk\>/
Retrieve a single user profile by ID.

**Auth:** Bearer Token (IsAuthenticated)

**Success Response (200):**
```json
{
    "id": 1,
    "user": "username",
    "bio": "Developer bio...",
    "skills": "python,django,react",
    "github": "https://github.com/username",
    "portfolio": "https://portfolio.com",
    "location": "Lagos, Nigeria",
    "experience_level": "Senior",
    "avatar": "http://example.com/avatars/photo.jpg",
    "whatsapp_username": "username",
    "created_at": "2026-04-05T12:00:00Z"
}
```

**Error Response (404):**
```json
{
    "detail": "Not found."
}
```

---

### PUT /api/v1/users/update_profile/
### PATCH /api/v1/users/update_profile/
Update the authenticated user's own profile. Use `PATCH` for partial updates.

**Auth:** Bearer Token (IsAuthenticated, owner only)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| bio | string | No |
| skills | string | No |
| github | string (URL) | No |
| portfolio | string (URL) | No |
| location | string | No |
| experience_level | string | No |
| whatsapp_username | string | No |

**Success Response (200):**
```json
{
    "id": 1,
    "user": "username",
    "bio": "Updated bio...",
    "skills": "python,django",
    "github": "https://github.com/username",
    "portfolio": "https://portfolio.com",
    "location": "Abuja, Nigeria",
    "experience_level": "Mid-level",
    "whatsapp_username": "username",
    "created_at": "2026-04-05T12:00:00Z"
}
```

---

### PUT /api/v1/users/avatar/
### PATCH /api/v1/users/avatar/
Upload or update the authenticated user's profile avatar.

**Auth:** Bearer Token (IsAuthenticated, owner only)

**Request Body (multipart/form-data):**
| Field | Type | Required |
|---|---|---|
| avatar | image file | Yes |

**Success Response (200):**
```json
{
    "avatar": "http://example.com/avatars/photo.jpg"
}
```

---

## Jobs & Applications Endpoints

### POST /api/v1/job/
Create a new job posting.

**Auth:** Bearer Token (IsJobPoster)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| job_title | string | Yes |
| job_description | string | Yes |
| job_skills | array of objects | Yes |
| job_skills[].skill.name | string | Yes |
| job_skills[].skill_level | string ("Beginner", "Intermidiate", "Advanced") | Yes |
| employment_type | string ("Full Time", "Part Time", "Contract", "Internship", "Voluntary") | Yes |
| company | integer (company ID) | No |
| company_name | string | No |
| salary | decimal | No |
| application_deadline | datetime (ISO 8601, must be future) | No |
| published_at | datetime (ISO 8601, must be future) | No |
| status | string ("Draft", "Published", "Archived", "Expired") | No (default: "Draft") |
| visibility | string ("Private", "Internal", "Public", "Featured") | No (default: "Private") |

**Success Response (201):**
```json
{
    "job": "http://example.com/api/v1/job/550e8400-e29b-41d4-a716-446655440000/",
    "job_title": "backend developer",
    "job_description": "we are looking for...",
    "job_skills": [
        {
            "skill": { "name": "Python" },
            "skill_level": "Advanced"
        }
    ],
    "employment_type": "Full Time",
    "salary": "50000.00",
    "posted_by": {},
    "created_at": "2026-04-05T12:00:00Z",
    "views_count": 0,
    "applications_count": 0,
    "tags": ["python"],
    "is_approved": false,
    "version": 1
}
```

**Error Response (400):**
```json
{
    "error": "...",
    "errors": {}
}
```

---

### GET /api/v1/job/job-list/
List all published/approved jobs. Supports search, filtering, and ordering.

**Auth:** Bearer Token (IsAuthenticated)

**Query Parameters:**
| Param | Type | Required |
|---|---|---|
| search | string (comma-separated terms) | No |
| ordering | string ("job_title", "employment_type", "salary") | No |
| page | integer | No |

**Success Response (200):**
```json
{
    "count": 10,
    "next": "http://example.com/api/v1/job/job-list/?page=2",
    "previous": null,
    "results": [...]
}
```

---

### GET /api/v1/job/\<slug:slug\>/
Retrieve a single job by its UUID slug.

**Auth:** Bearer Token (IsAuthenticated)

**Success Response (200):**
```json
{
    "job": "http://example.com/api/v1/job/550e8400-e29b-41d4-a716-446655440000/",
    "job_title": "backend developer",
    "job_description": "we are looking for...",
    "job_skills": [...],
    "employment_type": "Full Time",
    "salary": "50000.00",
    "posted_by": {},
    "created_at": "2026-04-05T12:00:00Z",
    "views_count": 15,
    "applications_count": 3,
    "tags": ["python"],
    "is_approved": true,
    "version": 1
}
```

**Error Response (404):**
```json
{
    "detail": "Not found."
}
```

---

### PUT /api/v1/job/\<slug:slug\>/
### PATCH /api/v1/job/\<slug:slug\>/
Update a job posting. Creates a new version; the original is preserved.

**Auth:** Bearer Token (job poster or admin)

**Request Body:** Same fields as POST (all optional for PATCH)

**Success Response (200):**
```json
{
    "job": "http://example.com/api/v1/job/<new-slug>/",
    "version": 2,
    "original_job": "http://example.com/api/v1/job/<original-slug>/",
    "job_title": "backend developer",
    ...
}
```

---

### DELETE /api/v1/job/\<slug:slug\>/
Delete a job posting.

**Auth:** Bearer Token (job poster or admin)

**Success Response (204):** No content

---

### POST /api/v1/job/approve/\<slug:slug\>/
Approve or reject a job posting.

**Auth:** Bearer Token (IsAdminUser)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| is_approved | boolean | Yes |
| message | string | No (use for rejection reason) |

**Success Response (200):**
```json
{
    "status": "Approved",
    "message": null,
    "is_approved": true
}
```

**Error Response (403):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

### POST /api/v1/bookmark-folders/
Create a bookmark folder.

**Auth:** Bearer Token (IsAuthenticated)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| folder_name | string | Yes |
| folder_description | string | No |

**Success Response (201):**
```json
{
    "folder_instance": "http://example.com/api/v1/bookmark-folders/1/",
    "folder_name": "my python jobs",
    "folder_description": "interesting python roles",
    "user": {}
}
```

---

### GET /api/v1/bookmark-folders/
List the authenticated user's bookmark folders.

**Auth:** Bearer Token (IsAuthenticated)

**Success Response (200):**
```json
[
    {
        "folder_instance": "http://example.com/api/v1/bookmark-folders/1/",
        "folder_name": "my python jobs",
        "folder_description": "interesting python roles",
        "user": {}
    }
]
```

---

### GET /api/v1/bookmark-folders/\<int:pk\>/
Retrieve a single bookmark folder.

**Auth:** Bearer Token (owner or admin)

**Success Response (200):** Single folder object (same shape as Create)

---

### PUT /api/v1/bookmark-folders/\<int:pk\>/
### PATCH /api/v1/bookmark-folders/\<int:pk\>/
Update a bookmark folder.

**Auth:** Bearer Token (owner or admin)

**Request Body:** Same as POST (all optional for PATCH)

**Success Response (200):** Updated folder object

---

### DELETE /api/v1/bookmark-folders/\<int:pk\>/
Delete a bookmark folder.

**Auth:** Bearer Token (owner or admin)

**Success Response (204):** No content

---

### POST /api/v1/bookmark/
Bookmark a job.

**Auth:** Bearer Token (IsAuthenticated)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| job | string (job UUID slug) | Yes |
| folder | integer (folder ID) | No |
| status | string ("Saved", "Applied", "Interviewing", "Rejected", "Offered", "Archived") | No (default: "Saved") |
| notes | string | No |

**Success Response (201):**
```json
{
    "bookmark": "http://example.com/api/v1/bookmark/1/",
    "job_instance": "http://example.com/api/v1/job/550e8400-e29b-41d4-a716-446655440000/",
    "folder_instance": "http://example.com/api/v1/bookmark-folders/1/",
    "status": "Saved",
    "notes": "follow up on Monday",
    "user": {},
    "created_at": "2026-04-05T12:00:00Z",
    "updated_at": "2026-04-05T12:00:00Z"
}
```

**Error Response (400):**
```json
{
    "error": "You have already bookmarked this job."
}
```

---

### GET /api/v1/bookmark/
List the authenticated user's bookmarks.

**Auth:** Bearer Token (IsAuthenticated)

**Success Response (200):** Array of bookmark objects (same shape as Create)

---

### GET /api/v1/bookmark/\<int:pk\>/
Retrieve a single bookmark.

**Auth:** Bearer Token (owner or admin)

**Success Response (200):** Single bookmark object

---

### PUT /api/v1/bookmark/\<int:pk\>/
### PATCH /api/v1/bookmark/\<int:pk\>/
Update a bookmark (e.g. change status or notes).

**Auth:** Bearer Token (owner or admin)

**Request Body:** Same as POST (all optional for PATCH)

**Success Response (200):** Updated bookmark object

---

### DELETE /api/v1/bookmark/\<int:pk\>/
Remove a bookmark.

**Auth:** Bearer Token (owner or admin)

**Success Response (204):** No content

---

## Posts & Comments Endpoints

### GET /api/v1/posts/
List all community posts.

**Auth:** Public (read) / Bearer Token (write)

**Success Response (200):**
```json
[
    {
        "id": 1,
        "author": "user_id",
        "author_email": "user@example.com",
        "title": "My First Post",
        "content": "Post content here...",
        "tags": "python,events",
        "likes_count": 5,
        "is_liked": false,
        "comments": [...],
        "created_at": "2026-04-05T12:00:00Z",
        "updated_at": "2026-04-05T12:00:00Z"
    }
]
```

---

### POST /api/v1/posts/
Create a new community post.

**Auth:** Bearer Token (IsAuthenticated)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| title | string | Yes |
| content | string | Yes |
| tags | string (comma-separated) | No |

**Success Response (201):**
```json
{
    "id": 1,
    "title": "My First Post",
    "content": "Post content here...",
    "tags": "python,events",
    "created_at": "2026-04-05T12:00:00Z",
    "updated_at": "2026-04-05T12:00:00Z"
}
```

---

### GET /api/v1/posts/\<int:pk\>/
Retrieve a single post with its comments.

**Auth:** Public (read)

**Success Response (200):**
```json
{
    "id": 1,
    "author": "user_id",
    "author_email": "user@example.com",
    "title": "My First Post",
    "content": "Post content here...",
    "tags": "python,events",
    "likes_count": 5,
    "is_liked": true,
    "comments": [
        {
            "id": 1,
            "author": "user_id",
            "author_email": "user@example.com",
            "content": "Great post!",
            "created_at": "2026-04-05T12:00:00Z"
        }
    ],
    "created_at": "2026-04-05T12:00:00Z",
    "updated_at": "2026-04-05T12:00:00Z"
}
```

**Error Response (404):**
```json
{
    "detail": "Not found."
}
```

---

### PUT /api/v1/posts/\<int:pk\>/
### PATCH /api/v1/posts/\<int:pk\>/
Update a post. Only the post author can edit.

**Auth:** Bearer Token (owner or admin)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| title | string | No (PATCH) / Yes (PUT) |
| content | string | No (PATCH) / Yes (PUT) |
| tags | string | No |

**Success Response (200):** Updated post object

---

### DELETE /api/v1/posts/\<int:pk\>/
Delete a post.

**Auth:** Bearer Token (owner or admin)

**Success Response (204):** No content

---

### POST /api/v1/posts/\<int:pk\>/comment/
Add a comment to a post.

**Auth:** Bearer Token (IsAuthenticated)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| content | string | Yes |

**Success Response (201):**
```json
{
    "id": 1,
    "author": "user_id",
    "author_email": "user@example.com",
    "content": "Great post!",
    "created_at": "2026-04-05T12:00:00Z"
}
```

---

### DELETE /api/v1/posts/\<int:pk\>/comment/\<int:comment_id\>/
Delete a comment.

**Auth:** Bearer Token (comment author or admin)

**Success Response (204):** No content

---

### POST /api/v1/posts/\<int:pk\>/like/
Toggle a like on a post. Liking again removes the like.

**Auth:** Bearer Token (IsAuthenticated)

**Request Body:** None

**Success Response (201) — liked:**
```json
{
    "status": "liked",
    "likes_count": 6
}
```

**Success Response (200) — unliked:**
```json
{
    "status": "unliked",
    "likes_count": 5
}
```

---

## Resources (Knowledge Base) Endpoints

### GET /api/v1/knowledge-base/api/uploads/
List all of the authenticated user's uploaded resources.

**Auth:** Bearer Token (IsAuthenticated)

**Success Response (200):**
```json
[
    {
        "id": 1,
        "upload_type": "PDF",
        "file": "http://example.com/uploads/2026/04/05/filename.pdf",
        "description": "Django REST Framework guide",
        "created_at": "2026-04-05T12:00:00Z",
        "published_at": "2026-04-05T12:00:00Z",
        "status": "PENDING",
        "tags": ["django", "python"]
    }
]
```

---

### POST /api/v1/knowledge-base/api/uploads/
Upload a new resource.

**Auth:** Bearer Token (IsAuthenticated)

**Request Body (multipart/form-data):**
| Field | Type | Required |
|---|---|---|
| upload_type | string ("PDF", "EBOOK", "IMAGE") | Yes |
| file | file (pdf, doc, docx, jpg, jpeg, png) | Yes |
| description | string | No |
| tags | string (comma-separated) | No |

**Success Response (201):**
```json
{
    "id": 1,
    "upload_type": "PDF",
    "file": "http://example.com/uploads/2026/04/05/filename.pdf",
    "description": "Django REST Framework guide",
    "created_at": "2026-04-05T12:00:00Z",
    "published_at": null,
    "status": "PENDING",
    "tags": ["django"]
}
```

**Error Response (400):**
```json
{
    "error": "File type not allowed."
}
```

---

### GET /api/v1/knowledge-base/api/uploads/\<int:pk\>/
Retrieve a single uploaded resource (owner only).

**Auth:** Bearer Token (owner)

**Success Response (200):** Single upload object (same shape as POST)

**Error Response (404):**
```json
{
    "detail": "Not found."
}
```

---

### PUT /api/v1/knowledge-base/api/uploads/\<int:pk\>/
### PATCH /api/v1/knowledge-base/api/uploads/\<int:pk\>/
Update an uploaded resource.

**Auth:** Bearer Token (owner or admin)

**Request Body:** Same as POST (all optional for PATCH)

**Success Response (200):** Updated upload object

---

### DELETE /api/v1/knowledge-base/api/uploads/\<int:pk\>/
Delete an uploaded resource.

**Auth:** Bearer Token (owner or admin)

**Success Response (204):** No content

---

### GET /api/v1/knowledge-base/api/uploads/published/
List all approved/published resources (visible to all authenticated users).

**Auth:** Bearer Token (IsAuthenticated)

**Success Response (200):** Array of approved upload objects

---

### GET /api/v1/knowledge-base/api/uploads/mine/
List only the authenticated user's own uploads.

**Auth:** Bearer Token (IsAuthenticated)

**Success Response (200):** Array of the current user's upload objects

---

### PATCH /api/v1/knowledge-base/api/uploads/\<int:pk\>/status/
Approve or reject a pending upload. Approved/rejected uploads cannot be changed.

**Auth:** Bearer Token (IsAdminUser)

**Request Body:**
| Field | Type | Required |
|---|---|---|
| status | string ("APPROVED", "REJECTED") | Yes |

**Success Response (200):**
```json
{
    "status": "success",
    "message": "Status updated successfully."
}
```

**Error Response (400):**
```json
{
    "status": "error",
    "message": "Cannot change status from APPROVED to PENDING."
}
```

---

## API Documentation Endpoints

These endpoints are auto-generated by drf-spectacular.

| Method | Path | Description |
|---|---|---|
| GET | `/api/schema/` | OpenAPI 3 schema (YAML/JSON) |
| GET | `/api/schema/swagger-ui/` | Interactive Swagger UI |
| GET | `/api/schema/redoc/` | ReDoc documentation viewer |

---

## Notes

- **Events & RSVP** — Not yet implemented.
- **Notifications** — Not yet implemented.
- **Login TOTP step** (`LoginTOTPView`) — Defined in `apps/authentication/views.py` but not yet wired to a URL.
- **Users app** — Views exist in `apps/users/views.py` but the app is not registered in `config/urls.py`. Endpoints listed above are not yet accessible.

# Below are the Requsest body format and response to expect when a request is successful

- ## When creating a job posting - Post Request

```json
# This is how your request body will be like

{
    "title": "Software Developer",
    "company": "Tech Solutions Inc.",
    "description": "We are looking for a skilled software developer to join our team. The ideal candidate will have experience with Python, JavaScript, and web development frameworks.",
    "location": "New York, USA",
    "employment_type": "Full Time",
    "skills": [
        {"name": "Python"},
        {"name": "JavaScript"},
        {"name": "Django"},
        {"name": "React"},
        {"name": "SQL"}
    ],
    "salary": 200000,
    "application_deadline": "2024-12-31"
}

And a successful response will return

{
    "job": "http://localhost:8003/job/d283a127-b33c-4377-b90c-0cfcdc3fa945/",
    "skills": [
        {
            "name": "Django"
        },
        {
            "name": "Javascript"
        },
        {
            "name": "Python"
        },
        {
            "name": "React"
        },
        {
            "name": "Sql"
        }
    ],
    "employment_type": "Full Time",
    "title": "Software Developer",
    "company": "Tech Solutions Inc.",
    "location": "New York, Usa",
    "description": "We are looking for a skilled software developer to join our team. the ideal candidate will have experience with python, javascript, and web development frameworks.",
    "application_deadline": "2024-12-31",
    "salary": "200000.00",
    "created_at": "2024-12-18",
    "posted_by": "Admin@Admin.Com"
}
```

- ## When listing out all the job posting or trying to retrieve a singular instance - Get request

This is a list of all instance

```json
[
    {
        "job": "http://localhost:8003/job/3477bd05-2ab1-4468-a31b-0838bb3e96d4/",
        "skills": [
            {
                "name": "Django"
            },
            {
                "name": "Javascript"
            },
            {
                "name": "Python"
            },
            {
                "name": "React"
            },
            {
                "name": "Sql"
            }
        ],
        "employment_type": "Full Time",
        "title": "Software Developer",
        "company": "Tech Solutions Inc.",
        "location": "New York, Usa",
        "description": "We are looking for a skilled software developer to join our team. the ideal candidate will have experience with python, javascript, and web development frameworks.",
        "application_deadline": "2024-12-31",
        "salary": "20.00",
        "created_at": "2024-12-18",
        "posted_by": "Admin@Admin.Com"
    }
]
```

This is a singular instance

```json
{
        "job": "http://localhost:8003/job/3477bd05-2ab1-4468-a31b-0838bb3e96d4/",
        "skills": [
            {
                "name": "Django"
            },
            {
                "name": "Javascript"
            },
            {
                "name": "Python"
            },
            {
                "name": "React"
            },
            {
                "name": "Sql"
            }
        ],
        "employment_type": "Full Time",
        "title": "Software Developer",
        "company": "Tech Solutions Inc.",
        "location": "New York, Usa",
        "description": "We are looking for a skilled software developer to join our team. the ideal candidate will have experience with python, javascript, and web development frameworks.",
        "application_deadline": "2024-12-31",
        "salary": "20.00",
        "created_at": "2024-12-18",
        "posted_by": "Admin@Admin.Com"
}
```

> **N.B:** The difference between the list of instanceand singular instance is that the list returns a list as in python `list` datatype and a singular instance returns a `dict` datatype.

The request body for update request is the same as post request.

# Personal Blogging Platform

A full-stack blogging platform built with **Flask** that allows users to register, create profiles, publish blog posts, comment on articles, and interact through a responsive web interface.

The project demonstrates modern Flask development practices including authentication, role-based authorization, database migrations, rich text editing, file uploads, and PostgreSQL integration.

> **Status:** Work in Progress

---

## Features

### Content Management

* Create blog posts
* Edit existing posts
* Delete posts
* Rich text editing with CKEditor
* Display latest and archived posts
* User comments section

### User Management

* User registration
* Secure password hashing
* Login & logout
* User profiles
* Profile picture upload
* User settings page

### Authentication & Authorization

* Flask-Login authentication
* Admin-only routes
* Role-based permissions
* Protected pages

### Community Features

* Post comments
* Author profiles
* Personal post history
* User comment history

### Contact

* Contact form
* Email notifications via SMTP

---

## Technology

* Python
* Flask
* SQLAlchemy
* PostgreSQL
* Flask-Migrate
* Flask-Login
* Flask-WTF
* Flask-Bootstrap
* Flask-CKEditor

---

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/project.git
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run database migrations

```bash
flask db upgrade
```

Start the application

```bash
python app.py
```

---

## Screenshots

Future versions of this README will include screenshots of:

* Home page
* Blog detail page
* User profile
* Admin dashboard
* Post editor

---

## Planned Features

The project is actively being developed.

Upcoming improvements include:

* Email account activation
* Password reset
* User profile editing
* Password change page
* Better image management
* Search functionality
* Categories & tags
* Pagination

---

## What I Learned

This project provided hands-on experience with:

* Flask application architecture
* SQLAlchemy ORM
* Database migrations
* Authentication and authorization
* File uploads
* Form validation
* PostgreSQL integration
* Rich text editing
* Secure password hashing


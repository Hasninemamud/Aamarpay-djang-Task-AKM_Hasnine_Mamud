# Payment Gateway Integration and File Upload System

## Project Overview

This is a Django-based web application that allows users to upload files only after completing a payment through aamarPay. The system includes file processing capabilities using Celery for background tasks to count words in uploaded files.

## Features

- User authentication with Django's built-in user model
- Payment gateway integration with aamarPay sandbox
- File upload functionality (only after successful payment)
- Word count processing via Celery background tasks
- Payment and activity logging
- RESTful API interface
- Bootstrap-based frontend
- Django Admin for data inspection

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: SQLite (development)
- **Task Queue**: Celery with Redis
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Payment Gateway**: aamarPay Sandbox
- **File Processing**: python-docx for .docx files

## Project Structure

```
payment_file_upload/
├── payment_file_upload/     # Project settings
│   ├── __init__.py
│   ├── celery.py           # Celery configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                   # Main app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py            # Django admin configuration
│   ├── apps.py
│   ├── models.py           # Database models
│   ├── serializers.py      # DRF serializers
│   ├── tasks.py            # Celery tasks
│   ├── urls.py             # App URLs
│   └── views.py            # API and view logic
├── media/                  # Uploaded files
├── static/                 # Static files
├── templates/              # HTML templates
│   └── core/
│       ├── base.html
│       ├── dashboard.html
│       └── login.html
├── venv/                   # Virtual environment
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── manage.py
└── README.md               # This file
```

## Installation and Setup

### Prerequisites

- Python 3.8+
- Redis server
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/payment-file-upload.git
cd payment-file-upload
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Step 5: Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Start Redis Server

```bash
# Ubuntu/Debian
sudo service redis-server start

# macOS
brew services start redis

# Windows
redis-server
```

### Step 8: Start Celery Worker

Open a new terminal and run:

```bash
celery -A your_project worker --loglevel=info --pool=solo
```

### Step 9: Start Django Server

Open another terminal and run:

```bash
python manage.py runserver
```

### Step 10: Access the Application

- Frontend: http://localhost:8000/dashboard/
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/

## Usage

### 1. User Registration and Login

1. Create a user account through Django Admin
2. Log in at http://localhost:8000/login/

### 2. Payment Process

1. Click "Pay ৳100 to Upload Files" button
2. Complete payment using aamarPay sandbox credentials:
   - Card Number: 6262 6262 6262 6262
   - Expiry Date: Any future date
   - CVV: 123
   - OTP: 123456
3. After successful payment, you'll be redirected to the dashboard

### 3. File Upload

1. After successful payment, the file upload form will be enabled
2. Select a .txt or .docx file
3. Click "Upload File"
4. The file will be processed in the background by Celery

### 4. View Results

- Check "Uploaded Files" section for file status and word count
- View "Payment History" for transaction details
- Check "Recent Activity" for all user actions

## API Documentation

### Authentication

Get an authentication token:

```bash
curl -X POST http://localhost:8000/api/auth-token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### Endpoints

| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|----------------------|
| POST | `/api/initiate-payment/` | Initiate payment | Yes |
| GET | `/api/payment/success/` | Payment success callback | No |
| GET | `/api/payment/fail/` | Payment failure callback | No |
| GET | `/api/payment/cancel/` | Payment cancel callback | No |
| GET | `/api/get-token/` | Get user token | Yes |
| GET | `/api/files/` | List user files | Yes |
| POST | `/api/files/` | Upload file | Yes |
| GET | `/api/transactions/` | List payment history | Yes |
| GET | `/api/activity/` | List user activities | Yes |

### Example Requests

#### Upload a File

```bash
curl -X POST http://localhost:8000/api/files/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -F "file=@/path/to/your/file.txt"
```

#### List Files

```bash
curl -X GET http://localhost:8000/api/files/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## Configuration

### aamarPay Configuration

Update the `AAMARPAY_CONFIG` in `settings.py` for production:

```python
AAMARPAY_CONFIG = {
    'store_id': 'your_store_id',
    'signature_key': 'your_signature_key',
    'endpoint': 'https://secure.aamarpay.com/jsonpost.php',
    'amount': 100,
    'currency': 'BDT',
    'success_url': 'https://yourdomain.com/api/payment/success/',
    'fail_url': 'https://yourdomain.com/api/payment/fail/',
    'cancel_url': 'https://yourdomain.com/api/payment/cancel/',
}
```

## Deployment

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t payment-file-upload .
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

### Common Issues

1. **PermissionError on Windows**: Run Django and Celery as Administrator
2. **Redis connection issues**: Ensure Redis server is running
3. **Payment gateway errors**: Verify aamarPay credentials
4. **File processing errors**: Check Celery worker logs
5. **Authentication errors**: Verify token is being sent correctly




- User authentication and activity logging
- RESTful API implementation

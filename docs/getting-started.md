---
layout: default
title: Getting Started
nav_order: 2
description: "Step-by-step guide to set up CourseWagon development environment"
---

# Getting Started
{: .no_toc }

Get CourseWagon up and running on your local machine in minutes.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

- **Node.js**: v18 or higher ([Download](https://nodejs.org/))
- **Python**: 3.10 or higher ([Download](https://www.python.org/))
- **MySQL**: 8.0 or higher ([Download](https://dev.mysql.com/downloads/mysql/))
- **Git**: Latest version ([Download](https://git-scm.com/))

### Required Accounts & API Keys

- **Firebase Project**: For authentication ([Create Project](https://console.firebase.google.com/))
- **Google Gemini API Key**: For AI content generation ([Get API Key](https://makersuite.google.com/app/apikey))
- **Azure Storage Account** (Optional): For cloud storage ([Create Account](https://portal.azure.com/))
- **Google Cloud Storage** (Recommended): Primary storage solution
- **Gmail Account**: For email notifications (with app password)

---

## Clone the Repository

```bash
git clone https://github.com/Uttam-Mahata/coursewagon.git
cd coursewagon
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd angular-client
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable **Authentication** → **Email/Password** sign-in method
4. Copy your Firebase configuration

### 4. Update Environment Configuration

Edit `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
  firebase: {
    apiKey: "YOUR_FIREBASE_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
  }
};
```

### 5. Run Development Server

```bash
npm start
```

The application will be available at [http://localhost:4200](http://localhost:4200)

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run unit tests
- `npm run watch` - Watch mode for development

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd python-server
```

### 2. Install uv Package Manager (Recommended)

```bash
pip install uv
```

### 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

Or using standard pip:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:

```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/coursewagon

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key
JWT_ACCESS_TOKEN_EXPIRES_HOURS=1
JWT_REFRESH_TOKEN_EXPIRES_DAYS=30

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH=./coursewagon-firebase-adminsdk.json

# Google Cloud Storage (Primary)
GCS_BUCKET_NAME=coursewagon-storage-bucket
GCS_PROJECT_ID=your-project-id
GCS_CREDENTIALS_PATH=./gcs-service-account.json

# Azure Storage (Fallback)
AZURE_STORAGE_CONNECTION_STRING=your-azure-connection-string

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com

# Mailgun (Backup Email Service)
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=mg.yourdomain.com

# CORS Configuration
CORS_ORIGINS=http://localhost:4200,https://www.coursewagon.live
```

### 5. Set Up Firebase Admin SDK

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save the JSON file as `coursewagon-firebase-adminsdk.json` in `python-server/`

### 6. Set Up Database

Create a MySQL database:

```bash
mysql -u root -p
CREATE DATABASE coursewagon;
```

### 7. Run Database Migrations

The migrations will run automatically on application startup, or you can run them manually:

```bash
python migrations/add_welcome_email_sent_column.py
```

### 8. Run Development Server

```bash
uvicorn app:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

### API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Verify Installation

### 1. Test Frontend

Open [http://localhost:4200](http://localhost:4200) in your browser. You should see the CourseWagon home page.

### 2. Test Backend

Visit [http://localhost:8000/api/health](http://localhost:8000/api/health). You should see:

```json
{
  "status": "healthy",
  "timestamp": "2024-10-10T15:30:00.000Z"
}
```

### 3. Test Authentication

1. Go to [http://localhost:4200](http://localhost:4200)
2. Click "Get Started" or "Login"
3. Try creating a new account
4. You should receive a welcome email

---

## Common Issues

### Port Already in Use

If port 4200 or 8000 is already in use:

**Frontend:**
```bash
ng serve --port 4201
```

**Backend:**
```bash
uvicorn app:app --reload --port 8001
```

### Database Connection Error

Verify your MySQL server is running:

```bash
# Linux/Mac
sudo systemctl status mysql

# Windows
net start MySQL80
```

### Firebase Authentication Error

Ensure:
1. Firebase configuration is correct in `environment.ts`
2. Email/Password authentication is enabled in Firebase Console
3. Service account JSON file is in the correct location

### Module Not Found

Reinstall dependencies:

**Frontend:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Backend:**
```bash
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```

---

## Next Steps

Now that you have CourseWagon running locally:

1. 📖 Read the [User Guide](user-guide) to learn how to use the platform
2. 🏗️ Explore the [System Architecture](architecture) to understand how it works
3. 💻 Check the [Developer Guide](developer-guide) to start contributing
4. 🚀 Learn about [Deployment](deployment) to production

---

## Need Help?

- 📧 Email: [contact@coursewagon.live](mailto:contact@coursewagon.live)
- 🐛 Issues: [GitHub Issues](https://github.com/Uttam-Mahata/coursewagon/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Uttam-Mahata/coursewagon/discussions)

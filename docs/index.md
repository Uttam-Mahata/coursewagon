---
layout: default
title: Home
nav_order: 1
description: "CourseWagon is an enterprise-grade educational platform that leverages generative AI for dynamic course content generation."
permalink: /
---

# CourseWagon Documentation
{: .fs-9 }

An enterprise-grade educational platform powered by AI for dynamic course content generation and comprehensive learning management.
{: .fs-6 .fw-300 }

[Get Started](getting-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/Uttam-Mahata/coursewagon){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## Overview

CourseWagon integrates modern web technologies with advanced AI capabilities to deliver a scalable, secure, and user-centric educational experience. Built with Angular 19 on the frontend and FastAPI on the backend, it leverages Google Gemini AI for intelligent content generation.

### Key Features

- **🤖 AI-Powered Content Generation**: Automatically generate course subjects, chapters, topics, and detailed content using Google Gemini AI
- **📚 Comprehensive Course Management**: Create and organize courses with hierarchical structure (Courses → Subjects → Chapters → Topics → Content)
- **🔐 Real-time Authentication**: Secure user authentication with Firebase Auth and JWT tokens
- **☁️ Cloud Storage Integration**: Store images and media using Google Cloud Storage, Azure Blob Storage, and Firebase Storage
- **🎨 Responsive UI**: Modern, responsive interface built with Angular 19 and Tailwind CSS
- **👨‍💼 Admin Dashboard**: Comprehensive admin panel for managing users, courses, and testimonials
- **📐 Mathematical Content Support**: Render mathematical equations using KaTeX and MathJax
- **📊 Diagram Support**: Create and display diagrams using Mermaid.js
- **📧 Email Notifications**: Automated email system for password resets and user notifications

---

## Tech Stack

### Frontend
- **Framework**: Angular 19
- **Styling**: Tailwind CSS 4.1
- **Authentication**: Firebase Auth
- **Markdown**: ngx-markdown with Prism.js
- **Math Rendering**: KaTeX, MathJax
- **Diagrams**: Mermaid.js
- **Icons**: Font Awesome

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **AI Integration**: Google Gemini AI
- **Storage**: Google Cloud Storage (primary), Azure Blob Storage, Firebase Storage
- **Authentication**: JWT tokens with Firebase Admin SDK
- **Email Service**: Gmail SMTP (primary), Mailgun (backup)
- **Deployment**: Google Cloud Run / Microsoft Azure

---

## Quick Links

- [Getting Started Guide](getting-started) - Set up your development environment
- [System Architecture](architecture) - Understand the system design
- [API Reference](api-reference) - Explore API endpoints
- [User Guide](user-guide) - Learn how to use CourseWagon
- [Developer Guide](developer-guide) - Contribute to the project
- [Deployment Guide](deployment) - Deploy to production
- [FAQ & Troubleshooting](faq) - Common issues and solutions

---

## Live Application

Visit the live application at [https://www.coursewagon.live](https://www.coursewagon.live)

---

## Support

For support, email [contact@coursewagon.live](mailto:contact@coursewagon.live) or open an issue in the [GitHub repository](https://github.com/Uttam-Mahata/coursewagon/issues).

---

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Uttam-Mahata/coursewagon/blob/main/LICENSE) file for details.

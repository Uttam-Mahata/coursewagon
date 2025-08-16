# CourseWagon Flutter Mobile App

A Flutter mobile application for the CourseWagon educational platform with AI-powered course generation.

## Features

- **Authentication**
  - Email/Password login and registration
  - Google Sign-In integration
  - Password reset functionality
  - Remember me option
  - Secure token storage

- **Course Management**
  - Browse and search courses
  - Create courses with AI assistance
  - View course details with subjects and chapters
  - Course image generation
  - Progress tracking

- **Mobile-Optimized UI**
  - Material 3 design system
  - Light/Dark theme support
  - Bottom navigation
  - Responsive layouts
  - Cached network images
  - Shimmer loading effects

- **Content Viewing**
  - Markdown content rendering
  - Mathematical equation support
  - Mermaid diagram support
  - Topic-based learning structure

## Tech Stack

- **Flutter 3.5+** - Cross-platform mobile framework
- **Firebase** - Authentication and cloud storage
- **Provider** - State management
- **Go Router** - Navigation and routing
- **Dio** - HTTP networking
- **Material Design 3** - UI components

## Getting Started

### Prerequisites

- Flutter SDK 3.5.0 or higher
- Android Studio / Xcode
- Firebase project setup

### Installation

1. Install dependencies:
```bash
flutter pub get
```

2. Run the app:
```bash
# For iOS
flutter run -d ios

# For Android
flutter run -d android
```

### Build for Production

```bash
# Android APK
flutter build apk --release

# Android App Bundle
flutter build appbundle --release

# iOS
flutter build ios --release
```

## Project Structure

```
lib/
├── core/
│   ├── config/       # App configuration
│   ├── constants/    # Constants
│   ├── theme/        # Theme configuration
│   └── utils/        # Utility functions
├── data/
│   ├── models/       # Data models
│   ├── repositories/ # Data repositories
│   └── providers/    # Data providers
├── presentation/
│   ├── screens/      # Screen widgets
│   │   ├── auth/     # Authentication screens
│   │   ├── home/     # Home screen
│   │   ├── courses/  # Course screens
│   │   ├── subjects/ # Subject screens
│   │   ├── content/  # Content viewing
│   │   └── profile/  # Profile screen
│   └── widgets/      # Reusable widgets
├── services/         # Business logic services
└── main.dart         # App entry point
```

## API Integration

The app connects to the CourseWagon backend API at:
- Production: `https://coursewagon-backend.victoriousforest-3a334815.southeastasia.azurecontainerapps.io/api`

## Firebase Configuration

The app uses Firebase for:
- Authentication (Google Sign-In)
- Cloud Storage
- Analytics (optional)

Firebase configuration is managed through `firebase_options.dart`.

## State Management

The app uses Provider for state management with the following providers:
- `AuthService` - Authentication state
- `CourseService` - Course data management
- Additional services for subjects, chapters, and content

## Navigation

Navigation is handled by Go Router with:
- Auth-based routing guards
- Deep linking support
- Bottom navigation
- Named routes

## Security

- Secure token storage using flutter_secure_storage
- JWT-based API authentication
- Certificate pinning (optional)
- Biometric authentication (optional)

## Development

### Running Tests
```bash
flutter test
```

### Code Generation
```bash
flutter pub run build_runner build
```

### Debugging
- Use Flutter DevTools for performance profiling
- Enable network proxy for API debugging
- Use Flutter Inspector for UI debugging

## License

This project is proprietary and confidential.
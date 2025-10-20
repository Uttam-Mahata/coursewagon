#!/bin/bash

# Generate environment files from environment variables
# This script is used in CI/CD to inject secrets at build time

# Generate environment.ts (development/fallback)
cat > src/environments/environment.ts << EOF
export const environment = {
  production: false,
  apiUrl: '${API_URL}',
  apiBaseUrl: '${API_BASE_URL}',
  courseApiUrl: '${COURSE_API_URL}',
  authApiUrl: '${AUTH_API_URL}',
  firebase: {
    apiKey: "${FIREBASE_API_KEY}",
    authDomain: "${FIREBASE_AUTH_DOMAIN}",
    projectId: "${FIREBASE_PROJECT_ID}",
    storageBucket: "${FIREBASE_STORAGE_BUCKET}",
    messagingSenderId: "${FIREBASE_MESSAGING_SENDER_ID}",
    appId: "${FIREBASE_APP_ID}"
  }
};
EOF

# Generate environment.prod.ts (production)
cat > src/environments/environment.prod.ts << EOF
export const environment = {
  production: true,
  apiUrl: '${API_URL}',
  apiBaseUrl: '${API_BASE_URL}',
  courseApiUrl: '${COURSE_API_URL}',
  authApiUrl: '${AUTH_API_URL}',
  firebase: {
    apiKey: "${FIREBASE_API_KEY}",
    authDomain: "${FIREBASE_AUTH_DOMAIN}",
    projectId: "${FIREBASE_PROJECT_ID}",
    storageBucket: "${FIREBASE_STORAGE_BUCKET}",
    messagingSenderId: "${FIREBASE_MESSAGING_SENDER_ID}",
    appId: "${FIREBASE_APP_ID}"
  }
};
EOF

echo "✅ Generated environment.ts and environment.prod.ts from environment variables"

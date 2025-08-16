# Media Upload Implementation for Course Content

## Overview
This implementation adds the ability to upload and manage images/videos within course content. Media files are stored in Azure Blob Storage and can be embedded at specific parts of the content.

## Backend Implementation

### 1. Database Schema
Created a new `media` table to store media metadata:
```sql
CREATE TABLE media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_id INT NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_type ENUM('image', 'video') NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INT,
    mime_type VARCHAR(100),
    position INT,
    caption TEXT,
    alt_text VARCHAR(255),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
);
```

### 2. Models
- **Media Model** (`models/media.py`): Defines the media entity with all metadata fields
- **Content Model** (updated): Added relationship to media files

### 3. Repositories
- **MediaRepository** (`repositories/media_repo.py`): Handles CRUD operations for media records
- **ContentRepository** (updated): Added method to get content by ID

### 4. Services
- **MediaService** (`services/media_service.py`): 
  - Handles file uploads to Azure Storage
  - Manages media metadata in database
  - Validates file types and sizes
  - Supports reordering of media files

### 5. Routes
- **MediaRoutes** (`routes/media_routes.py`):
  - `POST /courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media` - Upload media
  - `GET /courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media` - Get media list
  - `PUT /courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media/{media_id}` - Update media metadata
  - `DELETE /courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media/{media_id}` - Delete media
  - `POST /courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/media/reorder` - Reorder media

## Frontend Implementation

### 1. Services
- **MediaService** (`services/media.service.ts`):
  - Handles file uploads with progress tracking
  - Validates files before upload
  - Manages all media-related API calls

### 2. Components
- **TopicsContentComponent** (updated):
  - Added media upload UI
  - Media gallery to display uploaded files
  - Copy embed code functionality
  - Delete media functionality

### 3. Features
- File validation (size and type)
- Upload progress tracking
- Media gallery with preview
- Copy markdown/HTML embed code
- Delete media with confirmation
- Support for both images and videos

## How to Use

### 1. Uploading Media
1. Navigate to a topic's content page
2. Click "Upload Media" button
3. Select an image or video file
4. Optionally add caption and alt text
5. Click "Upload"

### 2. Embedding Media in Content
1. After uploading, click the edit icon on any media file
2. The embed code will be copied to clipboard
3. Paste the code into your content where needed

### 3. Supported Formats
- **Images**: JPEG, PNG, GIF, WebP, SVG (max 10MB)
- **Videos**: MP4, WebM, AVI, MOV, MKV (max 100MB)

## Environment Variables Required
```
AZURE_STORAGE_ACCOUNT_NAME=your_account_name
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_CONTAINER_NAME=coursewagon-images
```

## Migration
Run the SQL migration file: `migrations/add_media_table.sql`

## Security Features
- File type validation on both frontend and backend
- File size limits
- User authentication required for uploads
- Course ownership verification
- Secure Azure Storage with SAS tokens

## Future Enhancements
- Drag-and-drop file upload
- Bulk upload support
- Image editing (crop, resize)
- Video thumbnail generation
- CDN integration for faster delivery
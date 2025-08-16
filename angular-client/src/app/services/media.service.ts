import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType, HttpResponse } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../environments/environment';

export interface MediaFile {
  id: number;
  content_id: number;
  file_url: string;
  file_type: 'image' | 'video';
  file_name: string;
  file_size?: number;
  mime_type?: string;
  position?: number;
  caption?: string;
  alt_text?: string;
  uploaded_at?: string;
}

export interface MediaUploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

@Injectable({
  providedIn: 'root'
})
export class MediaService {
  private apiUrl = environment.courseApiUrl;

  constructor(private http: HttpClient) { }

  // Upload media file with progress tracking
  uploadMedia(
    courseId: number, 
    subjectId: number, 
    chapterId: number, 
    topicId: number,
    file: File,
    fileType: 'image' | 'video' = 'image',
    metadata?: { position?: number; caption?: string; alt_text?: string }
  ): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);
    
    if (metadata?.position !== undefined) {
      formData.append('position', metadata.position.toString());
    }
    if (metadata?.caption) {
      formData.append('caption', metadata.caption);
    }
    if (metadata?.alt_text) {
      formData.append('alt_text', metadata.alt_text);
    }

    return this.http.post(
      `${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/media`,
      formData,
      {
        reportProgress: true,
        observe: 'events'
      }
    ).pipe(
      map(event => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          const progress: MediaUploadProgress = {
            loaded: event.loaded,
            total: event.total,
            percentage: Math.round((100 * event.loaded) / event.total)
          };
          return { type: 'progress', data: progress };
        } else if (event instanceof HttpResponse) {
          return { type: 'complete', data: event.body };
        }
        return { type: 'other', data: event };
      })
    );
  }

  // Get all media files for a topic
  getMediaByTopic(
    courseId: number, 
    subjectId: number, 
    chapterId: number, 
    topicId: number
  ): Observable<MediaFile[]> {
    return this.http.get<MediaFile[]>(
      `${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/media`
    );
  }

  // Update media metadata
  updateMedia(
    courseId: number, 
    subjectId: number, 
    chapterId: number, 
    topicId: number,
    mediaId: number,
    metadata: { caption?: string; alt_text?: string; position?: number }
  ): Observable<MediaFile> {
    return this.http.put<MediaFile>(
      `${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/media/${mediaId}`,
      metadata
    );
  }

  // Delete media file
  deleteMedia(
    courseId: number, 
    subjectId: number, 
    chapterId: number, 
    topicId: number,
    mediaId: number
  ): Observable<any> {
    return this.http.delete(
      `${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/media/${mediaId}`
    );
  }

  // Reorder media files
  reorderMedia(
    courseId: number, 
    subjectId: number, 
    chapterId: number, 
    topicId: number,
    mediaOrder: { [mediaId: string]: number }
  ): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/media/reorder`,
      { media_order: mediaOrder }
    );
  }

  // Get supported file formats
  getSupportedFormats(): Observable<{ image: string[]; video: string[] }> {
    return this.http.get<{ image: string[]; video: string[] }>(
      `${this.apiUrl}/media/supported-formats`
    );
  }

  // Validate file before upload
  validateFile(file: File, fileType: 'image' | 'video'): { valid: boolean; error?: string } {
    const maxSizeImage = 10 * 1024 * 1024; // 10MB for images
    const maxSizeVideo = 100 * 1024 * 1024; // 100MB for videos
    
    const imageFormats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'];
    const videoFormats = ['video/mp4', 'video/webm', 'video/avi', 'video/quicktime', 'video/x-matroska'];

    if (fileType === 'image') {
      if (!imageFormats.includes(file.type)) {
        return { valid: false, error: 'Invalid image format. Supported formats: JPEG, PNG, GIF, WebP, SVG' };
      }
      if (file.size > maxSizeImage) {
        return { valid: false, error: 'Image file too large. Maximum size: 10MB' };
      }
    } else if (fileType === 'video') {
      if (!videoFormats.includes(file.type)) {
        return { valid: false, error: 'Invalid video format. Supported formats: MP4, WebM, AVI, MOV, MKV' };
      }
      if (file.size > maxSizeVideo) {
        return { valid: false, error: 'Video file too large. Maximum size: 100MB' };
      }
    }

    return { valid: true };
  }
}
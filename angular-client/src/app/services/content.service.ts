import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { CacheService } from './cache.service';

@Injectable({
  providedIn: 'root'
})
export class ContentService {
  private apiUrl = environment.courseApiUrl;

  constructor(
    private http: HttpClient,
    private cacheService: CacheService
  ) { }
  
  generateContent(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`Generating content for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/generate_content`, {}).pipe(
      tap(() => {
        // Invalidate content cache after generation
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`;
        this.cacheService.invalidate(cachePattern);
        console.log(`[Cache] Invalidated content cache for topic ${topicId}`);
      })
    );
  }

  getContent(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`[ContentService] Fetching content for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`);
  }

  // New CRUD operations
  createContentManual(courseId: number, subjectId: number, chapterId: number, topicId: number, contentText: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`,
      { content: contentText }
    ).pipe(
      tap(() => {
        // Invalidate content cache after creation
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }

  updateContent(courseId: number, subjectId: number, chapterId: number, topicId: number, contentText: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`,
      { content: contentText }
    ).pipe(
      tap(() => {
        // Invalidate content cache after update
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }

  deleteContent(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`).pipe(
      tap(() => {
        // Invalidate content cache after deletion
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }

  // Video operations
  uploadVideo(courseId: number, subjectId: number, chapterId: number, topicId: number, videoFile: File): Observable<any> {
    const formData = new FormData();
    formData.append('video', videoFile);

    console.log(`[ContentService] Uploading video for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/video`, formData).pipe(
      tap(() => {
        // Invalidate content cache after video upload
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }

  deleteVideo(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`[ContentService] Deleting video for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.delete(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/video`).pipe(
      tap(() => {
        // Invalidate content cache after video deletion
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }
}

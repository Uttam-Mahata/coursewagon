import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { CacheService } from './cache.service';

@Injectable({
  providedIn: 'root'
})
export class TopicService {
  private apiUrl = environment.courseApiUrl;

  constructor(
    private http: HttpClient,
    private cacheService: CacheService
  ) { }
  
  generateTopics(courseId: number, subjectId: number, chapterId: number): Observable<any> {
    console.log(`Generating topics for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}`);
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/generate_topics`, {}).pipe(
      tap(() => {
        // Invalidate topics cache after successful generation
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics`;
        this.cacheService.invalidate(cachePattern);
        console.log(`[Cache] Invalidated topics cache for chapter ${chapterId}`);
      })
    );
  }
  
  getTopics(courseId: number, subjectId: number, chapterId: number): Observable<any> {
    console.log(`Fetching topics for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}`);
    return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics`);
  }
  
  // Get topic details by ID
  getTopicDetails(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`Fetching topic details for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}`);
  }
  
  // CRUD operations
  createTopic(courseId: number, subjectId: number, chapterId: number, name: string): Observable<any> {
    console.log(`Creating topic for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}`);
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics`, { name }).pipe(
      tap(() => {
        // Invalidate topics cache after creation
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }

  updateTopic(courseId: number, subjectId: number, chapterId: number, topicId: number, name: string): Observable<any> {
    console.log(`Updating topic for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.put(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}`, { name }).pipe(
      tap(() => {
        // Invalidate topics cache after update
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }

  deleteTopic(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`Deleting topic for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.delete(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}`).pipe(
      tap(() => {
        // Invalidate topics cache after deletion
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }
}

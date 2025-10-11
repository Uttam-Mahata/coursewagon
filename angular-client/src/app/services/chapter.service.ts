import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { CacheService } from './cache.service';

@Injectable({
  providedIn: 'root'
})
export class ChapterService {
  private apiUrl = environment.courseApiUrl;

  constructor(
    private http: HttpClient,
    private cacheService: CacheService
  ) { }
  
  generateChapters(courseId: number, subjectId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/generate_chapters`, {}).pipe(
      tap(() => {
        // Invalidate chapters cache after successful generation
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters`;
        this.cacheService.invalidate(cachePattern);
        console.log(`[Cache] Invalidated chapters cache for subject ${subjectId}`);
      })
    );
  }
  
  getChapters(courseId: number, subjectId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters`);
  }
  
  // Get chapter details by ID
  getChapterDetails(courseId: number, subjectId: number, chapterId: number): Observable<any> {
    console.log(`Fetching chapter details for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}`);
    return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}`);
  }
  
  // Enhanced CRUD operations
  createChapter(courseId: number, subjectId: number, name: string): Observable<any> {
    console.log(`Creating chapter for course: ${courseId}, subject: ${subjectId}, name: ${name}`);
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters`, { name }).pipe(
      tap(() => {
        // Invalidate chapters cache after creation
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }

  updateChapter(courseId: number, subjectId: number, chapterId: number, name: string): Observable<any> {
    console.log(`Updating chapter for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}`);
    return this.http.put(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}`, { name }).pipe(
      tap(() => {
        // Invalidate chapters cache after update
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }

  deleteChapter(courseId: number, subjectId: number, chapterId: number): Observable<any> {
    console.log(`Deleting chapter for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}`);
    return this.http.delete(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}`).pipe(
      tap(() => {
        // Invalidate chapters cache after deletion
        const cachePattern = `http:${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters`;
        this.cacheService.invalidate(cachePattern);
      })
    );
  }
}

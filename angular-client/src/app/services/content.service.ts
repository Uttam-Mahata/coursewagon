import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ContentGenerationOptions {
  include_media_placeholders?: boolean;
}

export interface MediaPlacementRequest {
  media_id: number;
  position?: number;
  section_identifier?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ContentService {
  private apiUrl = environment.courseApiUrl;
  
  constructor(private http: HttpClient) { }
  
  generateContent(
    courseId: number, 
    subjectId: number, 
    chapterId: number, 
    topicId: number,
    options: ContentGenerationOptions = {}
  ): Observable<any> {
    console.log(`Generating content for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.post(
      `${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/generate_content`,
      options
    );
  }
  
  generateContentWithMediaSuggestions(
    courseId: number, 
    subjectId: number, 
    chapterId: number, 
    topicId: number
  ): Observable<any> {
    console.log(`Generating content with media suggestions for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.post(
      `${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/generate_content_with_media_suggestions`,
      {}
    );
  }
  
  insertMediaInContent(
    courseId: number, 
    subjectId: number, 
    chapterId: number, 
    topicId: number,
    placement: MediaPlacementRequest
  ): Observable<any> {
    console.log(`Inserting media in content for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.post(
      `${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/insert_media`,
      placement
    );
  }
  
  getContent(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`Fetching content for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`);
  }
  
  // New CRUD operations
  createContentManual(courseId: number, subjectId: number, chapterId: number, topicId: number, contentText: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`, 
      { content: contentText }
    );
  }
  
  updateContent(courseId: number, subjectId: number, chapterId: number, topicId: number, contentText: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`,
      { content: contentText }
    );
  }
  
  deleteContent(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/content`);
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ContentService {
  private apiUrl = environment.courseApiUrl;
  
  constructor(private http: HttpClient) { }
  
  generateContent(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`Generating content for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/generate_content`, {});
  }
  
  getContent(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`[ContentService] Fetching content for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
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

  // Video operations
  uploadVideo(courseId: number, subjectId: number, chapterId: number, topicId: number, videoFile: File): Observable<any> {
    const formData = new FormData();
    formData.append('video', videoFile);

    console.log(`[ContentService] Uploading video for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/video`, formData);
  }

  deleteVideo(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`[ContentService] Deleting video for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.delete(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}/video`);
  }
}

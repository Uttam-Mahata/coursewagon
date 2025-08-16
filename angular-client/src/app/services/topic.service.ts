import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TopicService {
  private apiUrl = environment.courseApiUrl;
  
  constructor(private http: HttpClient) { }
  
  generateTopics(courseId: number, subjectId: number, chapterId: number): Observable<any> {
    console.log(`Generating topics for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}`);
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/generate_topics`, {});
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
    return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics`, { name });
  }
  
  updateTopic(courseId: number, subjectId: number, chapterId: number, topicId: number, name: string): Observable<any> {
    console.log(`Updating topic for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.put(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}`, { name });
  }
  
  deleteTopic(courseId: number, subjectId: number, chapterId: number, topicId: number): Observable<any> {
    console.log(`Deleting topic for course: ${courseId}, subject: ${subjectId}, chapter: ${chapterId}, topic: ${topicId}`);
    return this.http.delete(`${this.apiUrl}/${courseId}/subjects/${subjectId}/chapters/${chapterId}/topics/${topicId}`);
  }
}

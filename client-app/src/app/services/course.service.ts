import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CourseService {
  private apiUrl = environment.courseApiUrl;
    constructor(private http: HttpClient) {}
  
    addCourse(name: string): Observable<any> {
      return this.http.post(`${this.apiUrl}/add_course`, { name });
    }
  
    getCourses(): Observable<any> {
      return this.http.get(this.apiUrl);
    }
  
    // Get course details by ID
    getCourseDetails(courseId: number): Observable<any> {
      return this.http.get(`${this.apiUrl}/${courseId}`);
    }
  
    getModuleDetails(courseId: number, subjectId: number, moduleId: number): Observable<any> {
      return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}`);
    }
  
    getTopicDetails(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number): Observable<any> {
      return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}/chapters/${chapterId}/topics/${topicId}`);
    }
  
    generateSubjects(courseId: number): Observable<any> {
      return this.http.post(`${this.apiUrl}/${courseId}/generate_subjects`, {});
    }
  
    
  
    getSubjects(courseId: number): Observable<any> {
      return this.http.get(`${this.apiUrl}/${courseId}/subjects`);
    }
  
    generateModules(courseId: number, subjectId: number): Observable<any> {
      return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/generate_modules`, {});
    }
  
    getModules(courseId: number, subjectId: number): Observable<any> {
      return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules`);
    }
  
    generateChapters(courseId: number, subjectId: number, moduleId: number): Observable<any> {
      return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}/generate_chapters`, {});
    }
  
    getChapters(courseId: number, subjectId: number, moduleId: number): Observable<any> {
      return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}/chapters`);
    }
  
    generateTopics(courseId: number, subjectId: number, moduleId: number, chapterId: number): Observable<any> {
      return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}/chapters/${chapterId}/generate_topics`, {});
    }
  
    getTopics(courseId: number, subjectId: number, moduleId: number, chapterId: number): Observable<any> {
      return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}/chapters/${chapterId}/topics`);
    }
  
    generateSubtopics(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number): Observable<any> {
      return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}/chapters/${chapterId}/topics/${topicId}/generate_subtopics`, {});
    }
  
    getSubtopics(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number): Observable<any> {
      return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}/chapters/${chapterId}/topics/${topicId}/subtopics`);
    }
  
    generateContent(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number, subtopicId: number): Observable<any> {
      return this.http.post(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}/chapters/${chapterId}/topics/${topicId}/subtopics/${subtopicId}/generate_content`, {});
    }
  
    
    getContent(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number, subtopicId: number): Observable<any> {
      return this.http.get(`${this.apiUrl}/${courseId}/subjects/${subjectId}/modules/${moduleId}/chapters/${chapterId}/topics/${topicId}/subtopics/${subtopicId}/content`);
    }
  }
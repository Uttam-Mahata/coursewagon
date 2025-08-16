import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TestimonialService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  /**
   * Get all approved testimonials for public display
   */
  getApprovedTestimonials(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/testimonials`);
  }

  /**
   * Get the current user's testimonial
   */
  getUserTestimonial(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/testimonials/my-testimonial`);
  }

  /**
   * Create a new testimonial
   */
  createTestimonial(quote: string, rating: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/testimonials`, { quote, rating });
  }

  /**
   * Update an existing testimonial
   */
  updateTestimonial(id: number, quote?: string, rating?: number): Observable<any> {
    const updateData: any = {};
    if (quote !== undefined) updateData.quote = quote;
    if (rating !== undefined) updateData.rating = rating;
    
    return this.http.put<any>(`${this.apiUrl}/testimonials/${id}`, updateData);
  }

  /**
   * Delete a testimonial
   */
  deleteTestimonial(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/testimonials/${id}`);
  }

  /**
   * Admin: Get all testimonials including unapproved
   */
  getAllTestimonials(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/testimonials/admin/all`);
  }

  /**
   * Admin: Approve/disapprove a testimonial
   */
  approveTestimonial(id: number, approved: boolean): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/testimonials/admin/${id}/approve`, { approved });
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private apiUrl = `${environment.apiUrl}/admin`;

  constructor(private http: HttpClient) { }

  /**
   * Get dashboard statistics
   */
  getDashboardStats(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/dashboard`);
  }

  /**
   * Get all users in the system
   */
  getAllUsers(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/users`);
  }

  /**
   * Get pending testimonials awaiting approval
   */
  getPendingTestimonials(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/testimonials/pending`);
  }

  /**
   * Toggle user active status
   */
  toggleUserStatus(userId: number, isActive: boolean): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/users/${userId}/status`, { is_active: isActive });
  }

  /**
   * Toggle user admin privileges
   */
  toggleAdminStatus(userId: number, isAdmin: boolean): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/users/${userId}/admin`, { is_admin: isAdmin });
  }

  /**
   * Approve or reject testimonial
   */
  approveTestimonial(testimonialId: number, approved: boolean): Observable<any> {
    return this.http.put<any>(`${environment.apiUrl}/testimonials/admin/${testimonialId}/approve`, { approved });
  }
}

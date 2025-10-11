import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  private apiUrl = `${environment.apiUrl}/admin`;
  private dashboardStatsCache$: Observable<any> | null = null;
  private usersCache$: Observable<any[]> | null = null;
  private pendingTestimonialsCache$: Observable<any[]> | null = null;

  constructor(private http: HttpClient) { }

  /**
   * Get dashboard statistics (cached with shareReplay to prevent duplicate requests)
   */
  getDashboardStats(): Observable<any> {
    if (!this.dashboardStatsCache$) {
      this.dashboardStatsCache$ = this.http.get<any>(`${this.apiUrl}/dashboard`).pipe(
        shareReplay(1)
      );
    }
    return this.dashboardStatsCache$;
  }

  /**
   * Clear the dashboard stats cache (call this after mutations)
   */
  clearDashboardCache(): void {
    this.dashboardStatsCache$ = null;
  }

  /**
   * Get all users in the system (cached with shareReplay)
   */
  getAllUsers(): Observable<any[]> {
    if (!this.usersCache$) {
      this.usersCache$ = this.http.get<any[]>(`${this.apiUrl}/users`).pipe(
        shareReplay(1)
      );
    }
    return this.usersCache$;
  }

  /**
   * Clear the users cache
   */
  clearUsersCache(): void {
    this.usersCache$ = null;
  }

  /**
   * Get pending testimonials awaiting approval (cached with shareReplay)
   */
  getPendingTestimonials(): Observable<any[]> {
    if (!this.pendingTestimonialsCache$) {
      this.pendingTestimonialsCache$ = this.http.get<any[]>(`${this.apiUrl}/testimonials/pending`).pipe(
        shareReplay(1)
      );
    }
    return this.pendingTestimonialsCache$;
  }

  /**
   * Clear the pending testimonials cache
   */
  clearPendingTestimonialsCache(): void {
    this.pendingTestimonialsCache$ = null;
  }

  /**
   * Toggle user active status
   */
  toggleUserStatus(userId: number, isActive: boolean): Observable<any> {
    // Clear all relevant caches after mutation
    this.clearDashboardCache();
    this.clearUsersCache();
    return this.http.put<any>(`${this.apiUrl}/users/${userId}/status`, { is_active: isActive });
  }

  /**
   * Toggle user admin privileges
   */
  toggleAdminStatus(userId: number, isAdmin: boolean): Observable<any> {
    // Clear all relevant caches after mutation
    this.clearDashboardCache();
    this.clearUsersCache();
    return this.http.put<any>(`${this.apiUrl}/users/${userId}/admin`, { is_admin: isAdmin });
  }

  /**
   * Approve or reject testimonial
   */
  approveTestimonial(testimonialId: number, approved: boolean): Observable<any> {
    // Clear all relevant caches after mutation
    this.clearDashboardCache();
    this.clearPendingTestimonialsCache();
    return this.http.put<any>(`${environment.apiUrl}/testimonials/admin/${testimonialId}/approve`, { approved });
  }
}

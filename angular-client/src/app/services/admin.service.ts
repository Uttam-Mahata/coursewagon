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
    this.clearDashboardCache(); // Clear cache to get fresh data after mutation
    return this.http.put<any>(`${this.apiUrl}/users/${userId}/status`, { is_active: isActive });
  }

  /**
   * Toggle user admin privileges
   */
  toggleAdminStatus(userId: number, isAdmin: boolean): Observable<any> {
    this.clearDashboardCache(); // Clear cache to get fresh data after mutation
    return this.http.put<any>(`${this.apiUrl}/users/${userId}/admin`, { is_admin: isAdmin });
  }

  /**
   * Approve or reject testimonial
   */
  approveTestimonial(testimonialId: number, approved: boolean): Observable<any> {
    this.clearDashboardCache(); // Clear cache to get fresh data after mutation
    return this.http.put<any>(`${environment.apiUrl}/testimonials/admin/${testimonialId}/approve`, { approved });
  }
}

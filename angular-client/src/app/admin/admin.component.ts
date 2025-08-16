import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { AdminService } from '../services/admin.service';
import { AuthService } from '../services/auth/auth.service';
import { faChartLine, faUsers, faStar } from '@fortawesome/free-solid-svg-icons';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';

@Component({
  selector: 'app-admin',
  standalone: false,
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  // Fix: Add the ! to indicate this property will be initialized after view init
  @ViewChild(AdminDashboardComponent)
    dashboardComponent!: AdminDashboardComponent;
  
  // FontAwesome icons
  faChartLine = faChartLine;
  faUsers = faUsers;
  faStar = faStar;

  dashboardStats: any = {};
  users: any[] = [];
  pendingTestimonials: any[] = [];
  loading = {
    dashboard: false,
    users: false,
    testimonials: false
  };
  error = {
    dashboard: '',
    users: '',
    testimonials: ''
  };
  
  activeTab = 'dashboard';

  constructor(
    private adminService: AdminService, 
    private router: Router,
    private authService: AuthService
  ) { }

  ngOnInit(): void {
    // Check if user is admin
    const user = this.authService.getCurrentUser();
    if (!user || !user.is_admin) {
      this.router.navigate(['/home']);
      return;
    }
    
    this.loadDashboardStats();
  }
  
  ngAfterViewInit() {
    if (this.dashboardComponent) {
      // Set up event handlers for the dashboard component
      this.dashboardComponent.viewAllUsers = () => this.setActiveTab('users');
      this.dashboardComponent.reviewTestimonials = () => this.setActiveTab('testimonials');
      this.dashboardComponent.retryLoading = () => this.loadDashboardStats();
    }
  }
  
  setActiveTab(tab: string): void {
    this.activeTab = tab;
    
    if (tab === 'users' && this.users.length === 0) {
      this.loadAllUsers();
    } else if (tab === 'testimonials' && this.pendingTestimonials.length === 0) {
      this.loadPendingTestimonials();
    }
  }

  loadDashboardStats(): void {
    this.loading.dashboard = true;
    this.adminService.getDashboardStats()
      .subscribe({
        next: (data: any) => {
          this.dashboardStats = data;
          this.loading.dashboard = false;
        },
        error: (err) => {
          this.error.dashboard = 'Failed to load dashboard data';
          this.loading.dashboard = false;
          console.error(err);
        }
      });
  }

  loadAllUsers(): void {
    this.loading.users = true;
    this.adminService.getAllUsers()
      .subscribe({
        next: (data: any) => {
          this.users = data;
          this.loading.users = false;
        },
        error: (err) => {
          this.error.users = 'Failed to load users';
          this.loading.users = false;
          console.error(err);
        }
      });
  }

  loadPendingTestimonials(): void {
    this.loading.testimonials = true;
    this.adminService.getPendingTestimonials()
      .subscribe({
        next: (data: any) => {
          this.pendingTestimonials = data;
          this.loading.testimonials = false;
        },
        error: (err) => {
          this.error.testimonials = 'Failed to load pending testimonials';
          this.loading.testimonials = false;
          console.error(err);
        }
      });
  }

  toggleUserStatus(event: {userId: number, isActive: boolean}): void {
    this.adminService.toggleUserStatus(event.userId, event.isActive)
      .subscribe({
        next: (updatedUser) => {
          // Update user in list
          const userIndex = this.users.findIndex(u => u.id === event.userId);
          if (userIndex !== -1) {
            this.users[userIndex].is_active = event.isActive;
          }
          
          // If this affects the dashboard stats, update them as well
          if (event.isActive) {
            if (this.dashboardStats.active_users !== undefined) {
              this.dashboardStats.active_users++;
            }
          } else {
            if (this.dashboardStats.active_users !== undefined && this.dashboardStats.active_users > 0) {
              this.dashboardStats.active_users--;
            }
          }
        },
        error: (err) => {
          console.error('Error updating user status', err);
        }
      });
  }

  toggleAdminStatus(event: {userId: number, isAdmin: boolean}): void {
    // Prevent revoking your own admin status
    const currentUser = this.authService.getCurrentUser();
    if (currentUser.id === event.userId && !event.isAdmin) {
      alert("You cannot remove your own admin privileges!");
      return;
    }

    this.adminService.toggleAdminStatus(event.userId, event.isAdmin)
      .subscribe({
        next: (updatedUser) => {
          // Update user in list
          const userIndex = this.users.findIndex(u => u.id === event.userId);
          if (userIndex !== -1) {
            this.users[userIndex].is_admin = event.isAdmin;
          }
        },
        error: (err) => {
          console.error('Error updating admin status', err);
        }
      });
  }

  approveTestimonial(testimonialId: number): void {
    this.adminService.approveTestimonial(testimonialId, true)
      .subscribe({
        next: () => {
          // Remove from pending list
          this.pendingTestimonials = this.pendingTestimonials.filter(t => t.id !== testimonialId);
          // Update dashboard stats
          if (this.dashboardStats.pending_testimonials > 0) {
            this.dashboardStats.pending_testimonials--;
          }
        },
        error: (err) => {
          console.error('Error approving testimonial', err);
        }
      });
  }

  rejectTestimonial(testimonialId: number): void {
    this.adminService.approveTestimonial(testimonialId, false)
      .subscribe({
        next: () => {
          // Remove from pending list 
          this.pendingTestimonials = this.pendingTestimonials.filter(t => t.id !== testimonialId);
          // Update dashboard stats
          if (this.dashboardStats.pending_testimonials > 0) {
            this.dashboardStats.pending_testimonials--;
          }
        },
        error: (err) => {
          console.error('Error rejecting testimonial', err);
        }
      });
  }
}

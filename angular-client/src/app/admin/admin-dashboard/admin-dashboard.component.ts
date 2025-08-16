import { Component, Input, OnInit } from '@angular/core';
import { faUsers, faGraduationCap, faStar } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-admin-dashboard',
  standalone: false,
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent {
  @Input() dashboardStats: any = {};
  @Input() loading: boolean = false;
  @Input() error: string = '';

  // FontAwesome icons
  faUsers = faUsers;
  faGraduationCap = faGraduationCap;
  faStar = faStar;

  constructor() { }

  // Method to notify parent component to switch to users tab
  viewAllUsers() {
    // This will be overridden by parent component
  }

  // Method to notify parent component to switch to testimonials tab
  reviewTestimonials() {
    // This will be overridden by parent component
  }

  // Method to reload dashboard data when there's an error
  retryLoading() {
    // This will be overridden by parent component
  }
}

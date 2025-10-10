import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faBook, faBookOpen, faGraduationCap, faChartLine,
  faSpinner, faPlay, faSearch, faTrophy, faClock
} from '@fortawesome/free-solid-svg-icons';
import { EnrollmentService, Enrollment } from '../services/enrollment.service';
import { LearningService } from '../services/learning.service';

interface EnrollmentWithProgress extends Enrollment {
  progressPercentage?: number;
  totalTimeSpent?: number;
  lastAccessedTopic?: string;
}

@Component({
  selector: 'app-learner-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule],
  templateUrl: './learner-dashboard.component.html',
  styleUrl: './learner-dashboard.component.css'
})
export class LearnerDashboardComponent implements OnInit {
  // Icons
  faBook = faBook;
  faBookOpen = faBookOpen;
  faGraduationCap = faGraduationCap;
  faChartLine = faChartLine;
  faSpinner = faSpinner;
  faPlay = faPlay;
  faSearch = faSearch;
  faTrophy = faTrophy;
  faClock = faClock;

  enrollments: EnrollmentWithProgress[] = [];
  activeEnrollments: EnrollmentWithProgress[] = [];
  completedEnrollments: EnrollmentWithProgress[] = [];
  loading = false;
  error = '';

  // Stats
  totalEnrollments = 0;
  completedCourses = 0;
  inProgressCourses = 0;
  totalTimeSpent = 0;

  constructor(
    private enrollmentService: EnrollmentService,
    private learningService: LearningService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadEnrollments();
  }

  loadEnrollments(): void {
    this.loading = true;
    this.error = '';

    this.enrollmentService.getMyEnrollments().subscribe({
      next: (enrollments) => {
        this.enrollments = enrollments;
        this.totalEnrollments = enrollments.length;

        // Separate active and completed
        this.activeEnrollments = enrollments.filter(e => e.status === 'active');
        this.completedEnrollments = enrollments.filter(e => e.status === 'completed');

        this.inProgressCourses = this.activeEnrollments.length;
        this.completedCourses = this.completedEnrollments.length;

        // Load progress for each enrollment
        this.loadProgressForEnrollments();

        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load enrollments';
        this.loading = false;
        console.error('Error loading enrollments:', err);
      }
    });
  }

  loadProgressForEnrollments(): void {
    this.enrollments.forEach(enrollment => {
      this.learningService.getCourseProgress(enrollment.id).subscribe({
        next: (progress) => {
          enrollment.progressPercentage = progress.progress_percentage;
          enrollment.totalTimeSpent = progress.total_time_spent_seconds;
          this.totalTimeSpent += progress.total_time_spent_seconds || 0;

          // Update enrollment's progress_percentage for display
          enrollment.progress_percentage = progress.progress_percentage;
        },
        error: (err) => {
          console.error(`Error loading progress for enrollment ${enrollment.id}:`, err);
          // Set default values on error
          enrollment.progressPercentage = 0;
          enrollment.totalTimeSpent = 0;
          enrollment.progress_percentage = 0;
        }
      });
    });
  }

  browseCourses(): void {
    this.router.navigate(['/courses/browse']);
  }

  continueLearning(enrollment: Enrollment): void {
    this.router.navigate(['/learn', enrollment.course_id]);
  }

  viewCoursePreview(courseId: number): void {
    this.router.navigate(['/courses/preview', courseId]);
  }

  getProgressColor(percentage: number): string {
    if (percentage >= 75) return 'bg-green-600';
    if (percentage >= 50) return 'bg-blue-600';
    if (percentage >= 25) return 'bg-yellow-600';
    return 'bg-gray-400';
  }

  getProgressLabel(percentage: number): string {
    if (percentage === 100) return 'Completed';
    if (percentage >= 75) return 'Almost done';
    if (percentage >= 50) return 'Halfway there';
    if (percentage >= 25) return 'Getting started';
    return 'Just started';
  }

  formatTimeSpent(seconds: number): string {
    if (!seconds) return '0h';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  formatDate(dateString: string): string {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faBook, faBookOpen, faListUl, faClock, faSignal,
  faUsers, faArrowLeft, faPlay, faSpinner, faCheckCircle, faStar, faPen
} from '@fortawesome/free-solid-svg-icons';
import { LearningService, CoursePreview } from '../services/learning.service';
import { EnrollmentService, EnrollmentCheck } from '../services/enrollment.service';
import { AuthService } from '../services/auth/auth.service';
import { ReviewService, ReviewStats, CourseReview } from '../services/review.service';
import { CacheService } from '../services/cache.service';
import { StarRatingComponent } from '../shared/star-rating/star-rating.component';
import { CourseReviewComponent } from '../course-review/course-review.component';
import { CourseReviewsListComponent } from '../course-reviews-list/course-reviews-list.component';

@Component({
  selector: 'app-course-preview',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FontAwesomeModule,
    StarRatingComponent,
    CourseReviewComponent,
    CourseReviewsListComponent
  ],
  templateUrl: './course-preview.component.html',
  styleUrl: './course-preview.component.css'
})
export class CoursePreviewComponent implements OnInit {
  // Icons
  faBook = faBook;
  faBookOpen = faBookOpen;
  faListUl = faListUl;
  faClock = faClock;
  faSignal = faSignal;
  faUsers = faUsers;
  faArrowLeft = faArrowLeft;
  faPlay = faPlay;
  faSpinner = faSpinner;
  faCheckCircle = faCheckCircle;
  faStar = faStar;
  faPen = faPen;

  courseId!: number;
  coursePreview: CoursePreview | null = null;
  enrollmentCheck: EnrollmentCheck | null = null;
  loading = false;
  enrolling = false;
  error = '';
  enrollmentError = '';

  isAuthenticated = false;
  isLearner = false;

  // Review-related state
  reviewStats: ReviewStats | null = null;
  userReview: CourseReview | null = null;
  showReviewForm = false;
  loadingReviewStats = false;
  loadingUserReview = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private learningService: LearningService,
    private enrollmentService: EnrollmentService,
    private authService: AuthService,
    private reviewService: ReviewService,
    private cacheService: CacheService
  ) {}

  ngOnInit(): void {
    // Check authentication
    const user = this.authService.getCurrentUser();
    this.isAuthenticated = !!user;
    this.isLearner = this.authService.isLearner();

    // Get course ID from route
    this.route.paramMap.subscribe(params => {
      const id = params.get('id') || params.get('course_id');
      if (id) {
        this.courseId = parseInt(id);
        this.loadCoursePreview();
        this.loadReviewStats();
        if (this.isAuthenticated) {
          this.checkEnrollmentStatus();
          this.loadUserReview();
        }
      }
    });
  }

  loadCoursePreview(): void {
    this.loading = true;
    this.error = '';

    this.learningService.getCoursePreview(this.courseId).subscribe({
      next: (preview) => {
        this.coursePreview = preview;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load course preview';
        this.loading = false;
        console.error('Error loading course preview:', err);
      }
    });
  }

  checkEnrollmentStatus(): void {
    this.enrollmentService.checkEnrollment(this.courseId).subscribe({
      next: (check) => {
        this.enrollmentCheck = check;
      },
      error: (err) => {
        console.error('Error checking enrollment:', err);
      }
    });
  }

  enrollInCourse(): void {
    if (!this.isAuthenticated) {
      this.router.navigate(['/auth'], { queryParams: { returnUrl: `/courses/preview/${this.courseId}` } });
      return;
    }

    if (!this.isLearner) {
      this.enrollmentError = 'Only learners can enroll in courses';
      return;
    }

    this.enrolling = true;
    this.enrollmentError = '';

    this.enrollmentService.enrollInCourse(this.courseId).subscribe({
      next: (response) => {
        if (response.success) {
          // Update enrollment status immediately
          this.enrollmentCheck = {
            enrolled: true,
            enrollment: response.enrollment || null
          };

          // Clear enrollment cache to ensure fresh data on next check
          this.cacheService.invalidateHttp('/enrollment');

          this.enrolling = false;
          // Navigate to learning view
          this.startLearning();
        } else {
          this.enrolling = false;
        }
      },
      error: (err) => {
        this.enrolling = false;
        this.enrollmentError = err.error?.message || 'Enrollment failed. Please try again.';
        console.error('Error enrolling in course:', err);
      }
    });
  }

  startLearning(): void {
    this.router.navigate(['/learn', this.courseId]);
  }

  goBack(): void {
    this.router.navigate(['/courses/browse']);
  }

  getDifficultyColor(level: string): string {
    switch (level?.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  formatDuration(hours: number): string {
    if (!hours) return 'Not specified';
    if (hours < 1) return `${Math.round(hours * 60)} minutes`;
    return `${hours} hour${hours > 1 ? 's' : ''}`;
  }

  get totalTopics(): number {
    if (!this.coursePreview?.structure) return 0;
    return this.coursePreview.structure.reduce((total, subject) => {
      return total + (subject.topics?.length || 0);
    }, 0);
  }

  get isEnrolled(): boolean {
    return this.enrollmentCheck?.enrolled || false;
  }

  // Review methods
  loadReviewStats(): void {
    this.loadingReviewStats = true;
    this.reviewService.getReviewStats(this.courseId).subscribe({
      next: (stats) => {
        this.reviewStats = stats;
        this.loadingReviewStats = false;
      },
      error: (err) => {
        console.error('Error loading review stats:', err);
        this.loadingReviewStats = false;
      }
    });
  }

  loadUserReview(): void {
    this.loadingUserReview = true;
    this.reviewService.getMyReview(this.courseId).subscribe({
      next: (review) => {
        this.userReview = review;
        this.loadingUserReview = false;
      },
      error: (err) => {
        // 404 is expected if user hasn't reviewed yet
        if (err.status !== 404) {
          console.error('Error loading user review:', err);
        }
        this.loadingUserReview = false;
      }
    });
  }

  openReviewForm(): void {
    if (!this.isAuthenticated) {
      this.router.navigate(['/auth'], { queryParams: { returnUrl: `/courses/preview/${this.courseId}` } });
      return;
    }
    this.showReviewForm = true;
  }

  onReviewSubmitted(review: CourseReview): void {
    this.userReview = review;
    this.showReviewForm = false;
    // Reload stats to reflect new review
    this.loadReviewStats();
    // Reload course preview to get updated ratings
    this.loadCoursePreview();
  }

  onReviewDeleted(): void {
    this.userReview = null;
    this.showReviewForm = false;
    // Reload stats
    this.loadReviewStats();
    // Reload course preview
    this.loadCoursePreview();
  }

  onReviewFormCancelled(): void {
    this.showReviewForm = false;
  }
}

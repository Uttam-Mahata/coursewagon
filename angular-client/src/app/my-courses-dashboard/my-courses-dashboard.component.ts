import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faBook, faBookOpen, faBookmark, faListUl, faFileAlt,
  faChartLine, faPlus, faEye, faSpinner, faGlobe, faLock, faTimes
} from '@fortawesome/free-solid-svg-icons';
import { CourseStatsService, UserCourseStats, CourseDetail } from '../services/course-stats.service';
import { LearningService } from '../services/learning.service';
import { ToastService } from '../services/toast.service';
import { CacheService } from '../services/cache.service';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-my-courses-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule, FormsModule],
  templateUrl: './my-courses-dashboard.component.html',
  styleUrl: './my-courses-dashboard.component.css'
})
export class MyCoursesDashboardComponent implements OnInit {
  // Icons
  faBook = faBook;
  faBookOpen = faBookOpen;
  faBookmark = faBookmark;
  faListUl = faListUl;
  faFileAlt = faFileAlt;
  faChartLine = faChartLine;
  faPlus = faPlus;
  faEye = faEye;
  faSpinner = faSpinner;
  faGlobe = faGlobe;
  faLock = faLock;
  faTimes = faTimes;

  stats: UserCourseStats | null = null;
  loading = false;
  error = '';
  publishingCourses = new Set<number>();

  // Publish modal
  showPublishModal = false;
  selectedCourseForPublish: CourseDetail | null = null;
  publishForm = {
    category: '',
    difficulty_level: '',
    estimated_duration_hours: 0
  };

  // Categories and difficulty levels
  categories = ['Programming', 'Data Science', 'Web Development', 'Mobile Development', 'Design', 'Business', 'Mathematics', 'Science', 'Languages', 'Other'];
  difficultyLevels = ['Beginner', 'Intermediate', 'Advanced'];

  constructor(
    private courseStatsService: CourseStatsService,
    private learningService: LearningService,
    private router: Router,
    private toastService: ToastService,
    private cacheService: CacheService
  ) {}

  ngOnInit(): void {
    this.loadStatistics();
  }

  loadStatistics(skipCache = false): void {
    this.loading = true;
    this.error = '';

    // Use fresh data if cache should be skipped (e.g., after publish/unpublish)
    const statsObservable = skipCache
      ? this.courseStatsService.getMyCourseStatisticsFresh()
      : this.courseStatsService.getMyCourseStatistics();

    statsObservable.subscribe({
      next: (data) => {
        this.stats = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load course statistics';
        this.loading = false;
        console.error('Error loading course statistics:', err);
      }
    });
  }

  createNewCourse(): void {
    this.router.navigate(['/create-course']);
  }

  viewCourse(courseId: number): void {
    this.router.navigate(['/courses', courseId, 'subjects']);
  }

  getProgressPercentage(course: CourseDetail): number {
    // Calculate progress based on content depth
    // A course is "complete" if it has subjects, chapters, topics, and content
    let progress = 0;
    if (course.subjects_count > 0) progress += 25;
    if (course.chapters_count > 0) progress += 25;
    if (course.topics_count > 0) progress += 25;
    if (course.content_count > 0) progress += 25;
    return progress;
  }

  getProgressColor(percentage: number): string {
    if (percentage >= 75) return 'bg-green-600';
    if (percentage >= 50) return 'bg-blue-600';
    if (percentage >= 25) return 'bg-yellow-600';
    return 'bg-gray-400';
  }

  openPublishModal(course: CourseDetail): void {
    this.selectedCourseForPublish = course;
    // Set default values if already published
    this.publishForm = {
      category: course.category || '',
      difficulty_level: course.difficulty_level || '',
      estimated_duration_hours: course.estimated_duration_hours || 0
    };
    this.showPublishModal = true;
  }

  closePublishModal(): void {
    this.showPublishModal = false;
    this.selectedCourseForPublish = null;
    this.publishForm = {
      category: '',
      difficulty_level: '',
      estimated_duration_hours: 0
    };
  }

  publishCourse(): void {
    if (!this.selectedCourseForPublish) return;

    // Validate form
    if (!this.publishForm.category || !this.publishForm.difficulty_level || !this.publishForm.estimated_duration_hours) {
      this.toastService.error('Please fill in all required fields');
      return;
    }

    if (this.publishForm.estimated_duration_hours <= 0) {
      this.toastService.error('Estimated duration must be greater than 0');
      return;
    }

    const courseId = this.selectedCourseForPublish.course_id;
    if (this.publishingCourses.has(courseId)) return;

    this.publishingCourses.add(courseId);

    this.learningService.publishCourse(courseId, this.publishForm).subscribe({
      next: () => {
        this.publishingCourses.delete(courseId);
        this.toastService.success('Course published successfully!');
        this.closePublishModal();

        // Clear the statistics cache to ensure fresh data
        const statsUrl = `${environment.apiUrl}/courses/my-courses/statistics`;
        this.cacheService.delete(`http:${statsUrl}`);

        // Reload statistics with cache bypass to get fresh data
        this.loadStatistics(true);
      },
      error: (err) => {
        this.publishingCourses.delete(courseId);
        console.error('Error publishing course:', err);
        const errorMessage = err?.error?.detail || 'Failed to publish course';
        this.toastService.error(errorMessage);
      }
    });
  }

  unpublishCourse(courseId: number): void {
    if (this.publishingCourses.has(courseId)) return;

    this.publishingCourses.add(courseId);

    this.learningService.unpublishCourse(courseId).subscribe({
      next: () => {
        this.publishingCourses.delete(courseId);
        this.toastService.success('Course unpublished successfully!');

        // Clear the statistics cache to ensure fresh data
        const statsUrl = `${environment.apiUrl}/courses/my-courses/statistics`;
        this.cacheService.delete(`http:${statsUrl}`);

        // Reload statistics with cache bypass to get fresh data
        this.loadStatistics(true);
      },
      error: (err) => {
        this.publishingCourses.delete(courseId);
        console.error('Error unpublishing course:', err);
        const errorMessage = err?.error?.detail || 'Failed to unpublish course';
        this.toastService.error(errorMessage);
      }
    });
  }

  isPublishing(courseId: number): boolean {
    return this.publishingCourses.has(courseId);
  }
}

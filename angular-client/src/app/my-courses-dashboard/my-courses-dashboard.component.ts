import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faBook, faBookOpen, faBookmark, faListUl, faFileAlt,
  faChartLine, faPlus, faEye, faSpinner, faGlobe, faLock
} from '@fortawesome/free-solid-svg-icons';
import { CourseStatsService, UserCourseStats, CourseDetail } from '../services/course-stats.service';
import { LearningService } from '../services/learning.service';
import { ToastService } from '../services/toast.service';

@Component({
  selector: 'app-my-courses-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule],
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

  stats: UserCourseStats | null = null;
  loading = false;
  error = '';
  publishingCourses = new Set<number>();

  constructor(
    private courseStatsService: CourseStatsService,
    private learningService: LearningService,
    private router: Router,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.loadStatistics();
  }

  loadStatistics(): void {
    this.loading = true;
    this.error = '';

    this.courseStatsService.getMyCourseStatistics().subscribe({
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

  publishCourse(courseId: number): void {
    if (this.publishingCourses.has(courseId)) return;

    // For now, use default values - in a real app, you'd show a modal to collect these
    const publishData = {
      category: 'General',
      difficulty_level: 'Intermediate',
      estimated_duration_hours: 10
    };

    this.publishingCourses.add(courseId);

    this.learningService.publishCourse(courseId, publishData).subscribe({
      next: () => {
        this.publishingCourses.delete(courseId);
        this.toastService.success('Course published successfully!');
        // Reload statistics to reflect published status
        this.loadStatistics();
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
        // Reload statistics to reflect unpublished status
        this.loadStatistics();
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

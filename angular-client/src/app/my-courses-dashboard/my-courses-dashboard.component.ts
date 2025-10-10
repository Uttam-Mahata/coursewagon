import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faBook, faBookOpen, faBookmark, faListUl, faFileAlt,
  faChartLine, faPlus, faEye, faSpinner
} from '@fortawesome/free-solid-svg-icons';
import { CourseStatsService, UserCourseStats, CourseDetail } from '../services/course-stats.service';

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

  stats: UserCourseStats | null = null;
  loading = false;
  error = '';

  constructor(
    private courseStatsService: CourseStatsService,
    private router: Router
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
}

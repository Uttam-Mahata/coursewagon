import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faSearch, faBook, faFilter, faStar, faUsers,
  faSpinner, faClock, faSignal
} from '@fortawesome/free-solid-svg-icons';
import { LearningService } from '../services/learning.service';
import { EnrollmentService } from '../services/enrollment.service';

interface CourseWithEnrollment {
  id: number;
  name: string;
  description: string;
  image_url?: string;
  category?: string;
  difficulty_level?: string;
  estimated_duration_hours?: number;
  enrollment_count: number;
  creator_name?: string;
  is_enrolled?: boolean;
  created_at?: string;
  published_at?: string;
}

@Component({
  selector: 'app-course-catalog',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, FontAwesomeModule],
  templateUrl: './course-catalog.component.html',
  styleUrl: './course-catalog.component.css'
})
export class CourseCatalogComponent implements OnInit {
  // Icons
  faSearch = faSearch;
  faBook = faBook;
  faFilter = faFilter;
  faStar = faStar;
  faUsers = faUsers;
  faSpinner = faSpinner;
  faClock = faClock;
  faSignal = faSignal;

  courses: CourseWithEnrollment[] = [];
  filteredCourses: CourseWithEnrollment[] = [];
  loading = false;
  error = '';

  // Search and filters
  searchQuery = '';
  selectedCategory = '';
  selectedDifficulty = '';
  selectedSort = 'popular';
  showFilters = false;

  // Categories and difficulty levels
  categories = ['Programming', 'Data Science', 'Web Development', 'Mobile Development', 'Design', 'Business', 'Mathematics', 'Science', 'Languages', 'Other'];
  difficultyLevels = ['Beginner', 'Intermediate', 'Advanced'];
  sortOptions = [
    { value: 'popular', label: 'Most Popular' },
    { value: 'newest', label: 'Newest First' },
    { value: 'duration_asc', label: 'Shortest Duration' },
    { value: 'duration_desc', label: 'Longest Duration' }
  ];

  // Pagination
  currentPage = 1;
  pageSize = 12;
  totalCourses = 0;

  constructor(
    private learningService: LearningService,
    private enrollmentService: EnrollmentService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadCourses();
  }

  loadCourses(): void {
    this.loading = true;
    this.error = '';

    const offset = (this.currentPage - 1) * this.pageSize;

    this.learningService.getPublishedCourses(this.pageSize, offset).subscribe({
      next: (courses) => {
        this.courses = courses;
        this.totalCourses = courses.length;
        this.checkEnrollmentStatus();
        this.applyFilters();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load courses';
        this.loading = false;
        console.error('Error loading courses:', err);
      }
    });
  }

  checkEnrollmentStatus(): void {
    // Check enrollment status for each course
    this.courses.forEach(course => {
      this.enrollmentService.checkEnrollment(course.id).subscribe({
        next: (check) => {
          course.is_enrolled = check.enrolled;
        },
        error: (err) => {
          console.error(`Error checking enrollment for course ${course.id}:`, err);
        }
      });
    });
  }

  searchCourses(): void {
    if (!this.searchQuery.trim()) {
      this.loadCourses();
      return;
    }

    this.loading = true;
    this.error = '';

    this.learningService.searchCourses(this.searchQuery, this.pageSize).subscribe({
      next: (courses) => {
        this.courses = courses;
        this.totalCourses = courses.length;
        this.checkEnrollmentStatus();
        this.applyFilters();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Search failed';
        this.loading = false;
        console.error('Error searching courses:', err);
      }
    });
  }

  applyFilters(): void {
    // Filter courses
    this.filteredCourses = this.courses.filter(course => {
      const categoryMatch = !this.selectedCategory || course.category === this.selectedCategory;
      const difficultyMatch = !this.selectedDifficulty || course.difficulty_level === this.selectedDifficulty;
      return categoryMatch && difficultyMatch;
    });

    // Apply sorting
    this.sortCourses();
  }

  sortCourses(): void {
    switch (this.selectedSort) {
      case 'popular':
        this.filteredCourses.sort((a, b) => (b.enrollment_count || 0) - (a.enrollment_count || 0));
        break;
      case 'newest':
        this.filteredCourses.sort((a, b) => {
          const dateA = new Date(a.created_at || 0).getTime();
          const dateB = new Date(b.created_at || 0).getTime();
          return dateB - dateA;
        });
        break;
      case 'duration_asc':
        this.filteredCourses.sort((a, b) => (a.estimated_duration_hours || 0) - (b.estimated_duration_hours || 0));
        break;
      case 'duration_desc':
        this.filteredCourses.sort((a, b) => (b.estimated_duration_hours || 0) - (a.estimated_duration_hours || 0));
        break;
    }
  }

  onCategoryChange(): void {
    this.applyFilters();
  }

  onDifficultyChange(): void {
    this.applyFilters();
  }

  onSortChange(): void {
    this.applyFilters();
  }

  toggleFilters(): void {
    this.showFilters = !this.showFilters;
  }

  clearFilters(): void {
    this.selectedCategory = '';
    this.selectedDifficulty = '';
    this.selectedSort = 'popular';
    this.searchQuery = '';
    this.applyFilters();
  }

  viewCoursePreview(courseId: number): void {
    this.router.navigate(['/courses/preview', courseId]);
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

  loadMore(): void {
    this.currentPage++;
    this.loadCourses();
  }

  get hasMore(): boolean {
    return this.totalCourses === this.pageSize;
  }

  get displayedCourses(): CourseWithEnrollment[] {
    return this.filteredCourses.length > 0 ? this.filteredCourses : this.courses;
  }
}

import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faSpinner, faChevronLeft, faChevronRight } from '@fortawesome/free-solid-svg-icons';
import { StarRatingComponent } from '../shared/star-rating/star-rating.component';
import { ReviewService, CourseReview, ReviewsListResponse } from '../services/review.service';

@Component({
  selector: 'app-course-reviews-list',
  standalone: true,
  imports: [CommonModule, FontAwesomeModule, StarRatingComponent],
  templateUrl: './course-reviews-list.component.html',
  styleUrl: './course-reviews-list.component.css'
})
export class CourseReviewsListComponent implements OnInit {
  // Icons
  faSpinner = faSpinner;
  faChevronLeft = faChevronLeft;
  faChevronRight = faChevronRight;

  // Inputs
  @Input() courseId!: number;
  @Input() limit: number = 10;

  // Component state
  reviews: CourseReview[] = [];
  loading = false;
  error = '';
  currentPage = 1;
  totalPages = 1;
  totalCount = 0;

  constructor(private reviewService: ReviewService) {}

  ngOnInit(): void {
    this.loadReviews();
  }

  loadReviews(): void {
    this.loading = true;
    this.error = '';

    this.reviewService.getCourseReviews(this.courseId, this.currentPage, this.limit).subscribe({
      next: (response: ReviewsListResponse) => {
        this.reviews = response.reviews;
        this.totalCount = response.total_count;
        this.totalPages = response.total_pages;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load reviews';
        this.loading = false;
        console.error('Error loading reviews:', err);
      }
    });
  }

  onPageChange(page: number): void {
    if (page < 1 || page > this.totalPages || page === this.currentPage) {
      return;
    }
    this.currentPage = page;
    this.loadReviews();
    // Scroll to top of reviews
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  get pageNumbers(): number[] {
    const pages: number[] = [];
    const maxPagesToShow = 5;
    let startPage = Math.max(1, this.currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(this.totalPages, startPage + maxPagesToShow - 1);

    // Adjust start page if end page is at the limit
    if (endPage - startPage < maxPagesToShow - 1) {
      startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) {
      return 'Today';
    } else if (diffInDays === 1) {
      return 'Yesterday';
    } else if (diffInDays < 7) {
      return `${diffInDays} days ago`;
    } else if (diffInDays < 30) {
      const weeks = Math.floor(diffInDays / 7);
      return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    } else if (diffInDays < 365) {
      const months = Math.floor(diffInDays / 30);
      return `${months} month${months > 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  truncateText(text: string, maxLength: number = 300): { text: string; isTruncated: boolean } {
    if (!text || text.length <= maxLength) {
      return { text: text || '', isTruncated: false };
    }
    return {
      text: text.substring(0, maxLength) + '...',
      isTruncated: true
    };
  }
}

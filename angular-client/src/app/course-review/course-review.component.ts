import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faTimes, faCheck, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { StarRatingComponent } from '../shared/star-rating/star-rating.component';
import { ReviewService, CourseReview, CanReviewResponse } from '../services/review.service';

@Component({
  selector: 'app-course-review',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FontAwesomeModule, StarRatingComponent],
  templateUrl: './course-review.component.html',
  styleUrl: './course-review.component.css'
})
export class CourseReviewComponent implements OnInit {
  // Icons
  faTimes = faTimes;
  faCheck = faCheck;
  faSpinner = faSpinner;

  // Inputs
  @Input() courseId!: number;
  @Input() existingReview?: CourseReview;

  // Outputs
  @Output() reviewSubmitted = new EventEmitter<CourseReview>();
  @Output() reviewDeleted = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  // Component state
  reviewForm: FormGroup;
  loading = false;
  checking = true;
  error = '';
  success = '';
  eligibility: CanReviewResponse | null = null;
  selectedRating = 5;
  maxCharacters = 500;

  constructor(
    private fb: FormBuilder,
    private reviewService: ReviewService
  ) {
    this.reviewForm = this.fb.group({
      rating: [5, [Validators.required, Validators.min(1), Validators.max(5)]],
      reviewText: ['', [Validators.maxLength(this.maxCharacters)]]
    });
  }

  ngOnInit(): void {
    if (this.existingReview) {
      // Edit mode - populate form with existing review
      this.reviewForm.patchValue({
        rating: this.existingReview.rating,
        reviewText: this.existingReview.review_text || ''
      });
      this.selectedRating = this.existingReview.rating;
      this.checking = false;
    } else {
      // Create mode - check eligibility
      this.checkEligibility();
    }
  }

  checkEligibility(): void {
    this.checking = true;
    this.reviewService.canReview(this.courseId).subscribe({
      next: (response) => {
        this.eligibility = response;
        this.checking = false;
      },
      error: (err) => {
        this.error = 'Failed to check review eligibility';
        this.checking = false;
        console.error('Error checking eligibility:', err);
      }
    });
  }

  onRatingChange(rating: number): void {
    this.selectedRating = rating;
    this.reviewForm.patchValue({ rating });
  }

  get characterCount(): number {
    return this.reviewForm.get('reviewText')?.value?.length || 0;
  }

  get charactersRemaining(): number {
    return this.maxCharacters - this.characterCount;
  }

  onSubmit(): void {
    if (this.reviewForm.invalid) {
      this.error = 'Please select a rating';
      return;
    }

    this.loading = true;
    this.error = '';
    this.success = '';

    const { rating, reviewText } = this.reviewForm.value;

    if (this.existingReview) {
      // Update existing review
      this.reviewService.updateReview(this.existingReview.id, rating, reviewText || undefined).subscribe({
        next: (response) => {
          this.loading = false;
          if (response.success && response.review) {
            this.success = 'Review updated successfully!';
            this.reviewSubmitted.emit(response.review);
            setTimeout(() => this.onCancel(), 1500);
          }
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 'Failed to update review';
          console.error('Error updating review:', err);
        }
      });
    } else {
      // Create new review
      this.reviewService.createReview(this.courseId, rating, reviewText || undefined).subscribe({
        next: (response) => {
          this.loading = false;
          if (response.success && response.review) {
            this.success = 'Review submitted successfully!';
            this.reviewSubmitted.emit(response.review);
            setTimeout(() => this.onCancel(), 1500);
          }
        },
        error: (err) => {
          this.loading = false;
          this.error = err.error?.detail || 'Failed to submit review';
          console.error('Error creating review:', err);
        }
      });
    }
  }

  onDelete(): void {
    if (!this.existingReview) return;

    if (!confirm('Are you sure you want to delete your review?')) {
      return;
    }

    this.loading = true;
    this.error = '';

    this.reviewService.deleteReview(this.existingReview.id).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success) {
          this.success = 'Review deleted successfully!';
          this.reviewDeleted.emit();
          setTimeout(() => this.onCancel(), 1500);
        }
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Failed to delete review';
        console.error('Error deleting review:', err);
      }
    });
  }

  onCancel(): void {
    this.cancelled.emit();
  }

  get canSubmit(): boolean {
    return !this.checking && (!this.eligibility || this.eligibility.can_review);
  }
}

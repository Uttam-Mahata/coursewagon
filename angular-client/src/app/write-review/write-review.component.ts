import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { faStar, faStarHalfAlt, faPen, faCheck, faTimes } from '@fortawesome/free-solid-svg-icons';
import { faStar as farStar } from '@fortawesome/free-regular-svg-icons';
import { TestimonialService } from '../services/testimonial.service';

@Component({
  selector: 'app-write-review',
  standalone: false,
  templateUrl: './write-review.component.html',
  styleUrl: './write-review.component.css'
})
export class WriteReviewComponent implements OnInit {
  // FontAwesome icons
  faStar = faStar;
  farStar = farStar;
  faStarHalfAlt = faStarHalfAlt;
  faPen = faPen;
  faCheck = faCheck;
  faTimes = faTimes;
  
  // Input and Output properties
  @Input() userTestimonial: any = null;
  @Output() testimonialUpdated = new EventEmitter<any>();
  @Output() testimonialDeleted = new EventEmitter<void>();
  
  // Form data
  showForm: boolean = false;
  newTestimonial = {
    quote: '',
    rating: 5
  };
  
  // Form states
  isSubmitting: boolean = false;
  formError: string | null = null;
  formSuccess: string | null = null;

  constructor(private testimonialService: TestimonialService) {}

  ngOnInit(): void {
    if (this.userTestimonial) {
      this.prepopulateForm();
    }
  }
  
  toggleForm(): void {
    this.showForm = !this.showForm;
    this.formError = null;
    this.formSuccess = null;
    
    if (this.showForm && this.userTestimonial) {
      this.prepopulateForm();
    }
  }
  
  prepopulateForm(): void {
    this.newTestimonial.quote = this.userTestimonial.quote;
    this.newTestimonial.rating = this.userTestimonial.rating;
  }

  submitTestimonial(): void {
    if (!this.newTestimonial.quote.trim()) {
      this.formError = 'Please enter your testimonial';
      return;
    }

    this.isSubmitting = true;
    this.formError = null;
    
    // Determine if creating new or updating existing
    if (this.userTestimonial) {
      this.updateTestimonial();
    } else {
      this.createTestimonial();
    }
  }

  createTestimonial(): void {
    this.testimonialService.createTestimonial(
      this.newTestimonial.quote,
      this.newTestimonial.rating
    ).subscribe({
      next: (response) => {
        this.testimonialUpdated.emit(response);
        this.formSuccess = 'Your testimonial has been submitted for approval!';
        this.isSubmitting = false;
        setTimeout(() => this.showForm = false, 3000);
      },
      error: (err) => {
        this.formError = err.error.error || 'Failed to submit testimonial';
        this.isSubmitting = false;
        console.error('Error submitting testimonial', err);
      }
    });
  }

  updateTestimonial(): void {
    this.testimonialService.updateTestimonial(
      this.userTestimonial.id,
      this.newTestimonial.quote,
      this.newTestimonial.rating
    ).subscribe({
      next: (response) => {
        this.testimonialUpdated.emit(response);
        this.formSuccess = 'Your testimonial has been updated and submitted for approval!';
        this.isSubmitting = false;
        setTimeout(() => this.showForm = false, 3000);
      },
      error: (err) => {
        this.formError = err.error.error || 'Failed to update testimonial';
        this.isSubmitting = false;
        console.error('Error updating testimonial', err);
      }
    });
  }

  deleteTestimonial(): void {
    if (!confirm('Are you sure you want to delete your testimonial?')) {
      return;
    }

    this.testimonialService.deleteTestimonial(this.userTestimonial.id).subscribe({
      next: () => {
        this.testimonialDeleted.emit();
        this.formSuccess = 'Your testimonial has been deleted';
        setTimeout(() => this.formSuccess = null, 3000);
      },
      error: (err) => {
        this.formError = 'Failed to delete testimonial';
        console.error('Error deleting testimonial', err);
      }
    });
  }
  
  editTestimonial(): void {
    this.prepopulateForm();
    this.showForm = true;
    this.formError = null;
    this.formSuccess = null;
  }

  // Helper method to generate star rating elements
  generateRatingStars(rating: number): { icon: any, half: boolean }[] {
    const stars: { icon: any, half: boolean }[] = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    // Add full stars
    for (let i = 0; i < fullStars; i++) {
      stars.push({ icon: this.faStar, half: false });
    }
    
    // Add half star if needed
    if (hasHalfStar) {
      stars.push({ icon: this.faStarHalfAlt, half: true });
    }
    
    // Add empty stars to make 5 total
    const emptyStars = 5 - stars.length;
    for (let i = 0; i < emptyStars; i++) {
      stars.push({ icon: this.farStar, half: false });
    }
    
    return stars;
  }
}

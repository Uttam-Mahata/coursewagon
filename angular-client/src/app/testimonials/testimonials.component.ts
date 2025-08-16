import { Component, OnInit } from '@angular/core';
import { faUser, faStar, faStarHalfAlt } from '@fortawesome/free-solid-svg-icons';
import { faStar as farStar } from '@fortawesome/free-regular-svg-icons';
import { TestimonialService } from '../services/testimonial.service';
import { AuthService } from '../services/auth/auth.service';
@Component({
  selector: 'app-testimonials',
  standalone: false,
  templateUrl: './testimonials.component.html',
  styleUrls: ['./testimonials.component.css']
})
export class TestimonialsComponent implements OnInit {
  // FontAwesome icons
  faUser = faUser;
  faStar = faStar;
  farStar = farStar;
  faStarHalfAlt = faStarHalfAlt;

  // Testimonial data
  testimonials: any[] = [];
  isLoading: boolean = true;
  error: string | null = null;
  
  // User-related state
  isAuthenticated: boolean = false;
  userTestimonial: any = null;

  constructor(
    private testimonialService: TestimonialService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadTestimonials();
    this.checkAuthState();
  }

  checkAuthState(): void {
    this.authService.isLoggedIn$.subscribe(isLoggedIn => {
      this.isAuthenticated = isLoggedIn;
      if (isLoggedIn) {
        this.loadUserTestimonial();
      }
    });
  }

  loadTestimonials(): void {
    this.isLoading = true;
    this.testimonialService.getApprovedTestimonials().subscribe({
      next: (data) => {
        // Filter testimonials to only show those with 4 or 5 stars
        this.testimonials = data.filter(testimonial => testimonial.rating >= 4);
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to load testimonials';
        this.isLoading = false;
        console.error('Error loading testimonials', err);
      }
    });
  }

  loadUserTestimonial(): void {
    this.testimonialService.getUserTestimonial().subscribe({
      next: (data) => {
        this.userTestimonial = data;
      },
      error: (err) => {
        // It's fine if user doesn't have a testimonial
        if (err.status !== 404) {
          console.error('Error loading user testimonial', err);
        }
      }
    });
  }

  // Handler methods for write-review component events
  onTestimonialUpdated(testimonial: any): void {
    this.userTestimonial = testimonial;
    // Reload testimonials if the updated one was already approved and might be displayed
    if (testimonial.is_approved) {
      this.loadTestimonials();
    }
  }

  onTestimonialDeleted(): void {
    this.userTestimonial = null;
    // Reload testimonials in case the deleted one was being displayed
    this.loadTestimonials();
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

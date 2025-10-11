import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faStar, faStarHalfAlt } from '@fortawesome/free-solid-svg-icons';
import { faStar as farStar } from '@fortawesome/free-regular-svg-icons';

type StarSize = 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'app-star-rating',
  standalone: true,
  imports: [CommonModule, FontAwesomeModule],
  templateUrl: './star-rating.component.html',
  styleUrl: './star-rating.component.css'
})
export class StarRatingComponent {
  // Icons
  faStar = faStar;
  faStarHalfAlt = faStarHalfAlt;
  farStar = farStar;

  // Inputs
  @Input() rating: number = 0;
  @Input() maxRating: number = 5;
  @Input() interactive: boolean = false;
  @Input() size: StarSize = 'md';
  @Input() showCount: boolean = false;
  @Input() reviewCount: number = 0;

  // Outputs
  @Output() ratingChange = new EventEmitter<number>();

  // Component state
  hoverRating: number = 0;

  /**
   * Get star display configuration
   */
  get stars(): { type: 'full' | 'half' | 'empty'; icon: any }[] {
    const displayRating = this.interactive && this.hoverRating > 0 ? this.hoverRating : this.rating;
    const stars: { type: 'full' | 'half' | 'empty'; icon: any }[] = [];

    for (let i = 1; i <= this.maxRating; i++) {
      if (i <= Math.floor(displayRating)) {
        // Full star
        stars.push({ type: 'full', icon: this.faStar });
      } else if (i === Math.ceil(displayRating) && displayRating % 1 >= 0.5) {
        // Half star (only for non-interactive ratings)
        stars.push({ type: 'half', icon: this.faStarHalfAlt });
      } else {
        // Empty star
        stars.push({ type: 'empty', icon: this.farStar });
      }
    }

    return stars;
  }

  /**
   * Get CSS class for star size
   */
  get sizeClass(): string {
    const sizeMap = {
      'sm': 'text-sm',
      'md': 'text-base',
      'lg': 'text-xl',
      'xl': 'text-2xl'
    };
    return sizeMap[this.size];
  }

  /**
   * Handle star click (interactive mode only)
   */
  onStarClick(rating: number): void {
    if (this.interactive) {
      this.rating = rating;
      this.ratingChange.emit(rating);
    }
  }

  /**
   * Handle star hover (interactive mode only)
   */
  onStarHover(rating: number): void {
    if (this.interactive) {
      this.hoverRating = rating;
    }
  }

  /**
   * Handle mouse leave (interactive mode only)
   */
  onMouseLeave(): void {
    if (this.interactive) {
      this.hoverRating = 0;
    }
  }

  /**
   * Format review count display
   */
  get reviewCountText(): string {
    if (this.reviewCount === 0) {
      return '(No reviews)';
    } else if (this.reviewCount === 1) {
      return '(1 review)';
    } else {
      return `(${this.reviewCount} reviews)`;
    }
  }
}

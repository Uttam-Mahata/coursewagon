import { Component, Input, Output, EventEmitter } from '@angular/core';
import { faStar } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-admin-testimonials',
    standalone: false,
  templateUrl: './admin-testimonials.component.html',
  styleUrls: ['./admin-testimonials.component.css']
})
export class AdminTestimonialsComponent {
  @Input() testimonials: any[] = [];
  @Input() loading: boolean = false;
  @Input() error: string = '';
  @Output() approveTestimonial = new EventEmitter<number>();
  @Output() rejectTestimonial = new EventEmitter<number>();
  @Output() retryLoad = new EventEmitter<void>();

  // FontAwesome icons
  faStar = faStar;

  constructor() { }

  onApproveTestimonial(testimonialId: number) {
    this.approveTestimonial.emit(testimonialId);
  }

  onRejectTestimonial(testimonialId: number) {
    this.rejectTestimonial.emit(testimonialId);
  }

  onRetryLoad() {
    this.retryLoad.emit();
  }
}

import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';
import { faEnvelope, faPaperPlane, faExclamationTriangle, faCheckCircle, faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule, FontAwesomeModule],
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']
})
export class ForgotPasswordComponent {
  forgotPasswordForm: FormGroup;
  isLoading = false;
  submitted = false;
  successMessage = '';
  errorMessage = '';
  
  // Icons
  faEnvelope = faEnvelope;
  faPaperPlane = faPaperPlane;
  faExclamationTriangle = faExclamationTriangle;
  faCheckCircle = faCheckCircle;
  faArrowLeft = faArrowLeft;

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.forgotPasswordForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  onSubmit() {
    this.submitted = true;
    
    // Stop if form is invalid
    if (this.forgotPasswordForm.invalid) {
      return;
    }
    
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';
    
    this.authService.forgotPassword(this.forgotPasswordForm.value.email)
      .subscribe({
        next: (response) => {
          this.successMessage = response.message || "If your email exists in our system, you will receive a password reset link shortly.";
          this.isLoading = false;
          this.forgotPasswordForm.reset();
          this.submitted = false;
        },
        error: (error) => {
          console.error('Forgot password error:', error);
          // Always show generic message for security
          this.successMessage = "If your email exists in our system, you will receive a password reset link shortly.";
          this.isLoading = false;
        }
      });
  }

  get f() { return this.forgotPasswordForm.controls; }
  
  backToLogin() {
    this.router.navigate(['/auth']);
  }
}

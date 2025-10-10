import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-email-verification',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './email-verification.component.html',
  styleUrl: './email-verification.component.css'
})
export class EmailVerificationComponent implements OnInit {
  isVerifying = true;
  verificationSuccess = false;
  errorMessage = '';
  token = '';
  resendingEmail = false;
  resendSuccess = false;
  userEmail = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    // Get token from query params
    this.route.queryParams.subscribe(params => {
      this.token = params['token'];
      if (this.token) {
        this.verifyEmail();
      } else {
        this.isVerifying = false;
        this.errorMessage = 'Invalid verification link. No token provided.';
      }
    });
  }

  verifyEmail(): void {
    this.isVerifying = true;
    this.errorMessage = '';

    this.authService.verifyEmail(this.token).subscribe({
      next: (response) => {
        this.isVerifying = false;
        this.verificationSuccess = true;
        this.userEmail = response.user?.email || '';
        console.log('Email verified successfully:', response);
      },
      error: (error) => {
        this.isVerifying = false;
        this.verificationSuccess = false;
        console.error('Email verification error:', error);
        this.errorMessage = error.error?.detail || 'Email verification failed. The link may be invalid or expired.';
      }
    });
  }

  resendVerification(): void {
    if (!this.userEmail) {
      this.errorMessage = 'Unable to resend verification email. Email address not found.';
      return;
    }

    this.resendingEmail = true;
    this.resendSuccess = false;

    this.authService.resendVerificationEmail(this.userEmail).subscribe({
      next: (response) => {
        this.resendingEmail = false;
        this.resendSuccess = true;
        console.log('Verification email resent:', response);
      },
      error: (error) => {
        this.resendingEmail = false;
        console.error('Error resending verification:', error);
        this.errorMessage = 'Failed to resend verification email. Please try again later.';
      }
    });
  }

  goToLogin(): void {
    this.router.navigate(['/auth'], { queryParams: { mode: 'login' } });
  }
}

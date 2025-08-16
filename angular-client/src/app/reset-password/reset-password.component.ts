import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';
import { faLock, faCheckCircle, faExclamationTriangle, faArrowLeft } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-reset-password',
  standalone: false,
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.css']
})
export class ResetPasswordComponent implements OnInit {
  resetForm: FormGroup;
  token: string = '';
  isLoading = false;
  isVerifying = true;
  isTokenValid = false;
  isComplete = false;
  errorMessage = '';
  successMessage = '';
  
  // Icons
  faLock = faLock;
  faCheckCircle = faCheckCircle;
  faExclamationTriangle = faExclamationTriangle;
  faArrowLeft = faArrowLeft;

  constructor(
    private formBuilder: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService
  ) {
    this.resetForm = this.formBuilder.group({
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required]
    }, { validator: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // Get token from URL parameters
    this.route.queryParams.subscribe(params => {
      this.token = params['token'] || '';
      
      if (!this.token) {
        this.isVerifying = false;
        this.errorMessage = 'Missing password reset token. Please use the link from your email.';
        return;
      }
      
      // Verify token with backend
      this.verifyToken();
    });
  }
  
  verifyToken(): void {
    this.authService.verifyResetToken(this.token).subscribe({
      next: (response) => {
        this.isTokenValid = response.valid === true;
        this.isVerifying = false;
        
        if (!this.isTokenValid) {
          this.errorMessage = response.message || 'This password reset link has expired or is invalid.';
        }
      },
      error: (error) => {
        this.isVerifying = false;
        this.isTokenValid = false;
        this.errorMessage = error.error?.error || 'Invalid or expired reset link.';
      }
    });
  }

  onSubmit(): void {
    if (this.resetForm.invalid) {
      return;
    }
    
    this.isLoading = true;
    this.errorMessage = '';
    
    const password = this.resetForm.value.password;
    
    this.authService.resetPassword(this.token, password).subscribe({
      next: (response) => {
        this.successMessage = response.message || 'Your password has been reset successfully.';
        this.isLoading = false;
        this.isComplete = true;
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          this.router.navigate(['/auth']);
        }, 3000);
      },
      error: (error) => {
        this.errorMessage = error.error?.error || 'Failed to reset password.';
        this.isLoading = false;
      }
    });
  }
  
  passwordMatchValidator(g: FormGroup) {
    const password = g.get('password')?.value;
    const confirmPassword = g.get('confirmPassword')?.value;
    
    if (password === confirmPassword) {
      return null;
    }
    
    return { mismatch: true };
  }
  
  get f() { return this.resetForm.controls; }
  
  backToLogin() {
    this.router.navigate(['/auth']);
  }

  goToForgotPassword(): void {
    this.router.navigate(['/forgot-password']);
  }
}

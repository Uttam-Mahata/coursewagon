import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';
import { FaIconLibrary, FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faEnvelope, faLock, faUser, faUserPlus, faSignInAlt, faKey, faExclamationTriangle, faCheckCircle } from '@fortawesome/free-solid-svg-icons';
import { faGoogle } from '@fortawesome/free-brands-svg-icons';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-auth',
    templateUrl: './auth.component.html',
    standalone: true,
    imports: [CommonModule, RouterModule, ReactiveFormsModule, FontAwesomeModule]
})
export class AuthComponent implements OnInit {
  loginForm!: FormGroup;
  registerForm! : FormGroup;
  isLoginMode = true;
  errorMessage = '';
  successMessage = '';
  isGoogleLoading = false;
  registeredEmail = '';
  showVerificationMessage = false;
  resendingVerification = false;

  faEnvelope = faEnvelope;
  faLock = faLock;
  faUser = faUser;
  faUserPlus = faUserPlus;
  faSignInAlt = faSignInAlt;
  faKey = faKey;
  faExclamationTriangle = faExclamationTriangle;
  faCheckCircle = faCheckCircle;
  faGoogle = faGoogle;

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute,
    private faLibrary: FaIconLibrary,
    private formBuilder: FormBuilder
  ) {
    faLibrary.addIcons(
      faEnvelope, faLock, faUser, faUserPlus, faSignInAlt, faKey, faExclamationTriangle, faCheckCircle, faGoogle
    );
  }

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      rememberMe: [false]
    });

    this.registerForm = this.formBuilder.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });

    // Check if user is already logged in at initialization only
    // Don't subscribe to changes to avoid redirecting during active sign-in
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      console.log('User already logged in. Redirecting to courses page.');
      this.router.navigate(['/courses']);
    }

    this.route.queryParams.subscribe(params => {
      const mode = params['mode'];
      if (mode === 'signup') {
        this.isLoginMode = false;
      } else if (mode === 'login') {
        this.isLoginMode = true;
      }
    });
  }

  toggleMode(): void {
    this.isLoginMode = !this.isLoginMode;
    this.clearMessages();
  }

  onSubmit(): void {
    this.clearMessages();
    
    if (this.isLoginMode) {
      this.onLogin();
    } else {
      this.onRegister();
    }
  }

  onLogin(): void {
    if (this.loginForm.invalid) {
      this.errorMessage = 'Please enter a valid email and password';
      return;
    }
    
    const { email, password, rememberMe } = this.loginForm.value;
    console.log('Attempting login with email:', email, 'Remember me:', rememberMe);
    
    this.authService.login(email, password, rememberMe)
      .subscribe({
        next: (response) => {
          console.log('Login successful, response:', response);
          this.successMessage = 'Login successful! Redirecting...';
          setTimeout(() => {
            this.router.navigate(['/courses']);
          }, 100);
        },
        error: (error) => {
          console.error('Login error:', error);
          this.errorMessage = this.getErrorMessage(error);
        }
      });
  }

  onRegister(): void {
    if (this.registerForm.invalid) {
      this.errorMessage = 'Please fill out all fields correctly.';
      return;
    }

    this.authService.register(this.registerForm.value)
      .subscribe({
        next: (response) => {
          this.registeredEmail = this.registerForm.value.email;
          this.showVerificationMessage = true;
          this.successMessage = '';
          this.registerForm.reset();
          console.log('Registration successful:', response);
        },
        error: (error) => {
          console.error('Registration error:', error);
          this.errorMessage = this.getErrorMessage(error);
        }
      });
  }

  resendVerificationEmail(): void {
    if (!this.registeredEmail) {
      return;
    }

    this.resendingVerification = true;
    this.clearMessages();

    this.authService.resendVerificationEmail(this.registeredEmail)
      .subscribe({
        next: (response) => {
          this.resendingVerification = false;
          this.successMessage = 'Verification email resent! Please check your inbox.';
          console.log('Verification email resent:', response);
        },
        error: (error) => {
          this.resendingVerification = false;
          console.error('Error resending verification:', error);
          this.errorMessage = this.getErrorMessage(error);
        }
      });
  }

  backToRegister(): void {
    this.showVerificationMessage = false;
    this.registeredEmail = '';
    this.isLoginMode = false;
  }

  // Google Sign-In method
  async onGoogleSignIn(): Promise<void> {
    this.clearMessages();
    this.isGoogleLoading = true;
    
    try {
      console.log('Attempting Google sign-in...');
      const response = await this.authService.signInWithGoogle();
      console.log('Google sign-in successful:', response);
      
      // Show success message
      this.successMessage = 'Google sign-in successful! Redirecting...';
      
      setTimeout(() => {
        this.router.navigate(['/courses']);
      }, 1000);
    } catch (error: any) {
      console.error('Google sign-in error:', error);
      this.errorMessage = this.getErrorMessage(error);
    } finally {
      this.isGoogleLoading = false;
    }
  }

  private getErrorMessage(error: any): string {
    console.log('Processing error:', error);
    
    // Handle null or undefined error
    if (!error) {
      return 'An unexpected error occurred. Please try again.';
    }

    // Handle different error response structures from backend
    if (error.error !== null && error.error !== undefined) {
      // Backend API error responses
      if (typeof error.error === 'string') {
        return error.error;
      }
      if (error.error.error) {
        return error.error.error;
      }
      if (error.error.detail) {
        if (typeof error.error.detail === 'string') {
          return error.error.detail;
        }
        if (error.error.detail.error) {
          return error.error.detail.error;
        }
      }
      if (error.error.message) {
        return error.error.message;
      }
    }
    
    // Firebase authentication errors
    if (error.message && typeof error.message === 'string') {
      // Check for technical error messages that shouldn't be shown to users
      if (error.message.includes('Http failure response for (unknown url)')) {
        // This is a CORS or network error
        if (error.status === 401) {
          return 'Login failed. Please check your email and password.';
        }
        if (error.status === 0) {
          return 'Cannot connect to the server. Please check your internet connection.';
        }
        return 'Connection error. Please check your internet connection and try again.';
      }
      
      if (error.message.includes('auth/user-not-found')) {
        return 'No account found with this email. Please sign up first.';
      }
      if (error.message.includes('auth/wrong-password')) {
        return 'Incorrect password. Please try again or use "Forgot password".';
      }
      if (error.message.includes('auth/invalid-email')) {
        return 'Please enter a valid email address.';
      }
      if (error.message.includes('auth/user-disabled')) {
        return 'Your account has been disabled. Please contact support.';
      }
      if (error.message.includes('auth/email-already-in-use')) {
        return 'An account with this email already exists. Please login instead.';
      }
      if (error.message.includes('auth/weak-password')) {
        return 'Password is too weak. Please use at least 6 characters.';
      }
      if (error.message.includes('auth/network-request-failed')) {
        return 'Network error. Please check your internet connection.';
      }
      if (error.message.includes('auth/popup-closed-by-user')) {
        return 'Sign-in cancelled. Please try again.';
      }
      if (error.message.includes('auth/popup-blocked')) {
        return 'Pop-up was blocked. Please allow pop-ups for this site.';
      }
      if (error.message.includes('auth/cancelled-popup-request')) {
        return 'Sign-in cancelled. Please try again.';
      }
      
      // Don't return technical error messages
      if (!error.message.includes('Http failure') && !error.message.includes('Unknown Error')) {
        return error.message;
      }
    }
    
    // HTTP status-based messages (fallback for when error.error is null)
    if (error.status === 0) {
      return 'Cannot connect to the server. Please check your internet connection.';
    }
    if (error.status === 400) {
      return 'Invalid request. Please check your input and try again.';
    }
    if (error.status === 401) {
      return 'Login failed. Please check your email and password.';
    }
    if (error.status === 403) {
      return 'Access denied. Your account may be inactive or you may not have permission.';
    }
    if (error.status === 404) {
      return 'Service not found. Please try again later.';
    }
    if (error.status >= 500) {
      return 'Server error. Please try again later.';
    }
    
    // Default fallback
    return 'An unexpected error occurred. Please try again.';
  }

  clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }
}

import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';
import { FaIconLibrary } from '@fortawesome/angular-fontawesome';
import { faEnvelope, faLock, faUser, faUserPlus, faSignInAlt, faKey, faExclamationTriangle, faCheckCircle } from '@fortawesome/free-solid-svg-icons';
import { faGoogle } from '@fortawesome/free-brands-svg-icons';

@Component({
    selector: 'app-auth',
    templateUrl: './auth.component.html',
    standalone: false
})
export class AuthComponent implements OnInit {
  // FontAwesome icons
  faEnvelope = faEnvelope;
  faLock = faLock;
  faUser = faUser;
  faUserPlus = faUserPlus;
  faSignInAlt = faSignInAlt;
  faKey = faKey;
  faExclamationTriangle = faExclamationTriangle;
  faCheckCircle = faCheckCircle;
  faGoogle = faGoogle;
  
  isLoginMode = true;
  errorMessage = '';
  successMessage = '';
  isGoogleLoading = false;
  
  loginData = {
    email: '',
    password: '',
    rememberMe: false  // Add remember me field
  };

  registerData = {
    email: '',
    password: '',
    first_name: '',
    last_name: ''
  };

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute, // Add ActivatedRoute to access query params
    private faLibrary: FaIconLibrary
  ) {
    faLibrary.addIcons(
      faEnvelope, faLock, faUser, faUserPlus, faSignInAlt, faKey, faExclamationTriangle, faCheckCircle, faGoogle
    );
  }

  ngOnInit(): void {
    // Check if user is already logged in
    this.authService.isLoggedIn$.subscribe(
      (isLoggedIn: boolean) => {
        if (isLoggedIn) {
          console.log('User already logged in. Redirecting to courses page.');
          this.router.navigate(['/courses']);
        }
      }
    );

    // Check for mode in query parameters
    this.route.queryParams.subscribe(params => {
      const mode = params['mode'];
      if (mode === 'signup') {
        this.isLoginMode = false;
      } else if (mode === 'login') {
        this.isLoginMode = true;
      }
      // If no mode is specified, default to login mode (already set)
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
    if (!this.loginData.email || !this.loginData.password) {
      this.errorMessage = 'Please enter both email and password';
      return;
    }
    
    console.log('Attempting login with email:', this.loginData.email, 'Remember me:', this.loginData.rememberMe);
    
    this.authService.login(
      this.loginData.email, 
      this.loginData.password, 
      this.loginData.rememberMe  // Pass the remember me value
    )
      .subscribe({
        next: (response) => {
          console.log('Login successful, response:', response);
          setTimeout(() => {
            this.router.navigate(['/courses']);
          }, 100);
        },
        error: (error) => {
          console.error('Login error:', error);
          this.errorMessage = error.error?.error || 'An unexpected error occurred';
        }
      });
  }

  onRegister(): void {
    this.authService.register(this.registerData)
      .subscribe({
        next: () => {
          this.successMessage = 'Registration successful! Please check your email for a welcome message and then login.';
          this.isLoginMode = true;
          this.loginData.email = this.registerData.email;
          this.registerData = {
            email: '',
            password: '',
            first_name: '',
            last_name: ''
          };
        },
        error: (error) => {
          this.errorMessage = error.error.error || 'An unexpected error occurred';
        }
      });
  }

  // Google Sign-In method
  async onGoogleSignIn(): Promise<void> {
    this.clearMessages();
    this.isGoogleLoading = true;
    
    try {
      console.log('Attempting Google sign-in...');
      const response = await this.authService.signInWithGoogle();
      console.log('Google sign-in successful:', response);
      
      setTimeout(() => {
        this.router.navigate(['/courses']);
      }, 100);
    } catch (error: any) {
      console.error('Google sign-in error:', error);
      this.errorMessage = error.message || 'Google sign-in failed. Please try again.';
    } finally {
      this.isGoogleLoading = false;
    }
  }

  clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }
}

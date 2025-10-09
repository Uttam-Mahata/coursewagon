import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';
import { FaIconLibrary } from '@fortawesome/angular-fontawesome';
import { faEnvelope, faLock, faUser, faUserPlus, faSignInAlt, faKey, faExclamationTriangle, faCheckCircle } from '@fortawesome/free-solid-svg-icons';
import { faGoogle } from '@fortawesome/free-brands-svg-icons';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors, AsyncValidatorFn } from '@angular/forms';
import { Observable, of, forkJoin } from 'rxjs';
import { map, catchError, debounceTime, switchMap, first } from 'rxjs/operators';

@Component({
    selector: 'app-auth',
    templateUrl: './auth.component.html',
    standalone: false
})
export class AuthComponent implements OnInit {
  loginForm!: FormGroup;
  registerForm! : FormGroup;
  isLoginMode = true;
  errorMessage = '';
  successMessage = '';
  isGoogleLoading = false;
  isCheckingEmail = false;
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
      email: ['', [Validators.required, Validators.email], [this.emailExistsValidator()]],
      password: ['', Validators.required]
    });

    this.authService.isLoggedIn$.subscribe(
      (isLoggedIn: boolean) => {
        if (isLoggedIn) {
          console.log('User already logged in. Redirecting to courses page.');
          this.router.navigate(['/courses']);
        }
      }
    );

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
          this.errorMessage = error.error?.detail || error.error?.error || 'Registration failed. Please try again.';
        }
      });
  }

  resendVerificationEmail(): void {
    if (!this.registeredEmail) {
      return;
    }

    this.resendingVerification = true;
    this.errorMessage = '';

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
          this.errorMessage = 'Failed to resend verification email. Please try again.';
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
      
      // Provide more detailed error messages
      if (error.error?.detail) {
        this.errorMessage = error.error.detail;
      } else if (error.message) {
        this.errorMessage = error.message;
      } else {
        this.errorMessage = 'Google sign-in failed. Please try again.';
      }
    } finally {
      this.isGoogleLoading = false;
    }
  }

  clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }

  // Async validator to check if email already exists
  emailExistsValidator(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      if (!control.value) {
        return of(null);
      }

      this.isCheckingEmail = true;
      
      return of(control.value).pipe(
        debounceTime(500), // Wait 500ms after user stops typing
        switchMap(email => 
          this.authService.checkEmailExists(email).pipe(
            map(response => {
              this.isCheckingEmail = false;
              // If email exists, return error
              return response.exists ? { emailExists: true } : null;
            }),
            catchError(() => {
              this.isCheckingEmail = false;
              // On error, allow the user to continue (fail open)
              return of(null);
            })
          )
        ),
        first() // Complete after first emission
      );
    };
  }

  // Getter for easy access to email validation state
  get emailControl() {
    return this.registerForm.get('email');
  }

  get isEmailTaken(): boolean {
    const emailControl = this.emailControl;
    return emailControl ? emailControl.hasError('emailExists') && !this.isCheckingEmail : false;
  }

  get isEmailAvailable(): boolean {
    const emailControl = this.emailControl;
    return emailControl ? 
      emailControl.valid && 
      emailControl.dirty && 
      emailControl.value && 
      !this.isCheckingEmail : 
      false;
  }
}

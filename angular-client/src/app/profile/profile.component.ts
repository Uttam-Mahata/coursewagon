import { Component, OnInit } from '@angular/core';
import { AuthService } from '../services/auth/auth.service';
import { Router } from '@angular/router';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { 
  faEnvelope, faCheckCircle, faTimesCircle, 
  faExclamationCircle, faTimes,
  faEye, faEyeSlash, faLock, faSave
} from '@fortawesome/free-solid-svg-icons';

@Component({
    selector: 'app-profile',
    
    templateUrl: './profile.component.html',
    styleUrls: ['./profile.component.scss'],
    standalone: false
})
export class ProfileComponent implements OnInit {
  // FontAwesome icons
  faEnvelope = faEnvelope;
  faCheckCircle = faCheckCircle;
  faTimesCircle = faTimesCircle;
  faExclamationCircle = faExclamationCircle;
  faTimes = faTimes;
  faEye = faEye;
  faEyeSlash = faEyeSlash;
  faLock = faLock;
  faSave = faSave;

  user: any = null;
  successMessage: string = '';
  errorMessage: string = '';
  isLoading: {[key: string]: boolean} = {
    passwordChange: false
  };
  token: string | null = null;
  
  // Password change form
  passwordForm: FormGroup;
  showCurrentPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private fb: FormBuilder
  ) {
    // Initialize password change form
    this.passwordForm = this.fb.group({
      currentPassword: ['', [Validators.required]],
      newPassword: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]]
    }, { validator: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    // Store token for debugging
    this.token = this.authService.getToken();
    console.log('Profile component initialized, token:', this.token?.substring(0, 10) + '...');
    
    this.authService.currentUser$.subscribe(user => {
      this.user = user;
      console.log('Current user in profile:', user);
    });
    
    // Check if we have a valid token and immediately try to fetch current user
    if (!this.token) {
      console.log('No token found, redirecting to login');
      this.errorMessage = 'You need to log in first';
      setTimeout(() => {
        this.router.navigate(['/auth']);
      }, 2000);
    } else {
      // Get the current user
      this.user = this.authService.getCurrentUser();
    }
  }

  // Password change functions
  togglePasswordVisibility(field: string): void {
    if (field === 'current') {
      this.showCurrentPassword = !this.showCurrentPassword;
    } else if (field === 'new') {
      this.showNewPassword = !this.showNewPassword;
    } else if (field === 'confirm') {
      this.showConfirmPassword = !this.showConfirmPassword;
    }
  }

  changePassword(): void {
    if (this.passwordForm.invalid) {
      return;
    }

    this.isLoading['passwordChange'] = true;
    this.clearMessages();

    const currentPassword = this.passwordForm.get('currentPassword')?.value;
    const newPassword = this.passwordForm.get('newPassword')?.value;

    this.authService.changePassword(currentPassword, newPassword)
      .subscribe({
        next: (response) => {
          this.successMessage = response.message || 'Password changed successfully';
          this.isLoading['passwordChange'] = false;
          this.passwordForm.reset();
        },
        error: (err) => {
          this.errorMessage = err.error?.error || 'Failed to change password';
          this.isLoading['passwordChange'] = false;
        }
      });
  }

  clearMessages(): void {
    this.successMessage = '';
    this.errorMessage = '';
  }

  passwordMatchValidator(g: FormGroup) {
    const newPassword = g.get('newPassword')?.value;
    const confirmPassword = g.get('confirmPassword')?.value;
    
    if (newPassword === confirmPassword) {
      return null;
    }
    
    return { mismatch: true };
  }
}

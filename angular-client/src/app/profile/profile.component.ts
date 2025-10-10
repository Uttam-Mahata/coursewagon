import { Component, OnInit } from '@angular/core';
import { AuthService } from '../services/auth/auth.service';
import { Router, RouterModule } from '@angular/router';
import { FormGroup, FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import {
  faEnvelope, faCheckCircle, faTimesCircle,
  faExclamationCircle, faTimes,
  faEye, faEyeSlash, faLock, faSave, faUser,
  faCalendar, faShieldAlt, faEdit, faCamera, faUserTag
} from '@fortawesome/free-solid-svg-icons';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@Component({
    selector: 'app-profile',
    
    templateUrl: './profile.component.html',
    styleUrls: ['./profile.component.scss'],
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, FontAwesomeModule, RouterModule]
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
  faUser = faUser;
  faCalendar = faCalendar;
  faShieldAlt = faShieldAlt;
  faEdit = faEdit;
  faCamera = faCamera;
  faUserTag = faUserTag;

  user: any = null;
  successMessage: string = '';
  errorMessage: string = '';
  isLoading: {[key: string]: boolean} = {
    passwordChange: false,
    profileUpdate: false
  };

  // Forms
  passwordForm: FormGroup;
  profileForm: FormGroup;

  // UI State
  showCurrentPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;
  isEditingProfile = false;

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

    // Initialize profile edit form
    this.profileForm = this.fb.group({
      first_name: ['', [Validators.required]],
      last_name: ['', [Validators.required]],
      bio: [''],
      role: ['both', [Validators.required]]
    });
  }

  ngOnInit(): void {
    console.log('Profile component initialized');

    this.authService.currentUser$.subscribe(user => {
      this.user = user;
      console.log('Current user in profile:', user);

      // Populate profile form when user data is available
      if (user) {
        this.profileForm.patchValue({
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          bio: user.bio || '',
          role: user.role || 'both'
        });
      }
    });

    // Check if user is logged in
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser) {
      console.log('No user found, redirecting to login');
      this.errorMessage = 'You need to log in first';
      setTimeout(() => {
        this.router.navigate(['/auth']);
      }, 2000);
    } else {
      // Get the current user
      this.user = currentUser;
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

  // Profile editing functions
  toggleEditProfile(): void {
    this.isEditingProfile = !this.isEditingProfile;
    if (!this.isEditingProfile) {
      // Reset form when canceling
      this.profileForm.patchValue({
        first_name: this.user?.first_name || '',
        last_name: this.user?.last_name || '',
        bio: this.user?.bio || '',
        role: this.user?.role || 'both'
      });
    }
  }

  updateProfile(): void {
    if (this.profileForm.invalid) {
      return;
    }

    this.isLoading['profileUpdate'] = true;
    this.clearMessages();

    const profileData = this.profileForm.value;

    this.authService.updateProfile(profileData).subscribe({
      next: (response) => {
        this.successMessage = 'Profile updated successfully';
        this.isLoading['profileUpdate'] = false;
        this.isEditingProfile = false;
        // The user data will be automatically updated via currentUser$ subscription
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'Failed to update profile';
        this.isLoading['profileUpdate'] = false;
      }
    });
  }

  getRoleDisplayName(role: string): string {
    const roleMap: {[key: string]: string} = {
      'creator': 'Creator',
      'learner': 'Learner',
      'both': 'Creator & Learner'
    };
    return roleMap[role] || role;
  }

  getRoleBadgeClass(role: string): string {
    const classMap: {[key: string]: string} = {
      'creator': 'bg-purple-100 text-purple-800',
      'learner': 'bg-green-100 text-green-800',
      'both': 'bg-blue-100 text-blue-800'
    };
    return classMap[role] || 'bg-gray-100 text-gray-800';
  }

  formatDate(dateString: string): string {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}

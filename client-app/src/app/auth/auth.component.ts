import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.scss']
})
export class AuthComponent {
  isLoginMode = true;
  errorMessage = '';
  successMessage = '';
  
  loginData = {
    email: '',
    password: ''
  };

  registerData = {
    email: '',
    password: '',
    first_name: '',
    last_name: ''
  };

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

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
    this.authService.login(this.loginData.email, this.loginData.password)
      .subscribe({
        next: () => {
          this.router.navigate(['/courses']);
        },
        error: (error) => {
          this.errorMessage = error.error.error || 'An unexpected error occurred';
        }
      });
  }

  onRegister(): void {
    this.authService.register(this.registerData)
      .subscribe({
        next: () => {
          this.successMessage = 'Registration successful! Please login.';
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

  clearMessages(): void {
    this.errorMessage = '';
    this.successMessage = '';
  }
}

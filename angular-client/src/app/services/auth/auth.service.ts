import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError, lastValueFrom } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { Router } from '@angular/router';
import { FirebaseAuthService } from '../firebase-auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private authUrl = environment.authApiUrl;
  private userKey = 'current_user';  // Still store user data for convenience

  // Observable sources
  private currentUserSource = new BehaviorSubject<any>(this.getInitialUser());
  private isLoggedInSource = new BehaviorSubject<boolean>(this.getInitialAuthState());
  private isCheckingAuthSource = new BehaviorSubject<boolean>(false);

  // Observable streams
  currentUser$ = this.currentUserSource.asObservable();
  isLoggedIn$ = this.isLoggedInSource.asObservable();
  isCheckingAuth$ = this.isCheckingAuthSource.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router,
    private firebaseAuthService: FirebaseAuthService
  ) {
    // Initialize from localStorage immediately (synchronous - no flash!)
    // Then verify with backend (asynchronous - security check)
    this.checkAuthState();
  }

  /**
   * Get initial auth state from localStorage (synchronous)
   * This prevents the flash of unauthenticated content on page load
   */
  private getInitialAuthState(): boolean {
    const userStr = localStorage.getItem(this.userKey);
    return userStr !== null;
  }

  /**
   * Get initial user data from localStorage (synchronous)
   */
  private getInitialUser(): any {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  checkAuthState(): void {
    // Set checking flag to true
    this.isCheckingAuthSource.next(true);

    // Always verify with backend to check if HttpOnly cookie is still valid
    // Don't trust localStorage alone as cookies might have been deleted
    this.http.get(`${this.authUrl}/profile`, { withCredentials: true }).subscribe({
      next: (userData: any) => {
        // Valid session - store/update user data
        this.storeUser(userData);
        this.isCheckingAuthSource.next(false);
        console.log('Auth state checked - User is logged in', {user: userData});
      },
      error: () => {
        // No valid session - clear any stale data
        this.clearAuthData();
        this.isCheckingAuthSource.next(false);
        console.log('Auth state checked - User is not logged in');
      }
    });
  }

  login(email: string, password: string, rememberMe: boolean = false): Observable<any> {
    console.log(`Attempting to login with ${email}, remember me: ${rememberMe}`);
    return this.http.post(`${this.authUrl}/login`, {
      email,
      password,
      remember_me: rememberMe
    }, { withCredentials: true }).pipe(
      tap((response: any) => {
        console.log('Login successful, storing user data', response);
        // Tokens are in HttpOnly cookies - just store user data
        this.storeUser(response.user);
      })
    );
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.authUrl}/register`, userData, { withCredentials: true });
  }

  checkEmailExists(email: string): Observable<any> {
    return this.http.post(`${this.authUrl}/check-email`, { email }, { withCredentials: true });
  }

  validateEmail(email: string): Observable<any> {
    return this.http.post(`${this.authUrl}/validate-email`, { email }, { withCredentials: true });
  }

  verifyEmail(token: string): Observable<any> {
    return this.http.post(`${this.authUrl}/verify-email`, { token }, { withCredentials: true });
  }

  resendVerificationEmail(email: string): Observable<any> {
    return this.http.post(`${this.authUrl}/resend-verification`, { email }, { withCredentials: true });
  }

  getVerificationStatus(): Observable<any> {
    return this.http.get(`${this.authUrl}/verification-status`, { withCredentials: true });
  }

  logout(): void {
    // Call backend to clear cookies
    this.http.post(`${this.authUrl}/logout`, {}, { withCredentials: true }).subscribe({
      next: () => {
        console.log('Logout successful');
      },
      error: (error) => {
        console.error('Logout error:', error);
      },
      complete: () => {
        // Always clear local data and redirect
        this.clearAuthData();
        this.router.navigate(['/auth']);
      }
    });
  }

  getCurrentUser(): any {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  // Password reset methods
  forgotPassword(email: string): Observable<any> {
    // Get current frontend URL to send in request for proper redirect
    const frontendUrl = window.location.origin;
    return this.http.post(`${this.authUrl}/forgot-password`, {
      email,
      frontend_url: frontendUrl
    }, { withCredentials: true });
  }

  verifyResetToken(token: string): Observable<any> {
    return this.http.post(`${this.authUrl}/verify-reset-token`, { token }, { withCredentials: true });
  }

  resetPassword(token: string, password: string): Observable<any> {
    return this.http.post(`${this.authUrl}/reset-password`, { token, password }, { withCredentials: true });
  }

  changePassword(currentPassword: string, newPassword: string): Observable<any> {
    return this.http.post(`${this.authUrl}/change-password`, {
      current_password: currentPassword,
      new_password: newPassword
    }, { withCredentials: true });
  }

  updateProfile(profileData: any): Observable<any> {
    return this.http.put(`${this.authUrl}/profile`, profileData, { withCredentials: true }).pipe(
      tap((response: any) => {
        // Update stored user data with new profile information
        const currentUser = this.getCurrentUser();
        if (currentUser && response.user) {
          this.storeUser(response.user);
        }
      })
    );
  }

  // Google Authentication Methods
  async signInWithGoogle(): Promise<any> {
    try {
      const firebaseResult = await this.firebaseAuthService.signInWithGoogle();

      // Extract user information from Firebase
      const { user, accessToken } = firebaseResult;

      // Send the Firebase ID token to your backend for verification and registration/login
      const backendResponse = await lastValueFrom(
        this.http.post(`${this.authUrl}/google-auth`, {
          firebase_token: accessToken,
          user_data: {
            uid: user.uid,
            email: user.email,
            display_name: user.displayName,
            photo_url: user.photoURL,
            email_verified: user.emailVerified
          }
        }, { withCredentials: true })
      );

      // Store user data (tokens are in HttpOnly cookies)
      if (backendResponse && (backendResponse as any).user) {
        this.storeUser((backendResponse as any).user);
        return backendResponse;
      }

      throw new Error('Invalid response from backend');
    } catch (error) {
      console.error('Google sign-in error:', error);
      throw error;
    }
  }

  async signOutGoogle(): Promise<void> {
    try {
      await this.firebaseAuthService.signOut();
      this.logout();
    } catch (error) {
      console.error('Google sign-out error:', error);
      // Still logout locally even if Firebase logout fails
      this.logout();
    }
  }

  private storeUser(user: any): void {
    localStorage.setItem(this.userKey, JSON.stringify(user));
    this.currentUserSource.next(user);
    this.isLoggedInSource.next(true);
  }

  private clearAuthData(): void {
    // Only clear user data from localStorage (tokens are in HttpOnly cookies)
    localStorage.removeItem(this.userKey);
    this.currentUserSource.next(null);
    this.isLoggedInSource.next(false);
  }

  // Role-based methods for learner functionality

  /**
   * Get user's role (creator, learner, or both)
   */
  getUserRole(): string {
    const user = this.getCurrentUser();
    return user?.role || 'both';
  }

  /**
   * Check if user is a creator
   */
  isCreator(): boolean {
    const role = this.getUserRole();
    return role === 'creator' || role === 'both';
  }

  /**
   * Check if user is a learner
   */
  isLearner(): boolean {
    const role = this.getUserRole();
    return role === 'learner' || role === 'both';
  }

  /**
   * Check if user is admin
   */
  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.is_admin === true;
  }
}

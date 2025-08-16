import { Injectable } from '@angular/core';
import { 
  Auth, 
  signInWithPopup, 
  signOut, 
  GoogleAuthProvider, 
  User,
  onAuthStateChanged,
  getAuth
} from 'firebase/auth';
import { BehaviorSubject, Observable } from 'rxjs';
import { initializeApp } from 'firebase/app';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class FirebaseAuthService {
  private auth: Auth;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor() {
    // Initialize Firebase
    const app = initializeApp(environment.firebase);
    this.auth = getAuth(app);
    
    // Listen to auth state changes
    onAuthStateChanged(this.auth, (user: User | null) => {
      this.currentUserSubject.next(user);
    });
  }

  async signInWithGoogle(): Promise<any> {
    try {
      const provider = new GoogleAuthProvider();
      provider.setCustomParameters({
        prompt: 'select_account'
      });
      
      const result = await signInWithPopup(this.auth, provider);
      
      // Extract user information
      const user = result.user;
      const userData = {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
        emailVerified: user.emailVerified
      };

      return {
        user: userData,
        accessToken: await user.getIdToken()
      };
    } catch (error: any) {
      console.error('Google sign-in error:', error);
      throw error;
    }
  }

  async signOut(): Promise<void> {
    try {
      await signOut(this.auth);
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  async getCurrentUserToken(): Promise<string | null> {
    const user = this.getCurrentUser();
    if (user) {
      return await user.getIdToken();
    }
    return null;
  }
}

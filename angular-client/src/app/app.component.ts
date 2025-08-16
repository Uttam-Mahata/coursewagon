import { Component, OnInit } from '@angular/core';
import { AuthService } from './services/auth/auth.service';
import { NavigationService } from './services/navigation.service';
import { faBars, faTimes, faGraduationCap, faShoppingCart, faBook, faUser, faPowerOff, faSignInAlt, faUserPlus, faUserShield } from '@fortawesome/free-solid-svg-icons'; // Import admin icon

@Component({
    selector: 'app-root',
    standalone: false,
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css'],
    
})
export class AppComponent implements OnInit {
  title = 'CourseWagon';
  isAuthenticated = false;
  isNavbarOpen = false;
  isAdmin = false;

  // Assign icons to properties
  faBars = faBars;
  faTimes = faTimes;
  faGraduationCap = faGraduationCap;
  faShoppingCart = faShoppingCart;
  faBook = faBook;
  faUser = faUser;
  faPowerOff = faPowerOff;
  faSignInAlt = faSignInAlt;
  faUserPlus = faUserPlus;
  faUserShield = faUserShield; // Add admin icon

  constructor(
    private authService: AuthService,
    private navigationService: NavigationService // Inject NavigationService
  ) {}

  ngOnInit(): void {
    // Use isLoggedIn$ directly instead of isAuthenticated method
    this.authService.isLoggedIn$.subscribe(
      (isAuth: boolean) => {
        console.log('App component - authentication state changed:', isAuth);
        this.isAuthenticated = isAuth;
        
        // Check if the user is an admin
        if (isAuth) {
          const user = this.authService.getCurrentUser();
          this.isAdmin = user && user.is_admin;
        } else {
          this.isAdmin = false;
        }
      }
    );
  }

  toggleNavbar(): void {
    this.isNavbarOpen = !this.isNavbarOpen;
  }

  onLogout(): void {
    this.authService.logout();
  }
  
  // Add method to manually scroll to top when needed
  scrollToTop(): void {
    this.navigationService.scrollToTop();
  }
}

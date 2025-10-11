import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { AuthService } from './services/auth/auth.service';
import { NavigationService } from './services/navigation.service';
import { ThemeService } from './services/theme.service';
import {
  faBars, faTimes, faGraduationCap, faShoppingCart, faBook, faUser,
  faPowerOff, faSignInAlt, faUserPlus, faUserShield, faChartLine,
  faBookOpen, faSearch, faMoon, faSun
} from '@fortawesome/free-solid-svg-icons';
import { FooterComponent } from './footer/footer.component';
import { ToastContainerComponent } from './toast-container/toast-container.component';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, RouterModule, FontAwesomeModule, FooterComponent, ToastContainerComponent],
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css'],

})
export class AppComponent implements OnInit {
  title = 'CourseWagon';
  isAuthenticated = false;
  isNavbarOpen = false;
  isAdmin = false;
  isCreator = false;
  isLearner = false;

  // Assign icons to properties
  faBars = faBars;
  faTimes = faTimes;
  faGraduationCap = faGraduationCap;
  faShoppingCart = faShoppingCart;
  faBook = faBook;
  faBookOpen = faBookOpen;
  faSearch = faSearch;
  faUser = faUser;
  faPowerOff = faPowerOff;
  faSignInAlt = faSignInAlt;
  faUserPlus = faUserPlus;
  faUserShield = faUserShield;
  faChartLine = faChartLine;
  faMoon = faMoon;
  faSun = faSun;

  constructor(
    private authService: AuthService,
    private navigationService: NavigationService,
    public themeService: ThemeService // Inject ThemeService
  ) {}

  ngOnInit(): void {
    // Use isLoggedIn$ directly instead of isAuthenticated method
    this.authService.isLoggedIn$.subscribe(
      (isAuth: boolean) => {
        console.log('App component - authentication state changed:', isAuth);
        this.isAuthenticated = isAuth;

        // Check user roles
        if (isAuth) {
          const user = this.authService.getCurrentUser();
          this.isAdmin = user && user.is_admin;
          this.isCreator = this.authService.isCreator();
          this.isLearner = this.authService.isLearner();
        } else {
          this.isAdmin = false;
          this.isCreator = false;
          this.isLearner = false;
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

  // Toggle theme between light and dark mode
  toggleTheme(): void {
    this.themeService.toggleTheme();
  }
}

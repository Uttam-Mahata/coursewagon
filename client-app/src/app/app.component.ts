import { Component, OnInit } from '@angular/core';
import { AuthService } from './auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  isNavbarOpen = false;
  isAuthenticated = false;

  constructor(private authService: AuthService) {}

  ngOnInit() {
    // Subscribe to authentication state changes
    this.authService.isAuthenticated().subscribe(
      isAuth => {
        this.isAuthenticated = isAuth;
      }
    );
  }

  toggleNavbar() {
    this.isNavbarOpen = !this.isNavbarOpen;
  }

  onLogout() {
    this.authService.logout();
  }
}

import { Component, OnInit } from '@angular/core';
import { 
  faMagic, 
  faBrain, 
  faLaptopCode, 
  faChartLine, 
  faBookOpen, 
  faShoppingCart, 
  faLayerGroup, 
  faSitemap, 
  faUserPlus 
} from '@fortawesome/free-solid-svg-icons';
import { NavigationService } from '../services/navigation.service';
import { AuthService } from '../services/auth/auth.service';

@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrl: './home.component.css',
    standalone: false
})
export class HomeComponent implements OnInit { 
  // FontAwesome icons
  faMagic = faMagic;
  faBrain = faBrain;
  faLaptopCode = faLaptopCode;
  faChartLine = faChartLine;
  faBookOpen = faBookOpen;
  faShoppingCart = faShoppingCart;
  faLayerGroup = faLayerGroup;
  faSitemap = faSitemap;
  faUserPlus = faUserPlus;
  
  isLoggedIn = false;
  
  constructor(
    private navigationService: NavigationService,
    private authService: AuthService
  ) {}
  
  ngOnInit(): void {
    this.authService.isLoggedIn$.subscribe(isLoggedIn => {
      this.isLoggedIn = isLoggedIn;
    });
  }
  
  // Method to scroll to top when links are clicked
  scrollToTop(): void {
    this.navigationService.scrollToTop();
  }
}

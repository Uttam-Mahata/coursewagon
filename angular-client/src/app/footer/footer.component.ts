import { Component } from '@angular/core';
import { 
  faFacebook, 
  faTwitter, 
  faLinkedin, 
  faInstagram 
} from '@fortawesome/free-brands-svg-icons';
import { 
  faMapMarkerAlt, 
  faEnvelope, 
  faPhone, 
  faChevronRight 
} from '@fortawesome/free-solid-svg-icons';
import { NavigationService } from '../services/navigation.service';

@Component({
    selector: 'app-footer',
    templateUrl: './footer.component.html',
    styleUrl: './footer.component.css',
    standalone: false
})
export class FooterComponent {
  // Brand icons
  faFacebook = faFacebook;
  faTwitter = faTwitter;
  faLinkedin = faLinkedin;
  faInstagram = faInstagram;
  
  // Solid icons
  faMapMarkerAlt = faMapMarkerAlt;
  faEnvelope = faEnvelope;
  faPhone = faPhone;
  faChevronRight = faChevronRight;
  
  constructor(private navigationService: NavigationService) {}
  
  // Method to scroll to top when footer links are clicked
  scrollToTop(): void {
    this.navigationService.scrollToTop();
  }
}

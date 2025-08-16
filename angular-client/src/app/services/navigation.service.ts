import { Injectable } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'

})
export class NavigationService {

  constructor(private router: Router) {
    // Subscribe to router events to handle scroll behavior
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      // Scroll to top on navigation end
      this.scrollToTop();
    });
  }

  /**
   * Scrolls the window to the top with smooth animation
   */
  scrollToTop(): void {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

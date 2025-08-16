import { Injectable } from '@angular/core';
import { Router, Resolve, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RouteRedirectResolver implements Resolve<boolean> {
  
  constructor(private router: Router) {}
  
  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
    // Check if we're accessing an old route pattern
    const urlPath = state.url;
    
    // Handle old topic content route format
    const contentPattern = /\/courses\/(\d+)\/subjects\/(\d+)\/chapters\/(\d+)\/topics\/(\d+)\/content/;
    const contentMatch = urlPath.match(contentPattern);
    
    if (contentMatch) {
      const [, courseId, subjectId, , topicId] = contentMatch;
      // Redirect to new format
      this.router.navigate([`/courses/${courseId}/subjects/${subjectId}/content/${topicId}`]);
      return of(false);
    }
    
    // Handle old topics route format
    const topicsPattern = /\/courses\/(\d+)\/subjects\/(\d+)\/chapters\/(\d+)\/topics/;
    const topicsMatch = urlPath.match(topicsPattern);
    
    if (topicsMatch) {
      const [, courseId, subjectId] = topicsMatch;
      // Redirect to the new content view without specific topic
      this.router.navigate([`/courses/${courseId}/subjects/${subjectId}/content`]);
      return of(false);
    }
    
    // Allow the navigation to continue for normal routes
    return of(true);
  }
}

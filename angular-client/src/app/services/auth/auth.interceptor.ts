import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(private authService: AuthService, private router: Router) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const token = this.authService.getToken();
    
    // Only add the Authorization header if token exists
    if (token) {
      // Clone the request and add the Authorization header with proper format
      const clonedRequest = request.clone({
        headers: request.headers.set('Authorization', `Bearer ${token}`)
      });
      
      console.log(`Adding token to ${request.url}`);
      return next.handle(clonedRequest).pipe(
        catchError((error: HttpErrorResponse) => {
          console.error('HTTP Error:', error);
          if (error.status === 401) {
            console.log('Authentication error detected, logging out...');
            this.authService.logout();
            this.router.navigate(['/auth']);
          }
          return throwError(() => error);
        })
      );
    }
    
    // Pass through the original request if no token
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        console.error('HTTP Error:', error);
        if (error.status === 401) {
          this.router.navigate(['/auth']);
        }
        return throwError(() => error);
      })
    );
  }
}

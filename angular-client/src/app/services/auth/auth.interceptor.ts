import { Injectable, Injector } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse,
  HttpClient
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;

  constructor(
    private router: Router,
    private injector: Injector
  ) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Tokens are in HttpOnly cookies - browser sends them automatically
    // Just ensure withCredentials is set for API requests
    let modifiedRequest = request;

    // Add withCredentials to API requests (so cookies are sent)
    if (request.url.includes(environment.apiBaseUrl)) {
      modifiedRequest = request.clone({
        withCredentials: true
      });
    }

    return next.handle(modifiedRequest).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // Try to refresh token on 401
          return this.handle401Error(modifiedRequest, next);
        }
        return throwError(() => error);
      })
    );
  }

  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Skip refresh for certain endpoints
    if (request.url.includes('/refresh') || request.url.includes('/login') || request.url.includes('/register')) {
      return throwError(() => new HttpErrorResponse({ status: 401 }));
    }

    if (!this.isRefreshing) {
      this.isRefreshing = true;

      // Lazy inject HttpClient to avoid circular dependency
      const http = this.injector.get(HttpClient);

      // Try to refresh the token
      return http.post(`${environment.authApiUrl}/refresh`, {}, { withCredentials: true }).pipe(
        switchMap(() => {
          this.isRefreshing = false;
          // Retry the original request
          return next.handle(request);
        }),
        catchError((error) => {
          this.isRefreshing = false;
          // Refresh failed - clear auth and redirect
          console.log('Token refresh failed, clearing auth data and redirecting to login...');

          // Clear user data from localStorage (tokens are in httpOnly cookies, cleared by backend)
          localStorage.removeItem('current_user');

          // Redirect to login page
          this.router.navigate(['/auth']);

          return throwError(() => error);
        })
      );
    }

    // If already refreshing, just retry the request
    return next.handle(request);
  }
}

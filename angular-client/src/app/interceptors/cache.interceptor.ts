import { Injectable } from '@angular/core';
import { HttpEvent, HttpInterceptor, HttpHandler, HttpRequest, HttpResponse } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { tap } from 'rxjs/operators';
import { CacheService } from '../services/cache.service';

/**
 * HTTP Caching Interceptor
 * 
 * Caches GET requests to reduce backend calls and improve performance.
 * - Only caches successful GET requests (status 200)
 * - TTL of 3 minutes for cached responses
 * - Automatically bypasses cache for requests with skipCache header
 */
@Injectable()
export class CacheInterceptor implements HttpInterceptor {
  private readonly CACHE_TTL = 3 * 60 * 1000; // 3 minutes

  constructor(private cacheService: CacheService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Only cache GET requests
    if (req.method !== 'GET') {
      return next.handle(req);
    }

    // Check if request should skip cache
    if (req.headers.has('X-Skip-Cache')) {
      return next.handle(req);
    }

    // Generate cache key from URL and params
    const cacheKey = `http:${req.urlWithParams}`;

    // Try to get from cache
    const cached = this.cacheService.get<HttpResponse<any>>(cacheKey);
    if (cached) {
      console.log(`[Cache] Hit: ${req.urlWithParams}`);
      return of(cached);
    }

    // Cache miss - make request and cache response
    console.log(`[Cache] Miss: ${req.urlWithParams}`);
    return next.handle(req).pipe(
      tap(event => {
        if (event instanceof HttpResponse && event.status === 200) {
          // Cache successful responses
          this.cacheService.set(cacheKey, event, this.CACHE_TTL);
        }
      })
    );
  }
}

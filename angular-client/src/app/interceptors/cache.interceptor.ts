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
 * - Auto-invalidates related caches on mutations (POST/PUT/DELETE)
 */
@Injectable()
export class CacheInterceptor implements HttpInterceptor {
  private readonly CACHE_TTL = 3 * 60 * 1000; // 3 minutes

  constructor(private cacheService: CacheService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Handle mutations (POST/PUT/DELETE) - invalidate related caches
    if (req.method !== 'GET') {
      return next.handle(req).pipe(
        tap(event => {
          if (event instanceof HttpResponse && (event.status === 200 || event.status === 201)) {
            // Extract resource path and invalidate related caches
            this.invalidateRelatedCaches(req.url);
          }
        })
      );
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

  /**
   * Invalidate related caches based on mutation URL
   * @param url The URL of the mutation request
   */
  private invalidateRelatedCaches(url: string): void {
    // Extract resource path patterns to invalidate
    const patterns: string[] = [];

    // Course-related endpoints
    if (url.includes('/courses')) {
      patterns.push('/courses');
      patterns.push('/my-courses');
    }

    // Learning/catalog endpoints
    if (url.includes('/learning')) {
      patterns.push('/learning');
    }

    // Subject endpoints
    if (url.includes('/subjects')) {
      patterns.push('/subjects');
    }

    // Topic endpoints
    if (url.includes('/topics')) {
      patterns.push('/topics');
    }

    // Content endpoints
    if (url.includes('/content')) {
      patterns.push('/content');
    }

    // Chapter endpoints
    if (url.includes('/chapters')) {
      patterns.push('/chapters');
    }

    // Statistics endpoints
    if (url.includes('/statistics')) {
      patterns.push('/statistics');
    }

    // Invalidate all matching caches
    patterns.forEach(pattern => {
      this.cacheService.invalidateHttp(pattern);
    });
  }
}

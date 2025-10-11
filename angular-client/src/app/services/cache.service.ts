import { Injectable } from '@angular/core';

/**
 * Cache entry interface with expiration time
 */
interface CacheEntry<T> {
  data: T;
  expiresAt: number;
}

/**
 * LocalStorage cache entry with TTL
 */
interface LocalStorageCacheEntry {
  data: any;
  timestamp: number;
  ttl: number | null;
}

/**
 * Cache service with multiple storage strategies
 * - Memory cache (fast, not persistent)
 * - LocalStorage cache (persistent across sessions)
 */
@Injectable({
  providedIn: 'root'
})
export class CacheService {
  private memoryCache = new Map<string, CacheEntry<any>>();
  private readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly CACHE_PREFIX = 'cw_cache_';

  constructor() {
    console.log('CacheService initialized');
  }

  /**
   * Set value in memory cache with TTL
   * @param key Cache key
   * @param data Data to cache
   * @param ttl Time to live in milliseconds (default 5 minutes)
   */
  set(key: string, data: any, ttl?: number): void {
    const expiresAt = Date.now() + (ttl || this.DEFAULT_TTL);
    this.memoryCache.set(key, { data, expiresAt });
  }

  /**
   * Get value from memory cache
   * @param key Cache key
   * @returns Cached data or null if not found or expired
   */
  get<T>(key: string): T | null {
    const entry = this.memoryCache.get(key);

    if (!entry) {
      return null;
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.memoryCache.delete(key);
      return null;
    }

    return entry.data as T;
  }

  /**
   * Delete key from memory cache
   * @param key Cache key
   */
  delete(key: string): void {
    this.memoryCache.delete(key);
  }

  /**
   * Invalidate keys matching pattern
   * @param pattern Pattern to match (e.g., 'courses:', 'user:123:')
   */
  invalidate(pattern: string): void {
    const keys = Array.from(this.memoryCache.keys());
    keys.forEach(key => {
      if (key.startsWith(pattern)) {
        this.memoryCache.delete(key);
      }
    });
  }

  /**
   * Invalidate HTTP cache keys matching URL pattern
   * @param urlPattern URL pattern to match (e.g., '/courses', '/learning')
   * @returns Number of cache entries invalidated
   */
  invalidateHttp(urlPattern: string): number {
    const keys = Array.from(this.memoryCache.keys());
    let invalidatedCount = 0;

    keys.forEach(key => {
      // HTTP cache keys are in format: http:{url}
      if (key.startsWith('http:') && key.includes(urlPattern)) {
        this.memoryCache.delete(key);
        invalidatedCount++;
      }
    });

    console.log(`[Cache] Invalidated ${invalidatedCount} HTTP cache entries matching: ${urlPattern}`);
    return invalidatedCount;
  }

  /**
   * Clear all memory cache
   */
  clear(): void {
    this.memoryCache.clear();
  }

  /**
   * Set value in LocalStorage with TTL
   * @param key Cache key
   * @param data Data to cache
   * @param ttlMinutes Time to live in minutes (null = no expiration)
   */
  setLocal(key: string, data: any, ttlMinutes?: number): void {
    const cacheKey = this.CACHE_PREFIX + key;
    const entry: LocalStorageCacheEntry = {
      data,
      timestamp: Date.now(),
      ttl: ttlMinutes ? ttlMinutes * 60 * 1000 : null
    };

    try {
      localStorage.setItem(cacheKey, JSON.stringify(entry));
    } catch (e) {
      // Handle quota exceeded - clear oldest 25% of entries
      console.warn('LocalStorage quota exceeded, clearing old entries');
      this.clearOldestLocalEntries();
      try {
        localStorage.setItem(cacheKey, JSON.stringify(entry));
      } catch (e2) {
        console.error('Failed to cache in localStorage after cleanup:', e2);
      }
    }
  }

  /**
   * Get value from LocalStorage
   * @param key Cache key
   * @returns Cached data or null if not found or expired
   */
  getLocal<T>(key: string): T | null {
    const cacheKey = this.CACHE_PREFIX + key;
    const item = localStorage.getItem(cacheKey);

    if (!item) {
      return null;
    }

    try {
      const entry: LocalStorageCacheEntry = JSON.parse(item);

      // Check TTL
      if (entry.ttl && Date.now() - entry.timestamp > entry.ttl) {
        localStorage.removeItem(cacheKey);
        return null;
      }

      return entry.data as T;
    } catch (e) {
      console.error('Error parsing localStorage cache:', e);
      return null;
    }
  }

  /**
   * Delete key from LocalStorage
   * @param key Cache key
   */
  deleteLocal(key: string): void {
    const cacheKey = this.CACHE_PREFIX + key;
    localStorage.removeItem(cacheKey);
  }

  /**
   * Clear oldest 25% of LocalStorage cache entries
   */
  private clearOldestLocalEntries(): void {
    const cacheEntries: Array<[string, LocalStorageCacheEntry]> = [];

    // Collect all cache entries
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.CACHE_PREFIX)) {
        const value = localStorage.getItem(key);
        if (value) {
          try {
            cacheEntries.push([key, JSON.parse(value)]);
          } catch { }
        }
      }
    }

    // Sort by timestamp and remove oldest 25%
    cacheEntries.sort((a, b) => a[1].timestamp - b[1].timestamp);
    const toRemove = Math.ceil(cacheEntries.length * 0.25);

    for (let i = 0; i < toRemove; i++) {
      localStorage.removeItem(cacheEntries[i][0]);
    }
  }

  /**
   * Get size of memory cache
   */
  getMemoryCacheSize(): number {
    return this.memoryCache.size;
  }

  /**
   * Get stats about cache usage
   */
  getCacheStats(): { memorySize: number, localStorageKeys: number } {
    let localStorageKeys = 0;
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(this.CACHE_PREFIX)) {
        localStorageKeys++;
      }
    }

    return {
      memorySize: this.memoryCache.size,
      localStorageKeys
    };
  }
}

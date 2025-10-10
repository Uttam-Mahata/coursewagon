import { TestBed } from '@angular/core/testing';
import { CacheService } from './cache.service';

describe('CacheService', () => {
  let service: CacheService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CacheService);
    
    // Clear cache before each test
    service.clear();
    localStorage.clear();
  });

  afterEach(() => {
    // Clean up after each test
    service.clear();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('Memory Cache', () => {
    it('should set and get values from memory cache', () => {
      service.set('test_key', 'test_value');
      const result = service.get('test_key');
      expect(result).toBe('test_value');
    });

    it('should return null for non-existent keys', () => {
      const result = service.get('nonexistent');
      expect(result).toBeNull();
    });

    it('should delete values from memory cache', () => {
      service.set('delete_key', 'delete_value');
      expect(service.get('delete_key')).toBe('delete_value');
      
      service.delete('delete_key');
      expect(service.get('delete_key')).toBeNull();
    });

    it('should handle complex objects in memory cache', () => {
      const complexData = {
        id: 1,
        name: 'Test',
        items: [1, 2, 3],
        nested: { value: 'nested' }
      };
      
      service.set('complex', complexData);
      const result = service.get('complex');
      expect(result).toEqual(complexData);
    });

    it('should expire values based on TTL', (done) => {
      // Set with 1 second TTL
      service.set('expiring', 'value', 1000);
      expect(service.get('expiring')).toBe('value');
      
      // Wait 1.5 seconds and check if expired
      setTimeout(() => {
        expect(service.get('expiring')).toBeNull();
        done();
      }, 1500);
    });

    it('should invalidate keys matching pattern', () => {
      service.set('user:1:profile', { name: 'User 1' });
      service.set('user:1:settings', { theme: 'dark' });
      service.set('user:2:profile', { name: 'User 2' });
      service.set('course:1', { name: 'Course 1' });
      
      service.invalidate('user:1:');
      
      expect(service.get('user:1:profile')).toBeNull();
      expect(service.get('user:1:settings')).toBeNull();
      expect(service.get('user:2:profile')).not.toBeNull();
      expect(service.get('course:1')).not.toBeNull();
    });

    it('should clear all memory cache', () => {
      service.set('key1', 'value1');
      service.set('key2', 'value2');
      service.set('key3', 'value3');
      
      expect(service.getMemoryCacheSize()).toBe(3);
      
      service.clear();
      
      expect(service.getMemoryCacheSize()).toBe(0);
      expect(service.get('key1')).toBeNull();
    });
  });

  describe('LocalStorage Cache', () => {
    it('should set and get values from localStorage', () => {
      service.setLocal('test_key', 'test_value');
      const result = service.getLocal('test_key');
      expect(result).toBe('test_value');
    });

    it('should handle complex objects in localStorage', () => {
      const complexData = {
        id: 1,
        name: 'Test',
        items: [1, 2, 3]
      };
      
      service.setLocal('complex', complexData);
      const result = service.getLocal('complex');
      expect(result).toEqual(complexData);
    });

    it('should delete values from localStorage', () => {
      service.setLocal('delete_key', 'delete_value');
      expect(service.getLocal('delete_key')).toBe('delete_value');
      
      service.deleteLocal('delete_key');
      expect(service.getLocal('delete_key')).toBeNull();
    });

    it('should expire localStorage values based on TTL', (done) => {
      // Set with 0.05 minute TTL (3 seconds)
      service.setLocal('expiring', 'value', 0.05);
      expect(service.getLocal('expiring')).toBe('value');
      
      // Wait 4 seconds and check if expired
      setTimeout(() => {
        expect(service.getLocal('expiring')).toBeNull();
        done();
      }, 4000);
    });

    it('should handle localStorage without TTL', () => {
      service.setLocal('persistent', 'value');
      const result = service.getLocal('persistent');
      expect(result).toBe('value');
    });
  });

  describe('Cache Stats', () => {
    it('should return correct cache stats', () => {
      service.set('mem1', 'value1');
      service.set('mem2', 'value2');
      service.setLocal('local1', 'value1');
      service.setLocal('local2', 'value2');
      
      const stats = service.getCacheStats();
      expect(stats.memorySize).toBe(2);
      expect(stats.localStorageKeys).toBeGreaterThanOrEqual(2);
    });
  });
});

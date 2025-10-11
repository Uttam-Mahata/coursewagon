import { Injectable, signal, effect } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  // Signal to track dark mode state
  private darkModeSignal = signal<boolean>(false);

  // Public readonly signal
  readonly isDarkMode = this.darkModeSignal.asReadonly();

  constructor() {
    // Load theme preference from localStorage on init
    this.loadThemePreference();

    // Effect to apply theme class to document and save to localStorage
    effect(() => {
      const isDark = this.darkModeSignal();
      this.applyTheme(isDark);
    });
  }

  /**
   * Toggle between light and dark mode
   */
  toggleTheme(): void {
    this.darkModeSignal.set(!this.darkModeSignal());
  }

  /**
   * Set theme explicitly
   */
  setTheme(isDark: boolean): void {
    this.darkModeSignal.set(isDark);
  }

  /**
   * Load theme preference from localStorage or system preference
   */
  private loadThemePreference(): void {
    // Check localStorage first
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme) {
      this.darkModeSignal.set(savedTheme === 'dark');
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.darkModeSignal.set(prefersDark);
    }
  }

  /**
   * Apply theme to document and save to localStorage
   */
  private applyTheme(isDark: boolean): void {
    const htmlElement = document.documentElement;

    if (isDark) {
      htmlElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      htmlElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }
}

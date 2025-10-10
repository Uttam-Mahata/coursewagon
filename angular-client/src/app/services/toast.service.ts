import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  private toastSubject = new Subject<Toast>();
  public toasts$ = this.toastSubject.asObservable();
  private toastIdCounter = 0;

  constructor() { }

  /**
   * Show a success toast message
   */
  success(message: string, duration: number = 3000): void {
    this.show(message, 'success', duration);
  }

  /**
   * Show an error toast message
   */
  error(message: string, duration: number = 4000): void {
    this.show(message, 'error', duration);
  }

  /**
   * Show an info toast message
   */
  info(message: string, duration: number = 3000): void {
    this.show(message, 'info', duration);
  }

  /**
   * Show a warning toast message
   */
  warning(message: string, duration: number = 3000): void {
    this.show(message, 'warning', duration);
  }

  /**
   * Show a toast message
   */
  private show(message: string, type: 'success' | 'error' | 'info' | 'warning', duration: number): void {
    const toast: Toast = {
      id: ++this.toastIdCounter,
      message,
      type,
      duration
    };
    this.toastSubject.next(toast);
  }
}

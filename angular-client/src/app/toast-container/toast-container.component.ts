import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  faCheckCircle, faExclamationCircle, faInfoCircle,
  faExclamationTriangle, faTimes
} from '@fortawesome/free-solid-svg-icons';
import { ToastService, Toast } from '../services/toast.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-toast-container',
  standalone: true,
  imports: [CommonModule, FontAwesomeModule],
  templateUrl: './toast-container.component.html',
  styleUrl: './toast-container.component.css'
})
export class ToastContainerComponent implements OnInit, OnDestroy {
  // Icons
  faCheckCircle = faCheckCircle;
  faExclamationCircle = faExclamationCircle;
  faInfoCircle = faInfoCircle;
  faExclamationTriangle = faExclamationTriangle;
  faTimes = faTimes;

  toasts: Toast[] = [];
  private subscription?: Subscription;

  constructor(private toastService: ToastService) { }

  ngOnInit(): void {
    this.subscription = this.toastService.toasts$.subscribe(toast => {
      this.toasts.push(toast);

      // Auto-dismiss after duration
      if (toast.duration) {
        setTimeout(() => {
          this.removeToast(toast.id);
        }, toast.duration);
      }
    });
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  removeToast(id: number): void {
    this.toasts = this.toasts.filter(toast => toast.id !== id);
  }

  getIcon(type: string) {
    switch (type) {
      case 'success':
        return this.faCheckCircle;
      case 'error':
        return this.faExclamationCircle;
      case 'warning':
        return this.faExclamationTriangle;
      case 'info':
      default:
        return this.faInfoCircle;
    }
  }

  getToastClasses(type: string): string {
    const baseClasses = 'flex items-center w-full max-w-md p-4 mb-4 rounded-lg shadow-lg transition-all duration-300 ease-in-out';
    switch (type) {
      case 'success':
        return `${baseClasses} bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300 border-l-4 border-green-500 dark:border-green-400`;
      case 'error':
        return `${baseClasses} bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300 border-l-4 border-red-500 dark:border-red-400`;
      case 'warning':
        return `${baseClasses} bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300 border-l-4 border-yellow-500 dark:border-yellow-400`;
      case 'info':
      default:
        return `${baseClasses} bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 border-l-4 border-blue-500 dark:border-blue-400`;
    }
  }

  getIconClasses(type: string): string {
    switch (type) {
      case 'success':
        return 'text-green-500 dark:text-green-400';
      case 'error':
        return 'text-red-500 dark:text-red-400';
      case 'warning':
        return 'text-yellow-500 dark:text-yellow-400';
      case 'info':
      default:
        return 'text-blue-500 dark:text-blue-400';
    }
  }
}

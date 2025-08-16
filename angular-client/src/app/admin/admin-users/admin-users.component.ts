import { Component, Input, Output, EventEmitter } from '@angular/core';
import { faUserShield, faUserSlash } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-admin-users',
  standalone: false,
  templateUrl: './admin-users.component.html',
  styleUrls: ['./admin-users.component.css']
})
export class AdminUsersComponent {
  @Input() users: any[] = [];
  @Input() loading: boolean = false;
  @Input() error: string = '';
  @Output() toggleUserStatus = new EventEmitter<{userId: number, isActive: boolean}>();
  @Output() toggleAdminStatus = new EventEmitter<{userId: number, isAdmin: boolean}>();
  @Output() retryLoad = new EventEmitter<void>();

  // FontAwesome icons
  faUserShield = faUserShield;
  faUserSlash = faUserSlash;

  constructor() { }

  onToggleUserStatus(userId: number, isActive: boolean) {
    this.toggleUserStatus.emit({ userId, isActive });
  }

  onToggleAdminStatus(userId: number, isAdmin: boolean) {
    this.toggleAdminStatus.emit({ userId, isAdmin });
  }

  onRetryLoad() {
    this.retryLoad.emit();
  }
}

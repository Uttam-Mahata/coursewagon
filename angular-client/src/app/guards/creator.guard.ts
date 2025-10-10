import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';

export const creatorGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const user = authService.getCurrentUser();

  if (!user) {
    router.navigate(['/auth'], { queryParams: { returnUrl: state.url } });
    return false;
  }

  if (authService.isCreator()) {
    return true;
  }

  // User is not a creator
  console.warn('Access denied: User is not a creator');
  router.navigate(['/home']);
  return false;
};

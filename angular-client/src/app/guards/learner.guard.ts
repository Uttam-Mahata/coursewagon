import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';

export const learnerGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const user = authService.getCurrentUser();

  if (!user) {
    router.navigate(['/auth'], { queryParams: { returnUrl: state.url } });
    return false;
  }

  if (authService.isLearner()) {
    return true;
  }

  // User is not a learner
  console.warn('Access denied: User is not a learner');
  router.navigate(['/home']);
  return false;
};

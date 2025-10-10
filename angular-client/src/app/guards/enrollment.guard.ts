import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';
import { EnrollmentService } from '../services/enrollment.service';
import { map, catchError } from 'rxjs/operators';
import { of } from 'rxjs';

export const enrollmentGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const enrollmentService = inject(EnrollmentService);
  const router = inject(Router);

  const user = authService.getCurrentUser();

  // First check if user is authenticated
  if (!user) {
    router.navigate(['/auth'], { queryParams: { returnUrl: state.url } });
    return false;
  }

  // Extract course_id from route parameters
  const courseId = route.paramMap.get('course_id') || route.paramMap.get('id');

  if (!courseId) {
    console.error('Enrollment guard: No course_id found in route parameters');
    router.navigate(['/home']);
    return false;
  }

  // Check enrollment status
  return enrollmentService.checkEnrollment(parseInt(courseId)).pipe(
    map(enrollmentCheck => {
      if (enrollmentCheck.enrolled) {
        return true;
      } else {
        // Not enrolled - redirect to course preview
        console.warn(`Access denied: User is not enrolled in course ${courseId}`);
        router.navigate(['/courses/preview', courseId]);
        return false;
      }
    }),
    catchError(error => {
      console.error('Enrollment check error:', error);
      router.navigate(['/courses/preview', courseId]);
      return of(false);
    })
  );
};

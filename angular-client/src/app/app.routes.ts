import { Routes } from '@angular/router';
import { CourseComponent } from './course/course.component';
import { CoursesComponent } from './courses/courses.component';
import { HomeComponent } from './home/home.component';
import { AuthComponent } from './auth/auth.component';
import { AuthGuard, NonAuthGuard, AdminGuard } from './services/auth/auth.guard';
import { ProfileComponent } from './profile/profile.component';
import { SubjectsChaptersComponent } from './subjects-chapters/subjects-chapters.component';
import { TopicsContentComponent } from './topics-content/topics-content.component';
import { CourseContentComponent } from './course-content/course-content.component';
import { SubjectsComponent } from './subjects/subjects.component';
import { RouteRedirectResolver } from './route-redirect.resolver';
import { TermsComponent } from './terms/terms.component';
import { PrivacyPolicyComponent } from './privacy-policy/privacy-policy.component';
import { ComingSoonComponent } from './coming-soon/coming-soon.component';
import { WriteReviewComponent } from './write-review/write-review.component';
import { AdminComponent } from './admin/admin.component';
import { ForgotPasswordComponent } from './forgot-password/forgot-password.component';
import { ResetPasswordComponent } from './reset-password/reset-password.component';
import { HowItWorksComponent } from './how-it-works/how-it-works.component';
import { HelpCenterComponent } from './help-center/help-center.component';
import { EmailVerificationComponent } from './email-verification/email-verification.component';
import { MyCoursesDashboardComponent } from './my-courses-dashboard/my-courses-dashboard.component';
import { LearnerDashboardComponent } from './learner-dashboard/learner-dashboard.component';
import { CourseCatalogComponent } from './course-catalog/course-catalog.component';
import { CoursePreviewComponent } from './course-preview/course-preview.component';
import { LearningViewComponent } from './learning-view/learning-view.component';
import { learnerGuard } from './guards/learner.guard';
import { creatorGuard } from './guards/creator.guard';
import { enrollmentGuard } from './guards/enrollment.guard';

export const routes: Routes = [
  { path: 'home', component: HomeComponent },
  { path: 'auth', component: AuthComponent, canActivate: [NonAuthGuard] },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  { path: 'verify-email', component: EmailVerificationComponent },
  { path: 'profile', component: ProfileComponent, canActivate: [AuthGuard] },

  // Creator Routes (protected by creatorGuard)
  { path: 'create-course', component: CourseComponent, canActivate: [creatorGuard] },
  { path: 'courses', component: CoursesComponent, canActivate: [creatorGuard] },
  { path: 'my-courses-dashboard', component: MyCoursesDashboardComponent, canActivate: [creatorGuard] },

  // Learner Routes (protected by learnerGuard)
  { path: 'learner/dashboard', component: LearnerDashboardComponent, canActivate: [learnerGuard] },
  { path: 'courses/browse', component: CourseCatalogComponent },
  { path: 'courses/preview/:id', component: CoursePreviewComponent },
  { path: 'learn/:course_id', component: LearningViewComponent, canActivate: [enrollmentGuard] },

  // Admin Routes
  { path: 'admin', component: AdminComponent, canActivate: [AdminGuard] },

  // Legal pages - accessible without authentication
  { path: 'terms', component: TermsComponent },
  { path: 'privacy-policy', component: PrivacyPolicyComponent },
  { path: 'coming-soon', component: ComingSoonComponent },
  { path: 'how-it-works', component: HowItWorksComponent },
  { path: 'help-center', component: HelpCenterComponent },
  
  // Creator Course Management Routes
  {
    path: 'courses/:course_id/subjects',
    component: SubjectsComponent,
    canActivate: [creatorGuard]
  },

  {
    path:'write-review',
    component: WriteReviewComponent,
    canActivate: [AuthGuard]
  },

  // Legacy route - keep for compatibility
  {
    path: 'courses/:course_id/subjects-chapters',
    component: SubjectsChaptersComponent,
    canActivate: [creatorGuard]
  },

  // Course content routes (for creators)
  {
    path: 'courses/:course_id/subjects/:subject_id/content',
    component: CourseContentComponent,
    canActivate: [creatorGuard]
  },
  {
    path: 'courses/:course_id/subjects/:subject_id/content/:topic_id',
    component: CourseContentComponent,
    canActivate: [creatorGuard]
  },

  // Legacy routes - using resolver to handle redirects
  {
    path: 'courses/:course_id/subjects/:subject_id/chapters/:chapter_id/topics',
    resolve: { redirect: RouteRedirectResolver },
    component: SubjectsChaptersComponent,
    canActivate: [creatorGuard]
  },
  {
    path: 'courses/:course_id/subjects/:subject_id/chapters/:chapter_id/topics/:topic_id/content',
    resolve: { redirect: RouteRedirectResolver },
    component: TopicsContentComponent,
    canActivate: [creatorGuard]
  },
  
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: '**', redirectTo: '/home' } // Handle unknown routes
];
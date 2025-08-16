import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';
import { CourseComponent } from './course/course.component';
import { CoursesComponent } from './courses/courses.component';
import { HomeComponent } from './home/home.component';
import { AppRoutingModule } from './app-routing.module';
import { CourseService } from './services/course.service';
import { MathRendererService } from './services/math-renderer.service';
import { MarkdownModule } from 'ngx-markdown';
import { FooterComponent } from './footer/footer.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { AuthComponent } from './auth/auth.component';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { MermaidViewComponent } from './mermaid-view/mermaid-view.component';
import { AuthInterceptor } from './services/auth/auth.interceptor';
import { AuthGuard } from './services/auth/auth.guard';
import { ProfileComponent } from './profile/profile.component';
import { SubjectsChaptersComponent } from './subjects-chapters/subjects-chapters.component';
import { TopicsContentComponent } from './topics-content/topics-content.component';
import { SharedMarkdownModule } from './shared/markdown.module';
import { SubjectsComponent } from './subjects/subjects.component';
import { CourseContentComponent } from './course-content/course-content.component';
import { FilterByIdPipe } from './pipes/filter-by-id.pipe';
import { TermsComponent } from './terms/terms.component';
import { PrivacyPolicyComponent } from './privacy-policy/privacy-policy.component';
import { ComingSoonComponent } from './coming-soon/coming-soon.component';
import { TestimonialsComponent } from './testimonials/testimonials.component';
import { WriteReviewComponent } from './write-review/write-review.component';
import { AdminComponent } from './admin/admin.component';

// Import new admin sub-components
import { AdminDashboardComponent } from './admin/admin-dashboard/admin-dashboard.component';
import { AdminUsersComponent } from './admin/admin-users/admin-users.component';
import { AdminTestimonialsComponent } from './admin/admin-testimonials/admin-testimonials.component';
import { ForgotPasswordComponent } from './forgot-password/forgot-password.component';
import { ResetPasswordComponent } from './reset-password/reset-password.component';

@NgModule({
  declarations: [
    AppComponent,
    CourseComponent,
    CoursesComponent,
    FooterComponent,
    AuthComponent,
    MermaidViewComponent,
    ProfileComponent,
    HomeComponent,
    SubjectsChaptersComponent,
    TopicsContentComponent,
    SubjectsComponent,
    CourseContentComponent,
    FilterByIdPipe,
    TermsComponent,
    PrivacyPolicyComponent,
    ComingSoonComponent,
    TestimonialsComponent,
    WriteReviewComponent,
    AdminComponent,
    // Admin sub-components
    AdminDashboardComponent,
    AdminUsersComponent,
    AdminTestimonialsComponent,
    ForgotPasswordComponent,
    ResetPasswordComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,  // Add ReactiveFormsModule
    AppRoutingModule,
    FontAwesomeModule,
    MarkdownModule.forRoot(),
    SharedMarkdownModule,
    RouterModule
  ],
  providers: [
    CourseService,
    MathRendererService,
    provideAnimationsAsync(),
    AuthGuard,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }


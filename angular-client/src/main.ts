import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { CourseService } from './app/services/course.service';
import { MathRendererService } from './app/services/math-renderer.service';
import { AuthGuard } from './app/services/auth/auth.guard';
import { AuthInterceptor } from './app/services/auth/auth.interceptor';
import { CacheInterceptor } from './app/interceptors/cache.interceptor';
import { routes } from './app/app.routes';
import { provideMarkdown, MARKED_OPTIONS } from 'ngx-markdown';
import { SecurityContext } from '@angular/core';

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptorsFromDi()),
    provideAnimationsAsync(),
    CourseService,
    MathRendererService,
    AuthGuard,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: CacheInterceptor,
      multi: true
    },
    provideMarkdown({
      sanitize: SecurityContext.NONE,
      markedOptions: {
        provide: MARKED_OPTIONS,
        useValue: {
          gfm: true,
          breaks: true,
          pedantic: false,
        },
      },
    }),
  ],
}).catch(err => console.error(err));

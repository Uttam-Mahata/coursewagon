import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MarkdownModule, MARKED_OPTIONS } from 'ngx-markdown';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { SecurityContext } from '@angular/core';

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    HttpClientModule,
    MarkdownModule.forRoot({
      loader: HttpClient,
      sanitize: SecurityContext.NONE, // Be careful with this setting in production
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
  exports: [
    MarkdownModule
  ]
})
export class SharedMarkdownModule { }

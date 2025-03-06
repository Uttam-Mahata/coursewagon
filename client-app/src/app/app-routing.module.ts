import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CourseComponent } from './course/course.component';
import { CoursesComponent } from './courses/courses.component';
import { TopicsComponent } from './topics/topics.component';

import { ContentComponent } from './content/content.component';
import { HomeComponent } from './home/home.component';
import { SubjectsModulesComponent } from './subjects-modules/subjects-modules.component';
import { ChaptersTopicsComponent } from './chapters-topics/chapters-topics.component';
import { SubtopicsContentComponent } from './subtopics-content/subtopics-content.component';
import { AuthComponent } from './auth/auth.component';
import { AuthGuard } from './auth.guard';

const routes: Routes = [
  {path: 'home', component: HomeComponent},
  {path: 'auth', component: AuthComponent},
 
  {path: 'create-course', component: CourseComponent, canActivate: [AuthGuard]},
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'courses', component: CoursesComponent, canActivate: [AuthGuard] },
  { path: 'courses/:course_id/subjects-modules', component: SubjectsModulesComponent, canActivate: [AuthGuard] },

  { path: 'courses/:course_id/subjects/:subject_id/modules/:module_id/chapters-topics', component: ChaptersTopicsComponent, canActivate: [AuthGuard] },
  { path: 'courses/:course_id/subjects/:subject_id/modules/:module_id/chapters/:chapter_id/topics', component: TopicsComponent, canActivate: [AuthGuard] },
  { path: 'courses/:course_id/subjects/:subject_id/modules/:module_id/chapters/:chapter_id/topics/:topic_id/subtopics-content', component: SubtopicsContentComponent, canActivate: [AuthGuard] },
  { path: 'courses/:course_id/subjects/:subject_id/modules/:module_id/chapters/:chapter_id/topics/:topic_id/subtopics/:subtopic_id/content', component: ContentComponent, canActivate: [AuthGuard] }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

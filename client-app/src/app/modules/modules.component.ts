import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-modules',
  templateUrl: './modules.component.html'
})
export class ModulesComponent implements OnInit {
  modules: any[] = [];
  courseId: number;
  subjectId: number;

  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // Extract courseId and subjectId from route params
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
    this.subjectId = +this.route.snapshot.paramMap.get('subject_id')!;
  }

  ngOnInit() {
    // Fetch modules for the given subject
    this.courseService.getModules(this.courseId, this.subjectId).subscribe((modules: any[]) => {
      this.modules = modules;
    });
  }

  generateChapters(moduleId: number) {
    // Trigger chapter generation for a module
    this.courseService.generateChapters(this.courseId, this.subjectId, moduleId).subscribe(() => {
      // Optionally, you can reload the modules or show a success message
    });
  }

  viewChapters(moduleId: number) {
    // Navigate to chapters page for the selected module
    this.router.navigate([`/courses/${this.courseId}/subjects/${this.subjectId}/modules/${moduleId}/chapters`]);
  }
}

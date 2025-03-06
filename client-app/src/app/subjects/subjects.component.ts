import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-subjects',
  templateUrl: './subjects.component.html'
})
export class SubjectsComponent implements OnInit {
  subjects: any[] = [];
  courseId: number;

  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // Extract courseId from route params
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
  }

  ngOnInit() {
    // Fetch subjects for the given course
    this.courseService.getSubjects(this.courseId).subscribe((subjects: any[]) => {
      this.subjects = subjects;
    });
  }

  generateModules(subjectId: number) {
    // Trigger module generation for a subject
    this.courseService.generateModules(this.courseId, subjectId).subscribe(() => {
      // Optionally, you can reload the subject modules or show a success message
    });
  }

  viewModules(subjectId: number) {
    // Navigate to modules page for the selected subject
    this.router.navigate([`/courses/${this.courseId}/subjects/${subjectId}/modules`]);
  }
}

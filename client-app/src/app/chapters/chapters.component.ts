import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-chapters',
  templateUrl: './chapters.component.html'
})
export class ChaptersComponent implements OnInit {
  chapters: any[] = [];
  courseId: number;
  subjectId: number;
  moduleId: number;

  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // Extract courseId, subjectId, and moduleId from route params
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
    this.subjectId = +this.route.snapshot.paramMap.get('subject_id')!;
    this.moduleId = +this.route.snapshot.paramMap.get('module_id')!;
  }

  ngOnInit() {
    // Fetch chapters for the given module
    this.courseService.getChapters(this.courseId, this.subjectId, this.moduleId).subscribe((chapters: any[]) => {
      this.chapters = chapters;
    });
  }

  generateTopics(chapterId: number) {
    // Trigger topic generation for a chapter
    this.courseService.generateTopics(this.courseId, this.subjectId, this.moduleId, chapterId).subscribe(() => {
      // Optionally, you can reload the chapters or show a success message
    });
  }

  viewTopics(chapterId: number) {
    // Navigate to topics page for the selected chapter
    this.router.navigate([`/courses/${this.courseId}/subjects/${this.subjectId}/modules/${this.moduleId}/chapters/${chapterId}/topics`]);
  }
}

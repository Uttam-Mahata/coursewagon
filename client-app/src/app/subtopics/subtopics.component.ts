import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-subtopics',
  templateUrl: './subtopics.component.html'
})
export class SubtopicsComponent implements OnInit {
  subtopics: any[] = [];
  courseId: number;
  subjectId: number;
  moduleId: number;
  chapterId: number;
  topicId: number;

  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // Extract courseId, subjectId, moduleId, chapterId, and topicId from route params
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
    this.subjectId = +this.route.snapshot.paramMap.get('subject_id')!;
    this.moduleId = +this.route.snapshot.paramMap.get('module_id')!;
    this.chapterId = +this.route.snapshot.paramMap.get('chapter_id')!;
    this.topicId = +this.route.snapshot.paramMap.get('topic_id')!;
  }

  ngOnInit() {
    // Fetch subtopics for the given topic
    this.courseService.getSubtopics(this.courseId, this.subjectId, this.moduleId, this.chapterId, this.topicId).subscribe((subtopics: any[]) => {
      this.subtopics = subtopics;
    });
  }

  generateContent(subtopicId: number) {
    // Trigger content generation for a subtopic
    this.courseService.generateContent(this.courseId, this.subjectId, this.moduleId, this.chapterId, this.topicId, subtopicId).subscribe(() => {
      // Optionally, you can reload the subtopics or show a success message
    });
  }

  viewContent(subtopicId: number) {
    // Navigate to content page for the selected subtopic
    this.router.navigate([`/courses/${this.courseId}/subjects/${this.subjectId}/modules/${this.moduleId}/chapters/${this.chapterId}/topics/${this.topicId}/subtopics/${subtopicId}/content`]);
  }
}

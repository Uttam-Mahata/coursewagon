import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-topics',
  templateUrl: './topics.component.html'
})
export class TopicsComponent implements OnInit {
  topics: any[] = [];
  courseId: number;
  subjectId: number;
  moduleId: number;
  chapterId: number;

  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // Extract courseId, subjectId, moduleId, and chapterId from route params
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
    this.subjectId = +this.route.snapshot.paramMap.get('subject_id')!;
    this.moduleId = +this.route.snapshot.paramMap.get('module_id')!;
    this.chapterId = +this.route.snapshot.paramMap.get('chapter_id')!;
  }

  ngOnInit() {
    // Fetch topics for the given chapter
    this.courseService.getTopics(this.courseId, this.subjectId, this.moduleId, this.chapterId).subscribe((topics: any[]) => {
      this.topics = topics;
    });
  }

  generateSubtopics(topicId: number) {
    // Trigger subtopic generation for a topic
    this.courseService.generateSubtopics(this.courseId, this.subjectId, this.moduleId, this.chapterId, topicId).subscribe(() => {
      // Optionally, you can reload the topics or show a success message
    });
  }

  viewSubtopics(topicId: number) {
    // Navigate to subtopics page for the selected topic
    this.router.navigate([`/courses/${this.courseId}/subjects/${this.subjectId}/modules/${this.moduleId}/chapters/${this.chapterId}/topics/${topicId}/subtopics`]);
  }
}

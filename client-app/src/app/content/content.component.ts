import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-content',
  templateUrl: './content.component.html'
})
export class ContentComponent implements OnInit {
  content: any;
  courseId!: number;
  subjectId!: number;
  moduleId!: number;
  chapterId!: number;
  topicId!: number;
  subtopicId!: number;

  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
    this.subjectId = +this.route.snapshot.paramMap.get('subject_id')!;
    this.moduleId = +this.route.snapshot.paramMap.get('module_id')!;
    this.chapterId = +this.route.snapshot.paramMap.get('chapter_id')!;
    this.topicId = +this.route.snapshot.paramMap.get('topic_id')!;
    this.subtopicId = +this.route.snapshot.paramMap.get('subtopic_id')!;

    // Log the parameters to ensure they are being passed correctly
    console.log('courseId:', this.courseId);
    console.log('subjectId:', this.subjectId);
    console.log('moduleId:', this.moduleId);
    console.log('chapterId:', this.chapterId);
    console.log('topicId:', this.topicId);
    console.log('subtopicId:', this.subtopicId);

    // Fetch content and handle errors
    this.courseService.getContent(this.courseId, this.subjectId, this.moduleId, this.chapterId, this.topicId, this.subtopicId).subscribe(
      (content: any) => {
        this.content = content;
        console.log('Fetched content:', content); // Log content for debugging
      },
      (error) => {
        console.error('Error fetching content:', error);
      }
    );
  }
}

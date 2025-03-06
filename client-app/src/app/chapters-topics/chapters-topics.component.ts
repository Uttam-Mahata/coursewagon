import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-chapters-topics',
  templateUrl: './chapters-topics.component.html',
  styleUrls: ['./chapters-topics.component.css']
})
export class ChaptersTopicsComponent implements OnInit {
  chapters: any[] = [];
  topics: any[] = [];
  courseId: number;
  courseName: string = '';
  subjectId: number;
  moduleId: number;
  moduleName: string = '';
  selectedChapterId: number | null = null;
  selectedChapterName: string | null = null;

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
    this.courseService.getCourseDetails(this.courseId).subscribe((courses: any) => {
      this.courseName = courses.name;
    });

    this.courseService.getModuleDetails(this.courseId, this.subjectId, this.moduleId).subscribe((module: any) => {
      this.moduleName = module.name;
    });
  }

  viewTopics(chapterId: number) {
    this.selectedChapterId = chapterId;
    this.selectedChapterName = this.chapters.find(chapter => chapter.id === chapterId)?.name || null;
    // Fetch topics for the selected chapter
    this.courseService.getTopics(this.courseId, this.subjectId, this.moduleId, chapterId).subscribe((topics: any[]) => {
      this.topics = topics;
    });
  }

  generateTopics(chapterId: number) {
    // Trigger topic generation for a chapter
    this.courseService.generateTopics(this.courseId, this.subjectId, this.moduleId, chapterId).subscribe(() => {
      this.viewTopics(chapterId);  // Reload topics after generation
    });
  }

  generateSubtopics(topicId: number) {
    // Trigger subtopic generation for a topic
    this.courseService.generateSubtopics(this.courseId, this.subjectId, this.moduleId, this.selectedChapterId!, topicId).subscribe(() => {
      // Optionally, refresh topics or show a message
      // Show a message
      alert('Subtopics generated successfully!');

      // Reload topics after generation
      this.viewTopics(this.selectedChapterId!);
    });
  }

  viewSubtopics(topicId: number) {
    // Navigate to subtopics page for the selected topic
    this.router.navigate([`/courses/${this.courseId}/subjects/${this.subjectId}/modules/${this.moduleId}/chapters/${this.selectedChapterId}/topics/${topicId}/subtopics-content`]);
  }
}

// Import necessary modules and libraries
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-subtopics-content',
  templateUrl: './subtopics-content.component.html'
})
export class SubtopicsContentComponent implements OnInit {
  subtopics: any[] = [];
  content: any = null;
  courseId: number;
  subjectId: number;
  moduleId: number;
  chapterId: number;
  topicId: number;
  showSubtopics: boolean = true; 
  courseName: string = '';
  moduleName: string = '';
  topicName: string = '';

  selectedSubtopicId: number | null = null;
  selectedSubtopicName: string | null = null;

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

    this.courseService.getCourseDetails(this.courseId).subscribe((courses: any) => {
      this.courseName = courses.name;
    }); 

    this.courseService.getModuleDetails(this.courseId, this.subjectId, this.moduleId).subscribe((module: any) => {
      this.moduleName = module.name;
    });

    this.courseService.getTopicDetails(this.courseId, this.subjectId, this.moduleId, this.chapterId, this.topicId).subscribe((topic: any) => {
      this.topicName = topic.name;
    });
  }

  viewContent(subtopicId: number) {
    // Clear existing content and reset selected subtopic before fetching new content
    this.content = null;
    this.selectedSubtopicId = subtopicId;
    this.selectedSubtopicName = this.subtopics.find(subtopic => subtopic.id === subtopicId)?.name || null;

    // Fetch content for the selected subtopic
    this.courseService.getContent(this.courseId, this.subjectId, this.moduleId, this.chapterId, this.topicId, subtopicId).subscribe((content: any) => {
      this.content = content;
    });
  }

  generateContent(subtopicId: number) {
    // Trigger content generation for a subtopic and fetch content
    this.courseService.generateContent(this.courseId, this.subjectId, this.moduleId, this.chapterId, this.topicId, subtopicId).subscribe(() => {
      this.viewContent(subtopicId);  // Reload content after generation
    });
  }

  hideSubtopics() {
    this.showSubtopics = !this.showSubtopics;
  }


  
  

  
  


}

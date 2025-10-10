import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, ParamMap, RouterModule } from '@angular/router';
import { CourseService } from '../services/course.service';
import { SubjectService } from '../services/subject.service';
import { ChapterService } from '../services/chapter.service';
import { TopicService } from '../services/topic.service';
import { ContentService } from '../services/content.service';
import { 
  faHome, faBook, faLayerGroup, faEye, faEyeSlash, faMagic, 
  faInfoCircle, faFileAlt, faSpinner, faChevronRight, faBookOpen,
  faChevronLeft, faList
} from '@fortawesome/free-solid-svg-icons';
import { Subscription } from 'rxjs';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { MarkdownModule } from 'ngx-markdown';

@Component({
  selector: 'app-topics-content',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule, MarkdownModule],
  templateUrl: './topics-content.component.html',
  styleUrls: ['./topics-content.component.css']
})
export class TopicsContentComponent implements OnInit, OnDestroy {
  // FontAwesome icons
  faHome = faHome;
  faBook = faBook;
  faLayerGroup = faLayerGroup;
  faEye = faEye;
  faEyeSlash = faEyeSlash;
  faMagic = faMagic;
  faInfoCircle = faInfoCircle;
  faFileAlt = faFileAlt;
  faSpinner = faSpinner;
  faChevronRight = faChevronRight;
  faChevronLeft = faChevronLeft;
  faBookOpen = faBookOpen;
  faList = faList;

  
  content: any = null;
  sanitizedContent: SafeHtml = '';
  courseId: number;
  subjectId: number;
  chapterId: number;
  topicId: number;
  courseName: string = '';
  subjectName: string = '';
  chapterName: string = '';
  topicName: string = '';
  isGenerating: boolean = false;
  errorMessage: string = '';
  currentTopic: any = null; // Track current topic details
  
  // Add topics list to navigate between them
  topics: any[] = [];
  currentTopicIndex: number = 0;
  
  // Subscription to handle route parameter changes
  private routeSubscription: Subscription;

  constructor(
    private courseService: CourseService,
    private subjectService: SubjectService,
    private chapterService: ChapterService,
    private topicService: TopicService,
    private contentService: ContentService,
    private route: ActivatedRoute,
    private router: Router,
    private sanitizer: DomSanitizer
  ) {
    // Extract route params
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
    this.subjectId = +this.route.snapshot.paramMap.get('subject_id')!;
    this.chapterId = +this.route.snapshot.paramMap.get('chapter_id')!;
    this.topicId = +this.route.snapshot.paramMap.get('topic_id')!;
    
    // Initialize subscriptions
    this.routeSubscription = new Subscription();
  }

  ngOnInit() {
    // Subscribe to route parameter changes
    this.routeSubscription = this.route.paramMap.subscribe(params => {
      this.courseId = +params.get('course_id')!;
      this.subjectId = +params.get('subject_id')!;
      this.chapterId = +params.get('chapter_id')!;
      this.topicId = +params.get('topic_id')!;
      
      this.loadAllData();
    });
  }
  
  ngOnDestroy() {
    // Clean up subscriptions when component is destroyed
    if (this.routeSubscription) {
      this.routeSubscription.unsubscribe();
    }
  }
  
  loadAllData() {
    // Load course details
    this.courseService.getCourseDetails(this.courseId).subscribe({
      next: (course: any) => {
        this.courseName = course.name;
      },
      error: (err) => console.error('Error loading course details:', err)
    });
    
    // Load subject details
    this.subjectService.getSubjectDetails(this.courseId, this.subjectId).subscribe({
      next: (subject: any) => {
        this.subjectName = subject.name;
      },
      error: (err) => console.error('Error loading subject details:', err)
    });
    
    // Load chapter details
    this.chapterService.getChapterDetails(this.courseId, this.subjectId, this.chapterId).subscribe({
      next: (chapter: any) => {
        this.chapterName = chapter.name;
        
        // Load all topics for this chapter to enable navigation between topics
        this.loadTopics();
      },
      error: (err) => console.error('Error loading chapter details:', err)
    });

    // Load topic details
    this.topicService.getTopicDetails(this.courseId, this.subjectId, this.chapterId, this.topicId).subscribe({
      next: (topic: any) => {
        this.topicName = topic.name;
        this.loadContent(); // Load content once we have the topic
      },
      error: (err) => console.error('Error loading topic details:', err)
    });
  }

  loadTopics() {
    this.topicService.getTopics(this.courseId, this.subjectId, this.chapterId).subscribe({
      next: (topics: any[]) => {
        this.topics = topics;
        // Find the index of the current topic
        this.currentTopicIndex = this.topics.findIndex(topic => topic.id === this.topicId);
        // Set the current topic
        this.currentTopic = this.topics.find(topic => topic.id === this.topicId) || null;
        console.log(`Current topic is at index ${this.currentTopicIndex} of ${this.topics.length} topics`);
      },
      error: (err) => console.error('Error loading topics:', err)
    });
  }

  loadContent() {
    this.contentService.getContent(this.courseId, this.subjectId, this.chapterId, this.topicId).subscribe({
      next: (content: any) => {
        this.content = this.prepareMarkdownContent(content); 
        
        // If we have content, mark this topic as having content in our local data
        if (content && this.currentTopic) {
          this.currentTopic.has_content = true;
        }
        console.log('Content loaded:', !!content);
      },
      error: (error) => {
        console.error('Error loading content:', error);
        this.content = null;
      }
    });
  }
  
  // Helper method to fix common markdown rendering issues
  prepareMarkdownContent(content: string): string {
    if (!content) return '';
    
    // Fix line breaks and spacing issues
    let formatted = content
      //.replace(/```/g, '\n```\n')       // Ensure code blocks have proper spacing
      //.replace(/<pre class="mermaid">/g, '\n<pre class="mermaid">\n')  // Fix mermaid diagram spacing
      //.replace(/<\/pre>/g, '\n</pre>\n')  // Fix closing pre tag spacing
      .replace(/\$\$/g, '\n$$\n')       // Fix math expressions spacing
      .replace(/\$\n\$/g, '$$ $$')       // Fix inline math expressions
      .replace(/\n{3,}/g, '\n\n');       // Remove excessive line breaks
    
    // Make sure each heading has a proper space after the # symbol
    formatted = formatted.replace(/^(#{1,6})([^ ])/gm, '$1 $2');
    
    return formatted;
  }

  generateContent() {
    // Show loading state
    this.isGenerating = true;
    this.errorMessage = '';
    
    // Find the current topic to determine if updating or generating
    const currentTopic = this.topics.find(t => t.id === this.topicId);
    const actionVerb = currentTopic && currentTopic.has_content ? 'updating' : 'generating';
    
    // Trigger content generation for the topic
    this.contentService.generateContent(this.courseId, this.subjectId, this.chapterId, this.topicId).subscribe({
      next: (response) => {
        console.log(`Content ${actionVerb} response:`, response);
        
        // Mark this topic as having content in our local data
        if (currentTopic) {
          currentTopic.has_content = true;
        }
        
        // Immediately load the new content without requiring a page refresh
        this.loadContent();
        this.isGenerating = false;
      },
      error: (error) => {
        console.error(`Error ${actionVerb} content:`, error);
        this.isGenerating = false;
        this.errorMessage = `Failed to ${actionVerb.replace('ing', '')} content. Please try again.`;
      }
    });
  }
  
  // Navigate to previous topic
  previousTopic() {
    if (this.currentTopicIndex > 0) {
      const prevTopic = this.topics[this.currentTopicIndex - 1];
      this.router.navigate([
        `/courses/${this.courseId}/subjects/${this.subjectId}/content/${prevTopic.id}`
      ]);
    }
  }
  
  // Navigate to next topic
  nextTopic() {
    if (this.currentTopicIndex < this.topics.length - 1) {
      const nextTopic = this.topics[this.currentTopicIndex + 1];
      this.router.navigate([
        `/courses/${this.courseId}/subjects/${this.subjectId}/content/${nextTopic.id}`
      ]);
    }
  }
  
  // Go back to topics list or to subject content view
  backToTopics() {
    this.router.navigate([`/courses/${this.courseId}/subjects/${this.subjectId}/content`]);
  }
}

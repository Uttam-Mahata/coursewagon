import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { MarkdownModule } from 'ngx-markdown';
import {
  faHome, faBook, faChevronLeft, faChevronRight, faCheckCircle,
  faCircle, faSpinner, faArrowLeft, faList, faBookOpen
} from '@fortawesome/free-solid-svg-icons';
import { Subscription } from 'rxjs';
import { LearningService } from '../services/learning.service';
import { EnrollmentService } from '../services/enrollment.service';
import { CourseService } from '../services/course.service';
import { SubjectService } from '../services/subject.service';
import { ChapterService } from '../services/chapter.service';
import { TopicService } from '../services/topic.service';
import { ContentService } from '../services/content.service';

@Component({
  selector: 'app-learning-view',
  standalone: true,
  imports: [CommonModule, RouterModule, FontAwesomeModule, MarkdownModule],
  templateUrl: './learning-view.component.html',
  styleUrl: './learning-view.component.css'
})
export class LearningViewComponent implements OnInit, OnDestroy {
  // Icons
  faHome = faHome;
  faBook = faBook;
  faChevronLeft = faChevronLeft;
  faChevronRight = faChevronRight;
  faCheckCircle = faCheckCircle;
  faCircle = faCircle;
  faSpinner = faSpinner;
  faArrowLeft = faArrowLeft;
  faList = faList;
  faBookOpen = faBookOpen;

  // Route parameters
  courseId!: number;
  topicId?: number;

  // Data
  enrollment: any = null;
  course: any = null;
  subjects: any[] = [];
  currentTopic: any = null;
  currentSubject: any = null;
  content: string = '';

  // All topics (flattened for navigation)
  allTopics: any[] = [];
  currentTopicIndex = 0;

  // Progress tracking
  progressMap = new Map<number, any>(); // topic_id -> progress
  completedTopics = new Set<number>();

  // State
  loading = false;
  loadingContent = false;
  error = '';

  // Sidebar
  showSidebar = true;
  isSidebarOpen = true;

  private routeSubscription?: Subscription;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private learningService: LearningService,
    private enrollmentService: EnrollmentService,
    private courseService: CourseService,
    private subjectService: SubjectService,
    private chapterService: ChapterService,
    private topicService: TopicService,
    private contentService: ContentService
  ) {}

  ngOnInit(): void {
    // Subscribe to route parameter changes
    this.routeSubscription = this.route.paramMap.subscribe(params => {
      const courseIdParam = params.get('course_id') || params.get('id');
      const topicIdParam = params.get('topic_id');

      if (courseIdParam) {
        this.courseId = parseInt(courseIdParam);
        this.topicId = topicIdParam ? parseInt(topicIdParam) : undefined;
        this.loadCourseData();
      }
    });

    // Adjust sidebar for screen size
    this.adjustSidebarForScreenSize();
    window.addEventListener('resize', this.adjustSidebarForScreenSize.bind(this));
  }

  ngOnDestroy(): void {
    // Save progress before leaving
    if (this.topicId && this.enrollment) {
      this.trackProgress();
    }

    // Unsubscribe
    if (this.routeSubscription) {
      this.routeSubscription.unsubscribe();
    }

    // Remove resize listener
    window.removeEventListener('resize', this.adjustSidebarForScreenSize.bind(this));
  }

  loadCourseData(): void {
    this.loading = true;
    this.error = '';

    // Check enrollment
    this.enrollmentService.checkEnrollment(this.courseId).subscribe({
      next: (check) => {
        if (!check.enrolled || !check.enrollment) {
          this.router.navigate(['/courses/preview', this.courseId]);
          return;
        }

        this.enrollment = check.enrollment;

        // Load course details
        this.loadCourseDetails();

        // Load progress
        this.loadProgress();
      },
      error: (err) => {
        this.error = 'Failed to verify enrollment';
        this.loading = false;
        console.error('Error checking enrollment:', err);
      }
    });
  }

  loadCourseDetails(): void {
    // Load course
    this.courseService.getCourseDetails(this.courseId).subscribe({
      next: (course) => {
        this.course = course;

        // Load subjects and topics
        this.loadSubjectsAndTopics();
      },
      error: (err) => {
        this.error = 'Failed to load course details';
        this.loading = false;
        console.error('Error loading course:', err);
      }
    });
  }

  loadSubjectsAndTopics(): void {
    this.subjectService.getSubjects(this.courseId).subscribe({
      next: (subjects) => {
        this.subjects = subjects;

        // Load chapters and topics for each subject
        let loadedCount = 0;
        const totalSubjects = subjects.length;

        if (totalSubjects === 0) {
          this.error = 'No subjects found in this course';
          this.loading = false;
          return;
        }

        subjects.forEach((subject: any) => {
          // Load chapters for this subject
          this.chapterService.getChapters(this.courseId, subject.id).subscribe({
            next: (chapters) => {
              subject.chapters = chapters;

              // Load topics for each chapter
              let loadedChapters = 0;
              const totalChapters = chapters.length;

              if (totalChapters === 0) {
                loadedCount++;
                if (loadedCount === totalSubjects) {
                  this.finishLoadingStructure();
                }
                return;
              }

              chapters.forEach((chapter: any) => {
                this.topicService.getTopics(this.courseId, subject.id, chapter.id).subscribe({
                  next: (topics) => {
                    chapter.topics = topics;

                    // Add topics to allTopics with full context
                    topics.forEach((topic: any) => {
                      this.allTopics.push({
                        ...topic,
                        subject_id: subject.id,
                        subject_name: subject.name,
                        chapter_id: chapter.id,
                        chapter_name: chapter.name
                      });
                    });

                    loadedChapters++;
                    if (loadedChapters === totalChapters) {
                      loadedCount++;
                      if (loadedCount === totalSubjects) {
                        this.finishLoadingStructure();
                      }
                    }
                  },
                  error: (err) => {
                    console.error(`Error loading topics for chapter ${chapter.id}:`, err);
                    loadedChapters++;
                    if (loadedChapters === totalChapters) {
                      loadedCount++;
                      if (loadedCount === totalSubjects) {
                        this.finishLoadingStructure();
                      }
                    }
                  }
                });
              });
            },
            error: (err) => {
              console.error(`Error loading chapters for subject ${subject.id}:`, err);
              loadedCount++;
              if (loadedCount === totalSubjects) {
                this.finishLoadingStructure();
              }
            }
          });
        });
      },
      error: (err) => {
        this.error = 'Failed to load course structure';
        this.loading = false;
        console.error('Error loading subjects:', err);
      }
    });
  }

  finishLoadingStructure(): void {
    // Determine which topic to load
    if (this.topicId) {
      this.loadTopic(this.topicId);
    } else {
      // Try to resume from last position
      this.resumeLearning();
    }

    this.loading = false;
  }

  loadProgress(): void {
    if (!this.enrollment) return;

    this.learningService.getCourseProgress(this.enrollment.id).subscribe({
      next: (progress) => {
        // Build progress map
        if (progress.progress_records) {
          progress.progress_records.forEach((record: any) => {
            this.progressMap.set(record.topic_id, record);
            if (record.completed) {
              this.completedTopics.add(record.topic_id);
            }
          });
        }
      },
      error: (err) => {
        console.error('Error loading progress:', err);
      }
    });
  }

  resumeLearning(): void {
    if (!this.enrollment) return;

    this.learningService.getResumePoint(this.enrollment.id).subscribe({
      next: (resumePoint) => {
        if (resumePoint && resumePoint.topic_id) {
          this.loadTopic(resumePoint.topic_id);
        } else if (this.allTopics.length > 0) {
          // Load first topic
          this.loadTopic(this.allTopics[0].id);
        }
      },
      error: (err) => {
        console.error('Error getting resume point:', err);
        // Load first topic as fallback
        if (this.allTopics.length > 0) {
          this.loadTopic(this.allTopics[0].id);
        }
      }
    });
  }

  loadTopic(topicId: number): void {
    // Save progress for previous topic
    if (this.topicId && this.enrollment) {
      this.trackProgress();
    }

    this.loadingContent = true;
    this.topicId = topicId;

    // Find topic in all topics
    const topicIndex = this.allTopics.findIndex(t => t.id === topicId);
    if (topicIndex >= 0) {
      this.currentTopicIndex = topicIndex;
      this.currentTopic = this.allTopics[topicIndex];

      // Find subject
      this.currentSubject = this.subjects.find(s => s.id === this.currentTopic.subject_id);

      // Load content
      this.loadContent();

      // Update URL without triggering route subscription
      this.router.navigate([], {
        relativeTo: this.route,
        queryParams: { topic: topicId },
        queryParamsHandling: 'merge',
        replaceUrl: true
      });
    }
  }

  loadContent(): void {
    if (!this.currentTopic) return;

    // Use the proper chapter_id from the current topic
    const chapterId = this.currentTopic.chapter_id || 0;
    const subjectId = this.currentTopic.subject_id || 0;

    this.contentService.getContent(
      this.courseId,
      subjectId,
      chapterId,
      this.currentTopic.id
    ).subscribe({
      next: (contentData) => {
        // contentData is the content string itself, not an object with .content property
        this.content = this.prepareMarkdownContent(contentData || '');
        console.log(`[LearningView] Content loaded successfully for topic ${this.currentTopic.id}, length: ${this.content?.length || 0}`);
        this.loadingContent = false;
      },
      error: (err) => {
        console.error('[LearningView] Error loading content:', err);
        this.content = '';
        this.loadingContent = false;
      }
    });
  }

  prepareMarkdownContent(content: string): string {
    if (!content) return '';

    let formatted = content
      .replace(/\$\$/g, '\n$$\n')
      .replace(/\$\n\$/g, '$$ $$')
      .replace(/\n{3,}/g, '\n\n');

    formatted = formatted.replace(/^(#{1,6})([^ ])/gm, '$1 $2');

    return formatted;
  }

  trackProgress(): void {
    if (!this.enrollment || !this.topicId) return;

    const isCompleted = this.isTopicCompleted(this.topicId);

    this.learningService.trackProgress({
      enrollment_id: this.enrollment.id,
      topic_id: this.topicId,
      completed: isCompleted,
      time_spent_seconds: 0
    }).subscribe({
      next: () => {
        console.log('Progress tracked');
      },
      error: (err) => {
        console.error('Error tracking progress:', err);
      }
    });
  }

  markTopicComplete(): void {
    if (!this.enrollment || !this.topicId) return;

    this.learningService.markTopicComplete({
      enrollment_id: this.enrollment.id,
      topic_id: this.topicId
    }).subscribe({
      next: () => {
        this.completedTopics.add(this.topicId!);
        // Move to next topic
        if (this.hasNextTopic) {
          this.nextTopic();
        }
      },
      error: (err) => {
        console.error('Error marking topic complete:', err);
      }
    });
  }

  previousTopic(): void {
    if (this.currentTopicIndex > 0) {
      const prevTopic = this.allTopics[this.currentTopicIndex - 1];
      this.loadTopic(prevTopic.id);
    }
  }

  nextTopic(): void {
    if (this.currentTopicIndex < this.allTopics.length - 1) {
      const nextTopic = this.allTopics[this.currentTopicIndex + 1];
      this.loadTopic(nextTopic.id);
    }
  }

  selectTopic(topicId: number): void {
    this.loadTopic(topicId);

    // Close sidebar on mobile after topic selection
    if (window.innerWidth < 768) {
      this.isSidebarOpen = false;

      // Scroll to top after closing sidebar
      setTimeout(() => {
        window.scrollTo(0, 0);
      }, 100);
    }
  }

  toggleSidebar(): void {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  adjustSidebarForScreenSize(): void {
    if (window.innerWidth < 768) {
      this.isSidebarOpen = false;
    } else {
      this.isSidebarOpen = true;
    }
  }

  goBackToDashboard(): void {
    this.router.navigate(['/learner/dashboard']);
  }

  isTopicCompleted(topicId: number): boolean {
    return this.completedTopics.has(topicId);
  }

  getTopicProgress(topicId: number): any {
    return this.progressMap.get(topicId);
  }

  get hasPreviousTopic(): boolean {
    return this.currentTopicIndex > 0;
  }

  get hasNextTopic(): boolean {
    return this.currentTopicIndex < this.allTopics.length - 1;
  }

  get progressPercentage(): number {
    if (this.allTopics.length === 0) return 0;
    return Math.round((this.completedTopics.size / this.allTopics.length) * 100);
  }
}

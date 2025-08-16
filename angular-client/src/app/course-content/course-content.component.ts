import { Component, OnInit, OnDestroy, AfterViewChecked } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';
import { SubjectService } from '../services/subject.service';
import { ChapterService } from '../services/chapter.service';
import { TopicService } from '../services/topic.service';
import { ContentService } from '../services/content.service';
import { MathRendererService } from '../services/math-renderer.service';
import { 
  faHome, faBook, faLayerGroup, faEye, faMagic, 
  faBookOpen, faChevronRight, faChevronDown, faChevronUp,
  faFileAlt, faSpinner, faInfoCircle, faChevronLeft, faList,
  faEdit, faTrash, faPlus
} from '@fortawesome/free-solid-svg-icons';
import { Subscription, forkJoin } from 'rxjs';
@Component({
  selector: 'app-course-content',
  standalone: false,
  templateUrl: './course-content.component.html',
  styleUrls: ['./course-content.component.css'],
})
export class CourseContentComponent implements OnInit, OnDestroy, AfterViewChecked {
  // FontAwesome icons
  faHome = faHome;
  faBook = faBook;
  faLayerGroup = faLayerGroup;
  faEye = faEye;
  faMagic = faMagic;
  faBookOpen = faBookOpen;
  faChevronRight = faChevronRight;
  faChevronDown = faChevronDown;
  faChevronUp = faChevronUp;
  faFileAlt = faFileAlt;
  faSpinner = faSpinner;
  faInfoCircle = faInfoCircle;
  faChevronLeft = faChevronLeft;
  faList = faList;
  faEdit = faEdit;
  faTrash = faTrash;
  faPlus = faPlus;

  // Course data
  courseId: number;
  courseName: string = '';
  subjectId: number;
  subjectName: string = '';
  subjects: any[] = [];
  
  // Chapter data
  chapters: any[] = [];
  expandedChapterId: number | null = null;
  
  // Topic data
  topics: { [chapterId: number]: any[] } = {};
  selectedTopicId: number | null = null;
  selectedTopic: any = null;
  
  // Content
  content: string | null = null;
  processedContent: string | null = null; // New property for processed content
  
  // UI state
  isGeneratingChapters: boolean = false;
  isGeneratingTopics: boolean = false;
  generatingChapterId: number | null = null;
  isGeneratingContent: boolean = false;
  errorMessage: string = '';
  isSidebarOpen: boolean = true; // For mobile responsiveness
  
  // Loading states
  isLoadingSubjects: boolean = false;
  isLoadingChapters: boolean = false;
  isLoadingContent: boolean = false;
  
  private subscriptions = new Subscription();

  // UI state for edit/delete operations
  editingChapter: any = null;
  editingTopic: any = null;
  editingContent: string | null = null;
  showEditChapterModal: boolean = false;
  showDeleteChapterModal: boolean = false;
  showEditTopicModal: boolean = false;
  showDeleteTopicModal: boolean = false;
  showEditContentModal: boolean = false;
  showDeleteContentConfirm: boolean = false;
  isDeletingChapter: boolean = false;
  isDeletingTopic: boolean = false;
  isDeletingContent: boolean = false;

  // New properties for modal forms
  showNewChapterModal: boolean = false;
  showNewTopicModal: boolean = false;
  showNewContentModal: boolean = false;
  newChapterName: string = '';
  newTopicName: string = '';
  newContentText: string = '';
  isAddingChapter: boolean = false;
  isAddingTopic: boolean = false;
  isAddingContent: boolean = false;

  // Flag to track if MathJax needs rendering
  private needsMathJaxUpdate = false;

  constructor(
    private courseService: CourseService,
    private subjectService: SubjectService,
    private chapterService: ChapterService,
    private topicService: TopicService,
    private contentService: ContentService,
    public mathRendererService: MathRendererService,
    private route: ActivatedRoute,
    private router: Router,
  ) {
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
    this.subjectId = +this.route.snapshot.paramMap.get('subject_id')!;
  }

  ngOnInit() {
    this.loadInitialData();
    
    // Subscribe to route parameter changes
    this.subscriptions.add(
      this.route.paramMap.subscribe(params => {
        const newCourseId = +params.get('course_id')!;
        const newSubjectId = +params.get('subject_id')!;
        const topicId = params.get('topic_id');
        
        // Check if course or subject has changed
        if (newCourseId !== this.courseId || newSubjectId !== this.subjectId) {
          this.courseId = newCourseId;
          this.subjectId = newSubjectId;
          this.loadInitialData();
        }
        
        // If a topic ID is provided in the URL, select that topic
        if (topicId) {
          this.selectTopicById(+topicId);
        }
      })
    );
    
    // Auto-close sidebar on small screens when component initializes
    this.adjustSidebarForScreenSize();
    
    // Add window resize listener
    window.addEventListener('resize', this.adjustSidebarForScreenSize.bind(this));
  }
  
  ngOnDestroy() {
    this.subscriptions.unsubscribe();
    
    // Remove resize listener when component is destroyed
    window.removeEventListener('resize', this.adjustSidebarForScreenSize.bind(this));
  }
  
  ngAfterViewChecked() {
    // Render MathJax if needed
    if (this.needsMathJaxUpdate) {
      this.mathRendererService.renderMathJax();
      this.needsMathJaxUpdate = false;
      
      // Trigger another update after a delay to catch any equations that might have loaded later
      setTimeout(() => {
        this.mathRendererService.renderMathJax();
      }, 500);
    }
  }
  
  loadInitialData() {
    this.isLoadingSubjects = true;
    
    // Load course details
    this.subscriptions.add(
      this.courseService.getCourseDetails(this.courseId).subscribe({
        next: (course) => {
          this.courseName = course.name;
        },
        error: (err) => console.error('Error loading course details:', err)
      })
    );
    
    // Load subject details to get the subject name
    this.subscriptions.add(
      this.subjectService.getSubjectDetails(this.courseId, this.subjectId).subscribe({
        next: (subject) => {
          this.subjectName = subject.name;
        },
        error: (err) => console.error('Error loading subject details:', err)
      })
    );
    
    // Load chapters for the current subject
    this.loadChapters();
  }
  
  loadChapters() {
    this.isLoadingChapters = true;
    this.chapters = [];
    this.topics = {};
    
    this.subscriptions.add(
      this.chapterService.getChapters(this.courseId, this.subjectId).subscribe({
        next: (chapters) => {
          this.chapters = chapters;
          this.isLoadingChapters = false;
          
          // If there's a chapter with topics, expand it
          const chapterWithTopics = this.chapters.find(c => c.has_topics);
          if (chapterWithTopics) {
            this.toggleChapter(chapterWithTopics.id);
          } else if (this.chapters.length > 0) {
            // Otherwise expand the first chapter
            this.toggleChapter(this.chapters[0].id);
          }
        },
        error: (err) => {
          console.error('Error loading chapters:', err);
          this.isLoadingChapters = false;
        }
      })
    );
  }
  
  toggleChapter(chapterId: number) {
    // If chapter is already expanded, collapse it
    if (this.expandedChapterId === chapterId) {
      this.expandedChapterId = null;
      return;
    }
    
    this.expandedChapterId = chapterId;
    
    // Check if we already loaded topics for this chapter
    if (this.topics[chapterId]) {
      return;
    }
    
    // Load topics for this chapter
    this.loadTopics(chapterId);
  }
  
  loadTopics(chapterId: number) {
    const chapter = this.chapters.find(c => c.id === chapterId);
    
    // If chapter has no topics yet, generate them
    if (!chapter?.has_topics) {
      this.generateTopics(chapterId);
      return;
    }
    
    this.subscriptions.add(
      this.topicService.getTopics(this.courseId, this.subjectId, chapterId).subscribe({
        next: (topics) => {
          this.topics[chapterId] = topics;
          
          // If no topic is selected yet and we have topics, select the first one
          if (!this.selectedTopicId && topics.length > 0) {
            this.selectTopic(topics[0]);
          }
        },
        error: (err) => console.error('Error loading topics:', err)
      })
    );
  }
  
  selectTopic(topic: any) {
    this.selectedTopicId = topic.id;
    this.selectedTopic = topic;
    this.loadContent(topic.id);
    
    // Update URL without navigation
    this.updateUrlWithTopicId(topic.id);
    
    // Hide sidebar on mobile when a topic is selected
    if (window.innerWidth < 768) {
      this.isSidebarOpen = false;
      
      // Scroll to top when selecting a new topic
      setTimeout(() => {
        window.scrollTo(0, 0);
      }, 100);
    }
  }
  
  selectTopicById(topicId: number) {
    // Find the topic in our loaded topics
    for (const chapterId in this.topics) {
      const topic = this.topics[chapterId].find(t => t.id === topicId);
      if (topic) {
        this.expandedChapterId = +chapterId;
        this.selectTopic(topic);
        return;
      }
    }
    
    // If topic not found in loaded topics, we need to find which chapter it belongs to
    // and load that chapter's topics
    this.findChapterForTopic(topicId);
  }
  
  findChapterForTopic(topicId: number) {
    // We'll check each chapter one by one to find which one contains this topic
    const checkNextChapter = (index: number) => {
      if (index >= this.chapters.length) {
        // Topic not found in any chapter
        console.error('Topic not found in any chapter:', topicId);
        return;
      }
      
      const chapter = this.chapters[index];
      
      this.topicService.getTopics(this.courseId, this.subjectId, chapter.id).subscribe({
        next: (topics) => {
          const topic = topics.find((t: any) => t.id === topicId);
          if (topic) {
            // Found the topic in this chapter
            this.topics[chapter.id] = topics;
            this.expandedChapterId = chapter.id;
            this.selectTopic(topic);
          } else {
            // Check the next chapter
            checkNextChapter(index + 1);
          }
        },
        error: () => {
          // Check the next chapter on error
          checkNextChapter(index + 1);
        }
      });
    };
    
    // Start checking from the first chapter
    checkNextChapter(0);
  }
  
  loadContent(topicId: number) {
    this.isLoadingContent = true;
    this.content = null;
    this.processedContent = null;
    
    this.subscriptions.add(
      this.contentService.getContent(this.courseId, this.subjectId, this.expandedChapterId!, topicId).subscribe({
        next: (content) => {
          this.content = content;
          
          // Process content for LaTeX equations
          if (content) {
            this.processedContent = this.mathRendererService.processContent(content);
            this.needsMathJaxUpdate = true; // Mark for MathJax rendering
          }
          
          this.isLoadingContent = false;
          
          // If we received content, mark this topic as having content
          if (content && this.selectedTopic) {
            this.selectedTopic.has_content = true;
          }
        },
        error: (err) => {
          console.error('Error loading content:', err);
          this.isLoadingContent = false;
        }
      })
    );
  }
  
  generateChapters() {
    this.isGeneratingChapters = true;
    this.errorMessage = '';
    
    this.subscriptions.add(
      this.chapterService.generateChapters(this.courseId, this.subjectId).subscribe({
        next: () => {
          this.isGeneratingChapters = false;
          this.loadChapters(); // Refresh chapters
        },
        error: (err) => {
          console.error('Error generating chapters:', err);
          this.isGeneratingChapters = false;
          this.errorMessage = 'Failed to generate chapters. Please try again.';
        }
      })
    );
  }
  
  generateTopics(chapterId: number) {
    this.isGeneratingTopics = true;
    this.generatingChapterId = chapterId;
    this.errorMessage = '';
    
    const chapter = this.chapters.find(c => c.id === chapterId);
    
    this.subscriptions.add(
      this.topicService.generateTopics(this.courseId, this.subjectId, chapterId).subscribe({
        next: () => {
          // Mark chapter as having topics
          if (chapter) {
            chapter.has_topics = true;
          }
          
          // Load the generated topics
          this.topicService.getTopics(this.courseId, this.subjectId, chapterId).subscribe({
            next: (topics) => {
              this.topics[chapterId] = topics;
              this.isGeneratingTopics = false;
              this.generatingChapterId = null;
              
              // Select first topic if available
              if (topics.length > 0) {
                this.selectTopic(topics[0]);
              }
            },
            error: (err) => {
              console.error('Error loading generated topics:', err);
              this.isGeneratingTopics = false;
              this.generatingChapterId = null;
            }
          });
        },
        error: (err) => {
          console.error('Error generating topics:', err);
          this.isGeneratingTopics = false;
          this.generatingChapterId = null;
          this.errorMessage = 'Failed to generate topics. Please try again.';
        }
      })
    );
  }
  
  generateContent() {
    if (!this.selectedTopicId || !this.expandedChapterId) {
      return;
    }
    
    this.isGeneratingContent = true;
    this.errorMessage = '';
    
    this.subscriptions.add(
      this.contentService.generateContent(
        this.courseId,
        this.subjectId,
        this.expandedChapterId,
        this.selectedTopicId
      ).subscribe({
        next: () => {
          // Mark topic as having content
          if (this.selectedTopic) {
            this.selectedTopic.has_content = true;
          }
          
          // Load the generated content
          this.contentService.getContent(
            this.courseId, 
            this.subjectId, 
            this.expandedChapterId!, 
            this.selectedTopicId!
          ).subscribe({
            next: (content) => {
              this.content = content;
              
              // Process content for LaTeX equations
              if (content) {
                this.processedContent = this.mathRendererService.processContent(content);
                this.needsMathJaxUpdate = true; // Mark for MathJax rendering
              }
              
              this.isGeneratingContent = false;
            },
            error: (err) => {
              console.error('Error loading generated content:', err);
              this.isGeneratingContent = false;
            }
          });
        },
        error: (err) => {
          console.error('Error generating content:', err);
          this.isGeneratingContent = false;
          this.errorMessage = 'Failed to generate content. Please try again.';
        }
      })
    );
  }
  
  updateUrlWithTopicId(topicId: number) {
    // Update URL without navigation for smoother experience
    const url = `/courses/${this.courseId}/subjects/${this.subjectId}/content/${topicId}`;
    window.history.replaceState({}, '', url);
  }
  
  toggleSidebar() {
    this.isSidebarOpen = !this.isSidebarOpen;
    
    // When closing sidebar on mobile, add a small delay to allow animation to complete
    if (!this.isSidebarOpen && window.innerWidth < 768) {
      setTimeout(() => {
        // Optional: scroll the content to the top for better UX
        const contentArea = document.querySelector('.flex-1.overflow-y-auto');
        if (contentArea) {
          contentArea.scrollTop = 0;
        }
      }, 300);
    }

    // When showing sidebar on mobile, scroll it to top
    if (this.isSidebarOpen && window.innerWidth < 768) {
      setTimeout(() => {
        const sidebar = document.querySelector('.bg-gray-900.text-white');
        if (sidebar) {
          sidebar.scrollTop = 0;
        }
      }, 100);
    }
  }
  
  // Adjust sidebar visibility based on screen size
  adjustSidebarForScreenSize() {
    // Auto-close sidebar on small screens (mobile)
    if (window.innerWidth < 768) {
      this.isSidebarOpen = false;
    } else {
      this.isSidebarOpen = true;
    }
  }
  
  // Helper function to prepare markdown content
  prepareMarkdownContent(content: string): string {
    if (!content) return '';
    
    // Fix line breaks and spacing issues
    let formatted = content
      .replace(/\$\$/g, '\n$$\n')       // Fix math expressions spacing
      .replace(/\$\n\$/g, '$$ $$')       // Fix inline math expressions
      .replace(/\n{3,}/g, '\n\n');       // Remove excessive line breaks
    
    // Make sure each heading has a proper space after the # symbol
    formatted = formatted.replace(/^(#{1,6})([^ ])/gm, '$1 $2');
    
    return formatted;
  }

  // Add these new methods to support topic navigation
  getPreviousTopic() {
    if (!this.selectedTopicId || !this.expandedChapterId) return null;
    
    const currentTopics = this.topics[this.expandedChapterId];
    if (!currentTopics) return null;
    
    const currentIndex = currentTopics.findIndex(topic => topic.id === this.selectedTopicId);
    if (currentIndex <= 0) return null;
    
    return currentTopics[currentIndex - 1];
  }
  
  getNextTopic() {
    if (!this.selectedTopicId || !this.expandedChapterId) return null;
    
    const currentTopics = this.topics[this.expandedChapterId];
    if (!currentTopics) return null;
    
    const currentIndex = currentTopics.findIndex(topic => topic.id === this.selectedTopicId);
    if (currentIndex === -1 || currentIndex >= currentTopics.length - 1) return null;
    
    return currentTopics[currentIndex + 1];
  }
  
  navigateToPreviousTopic() {
    const prevTopic = this.getPreviousTopic();
    if (prevTopic) {
      this.selectTopic(prevTopic);
    }
  }
  
  navigateToNextTopic() {
    const nextTopic = this.getNextTopic();
    if (nextTopic) {
      this.selectTopic(nextTopic);
    }
  }

  // Add this helper method to get a chapter name by ID
  getChapterNameById(chapterId: number | null): string {
    if (!chapterId || !this.chapters) return '';
    const chapter = this.chapters.find(c => c.id === chapterId);
    return chapter ? chapter.name : 'Course Outline';
  }

  // CRUD operations for Chapters
  openEditChapterModal(chapter: any, event?: Event) {
    if (event) {
      event.stopPropagation(); // Prevent chapter toggle
    }
    this.editingChapter = { ...chapter };
    this.showEditChapterModal = true;
  }

  closeEditChapterModal() {
    this.showEditChapterModal = false;
    this.editingChapter = null;
  }

  updateChapter() {
    if (!this.editingChapter || !this.editingChapter.name.trim()) {
      this.errorMessage = 'Chapter name is required';
      return;
    }

    this.chapterService.updateChapter(
      this.courseId,
      this.subjectId,
      this.editingChapter.id,
      this.editingChapter.name
    ).subscribe({
      next: () => {
        // Update local chapter data
        const index = this.chapters.findIndex(c => c.id === this.editingChapter.id);
        if (index !== -1) {
          this.chapters[index].name = this.editingChapter.name;
        }
        this.closeEditChapterModal();
      },
      error: (err) => {
        console.error('Error updating chapter:', err);
        this.errorMessage = 'Failed to update chapter. Please try again.';
      }
    });
  }

  openDeleteChapterModal(chapter: any, event?: Event) {
    if (event) {
      event.stopPropagation(); // Prevent chapter toggle
    }
    this.editingChapter = chapter;
    this.showDeleteChapterModal = true;
  }

  closeDeleteChapterModal() {
    this.showDeleteChapterModal = false;
    this.editingChapter = null;
  }

  deleteChapter() {
    if (!this.editingChapter) return;
    
    this.isDeletingChapter = true;
    
    this.chapterService.deleteChapter(
      this.courseId,
      this.subjectId,
      this.editingChapter.id
    ).subscribe({
      next: () => {
        // Remove chapter from local data
        this.chapters = this.chapters.filter(c => c.id !== this.editingChapter.id);
        
        // If we deleted the expanded chapter, clear selection
        if (this.expandedChapterId === this.editingChapter.id) {
          this.expandedChapterId = null;
          this.selectedTopicId = null;
          this.selectedTopic = null;
          this.content = null;
        }
        
        this.closeDeleteChapterModal();
        this.isDeletingChapter = false;
      },
      error: (err) => {
        console.error('Error deleting chapter:', err);
        this.errorMessage = 'Failed to delete chapter. Please try again.';
        this.isDeletingChapter = false;
      }
    });
  }

  // CRUD operations for Topics
  openEditTopicModal(topic: any, event?: Event) {
    if (event) {
      event.stopPropagation(); // Prevent topic selection
    }
    this.editingTopic = { ...topic };
    this.showEditTopicModal = true;
  }

  closeEditTopicModal() {
    this.showEditTopicModal = false;
    this.editingTopic = null;
  }

  updateTopic() {
    if (!this.editingTopic || !this.editingTopic.name.trim() || !this.expandedChapterId) {
      this.errorMessage = 'Topic name is required';
      return;
    }

    this.topicService.updateTopic(
      this.courseId,
      this.subjectId,
      this.expandedChapterId,
      this.editingTopic.id,
      this.editingTopic.name
    ).subscribe({
      next: () => {
        // Update local topic data
        const topicsArray = this.topics[this.expandedChapterId!];
        if (topicsArray) {
          const index = topicsArray.findIndex((t: any) => t.id === this.editingTopic.id);
          if (index !== -1) {
            topicsArray[index].name = this.editingTopic.name;
            
            // If this was the selected topic, update that too
            if (this.selectedTopicId === this.editingTopic.id) {
              this.selectedTopic.name = this.editingTopic.name;
            }
          }
        }
        this.closeEditTopicModal();
      },
      error: (err) => {
        console.error('Error updating topic:', err);
        this.errorMessage = 'Failed to update topic. Please try again.';
      }
    });
  }

  openDeleteTopicModal(topic: any, event?: Event) {
    if (event) {
      event.stopPropagation(); // Prevent topic selection
    }
    this.editingTopic = topic;
    this.showDeleteTopicModal = true;
  }

  closeDeleteTopicModal() {
    this.showDeleteTopicModal = false;
    this.editingTopic = null;
  }

  deleteTopic() {
    if (!this.editingTopic || !this.expandedChapterId) return;
    
    this.isDeletingTopic = true;
    
    this.topicService.deleteTopic(
      this.courseId,
      this.subjectId,
      this.expandedChapterId,
      this.editingTopic.id
    ).subscribe({
      next: () => {
        // Remove topic from local data
        if (this.topics[this.expandedChapterId!]) {
          this.topics[this.expandedChapterId!] = this.topics[this.expandedChapterId!]
            .filter((t: any) => t.id !== this.editingTopic.id);
        }
        
        // If we deleted the selected topic, clear selection
        if (this.selectedTopicId === this.editingTopic.id) {
          this.selectedTopicId = null;
          this.selectedTopic = null;
          this.content = null;
          
          // Try to select another topic
          if (this.topics[this.expandedChapterId!]?.length > 0) {
            this.selectTopic(this.topics[this.expandedChapterId!][0]);
          }
        }
        
        this.closeDeleteTopicModal();
        this.isDeletingTopic = false;
      },
      error: (err) => {
        console.error('Error deleting topic:', err);
        this.errorMessage = 'Failed to delete topic. Please try again.';
        this.isDeletingTopic = false;
      }
    });
  }

  // CRUD operations for Content
  openEditContentModal() {
    if (!this.content) return;
    this.editingContent = this.content;
    this.showEditContentModal = true;
  }

  closeEditContentModal() {
    this.showEditContentModal = false;
    this.editingContent = null;
  }

  updateContent() {
    if (!this.editingContent || !this.selectedTopicId || !this.expandedChapterId) {
      this.errorMessage = 'Content is required';
      return;
    }

    this.contentService.updateContent(
      this.courseId,
      this.subjectId,
      this.expandedChapterId,
      this.selectedTopicId,
      this.editingContent
    ).subscribe({
      next: (response) => {
        // Update local content data
        this.content = response.content || this.editingContent;
        
        // Process content for LaTeX equations
        if (this.content) {
          this.processedContent = this.mathRendererService.processContent(this.content);
          this.needsMathJaxUpdate = true; // Mark for MathJax rendering
        }
        
        // Update topic has_content flag
        if (this.selectedTopic) {
          this.selectedTopic.has_content = true;
        }
        
        this.closeEditContentModal();
      },
      error: (err) => {
        console.error('Error updating content:', err);
        this.errorMessage = 'Failed to update content. Please try again.';
      }
    });
  }

  openDeleteContentConfirm() {
    this.showDeleteContentConfirm = true;
  }

  closeDeleteContentConfirm() {
    this.showDeleteContentConfirm = false;
  }

  deleteContent() {
    if (!this.selectedTopicId || !this.expandedChapterId) return;
    
    this.isDeletingContent = true;
    
    this.contentService.deleteContent(
      this.courseId,
      this.subjectId,
      this.expandedChapterId,
      this.selectedTopicId
    ).subscribe({
      next: () => {
        // Clear content
        this.content = null;
        
        // Update topic has_content flag
        if (this.selectedTopic) {
          this.selectedTopic.has_content = false;
        }
        
        this.closeDeleteContentConfirm();
        this.isDeletingContent = false;
      },
      error: (err) => {
        console.error('Error deleting content:', err);
        this.errorMessage = 'Failed to delete content. Please try again.';
        this.isDeletingContent = false;
      }
    });
  }

  // Modal methods for new chapter
  openNewChapterModal() {
    this.newChapterName = '';
    this.showNewChapterModal = true;
  }

  closeNewChapterModal() {
    this.showNewChapterModal = false;
    this.newChapterName = '';
  }

  createNewChapter() {
    if (!this.newChapterName || !this.newChapterName.trim()) {
      this.errorMessage = 'Chapter name is required';
      return;
    }
    
    this.isAddingChapter = true;
    this.errorMessage = '';
    
    this.chapterService.createChapter(this.courseId, this.subjectId, this.newChapterName.trim()).subscribe({
      next: (newChapter) => {
        this.chapters.push(newChapter);
        // Optionally expand the new chapter
        this.toggleChapter(newChapter.id);
        this.closeNewChapterModal();
        this.isAddingChapter = false;
      },
      error: (err) => {
        console.error('Error creating chapter:', err);
        this.errorMessage = 'Failed to create chapter. Please try again.';
        this.isAddingChapter = false;
      }
    });
  }

  // Modal methods for new topic
  openNewTopicModal() {
    if (!this.expandedChapterId) {
      this.errorMessage = 'Please select a chapter first';
      return;
    }
    this.newTopicName = '';
    this.showNewTopicModal = true;
  }

  closeNewTopicModal() {
    this.showNewTopicModal = false;
    this.newTopicName = '';
  }

  createNewTopic() {
    if (!this.expandedChapterId) {
      this.errorMessage = 'Please select a chapter first';
      return;
    }
    
    if (!this.newTopicName || !this.newTopicName.trim()) {
      this.errorMessage = 'Topic name is required';
      return;
    }
    
    this.isAddingTopic = true;
    this.errorMessage = '';
    
    this.topicService.createTopic(this.courseId, this.subjectId, this.expandedChapterId, this.newTopicName.trim()).subscribe({
      next: (newTopic) => {
        // Initialize topics array for this chapter if it doesn't exist
        if (!this.topics[this.expandedChapterId!]) {
          this.topics[this.expandedChapterId!] = [];
        }
        
        this.topics[this.expandedChapterId!].push(newTopic);
        
        // Update chapter to show it has topics
        const chapter = this.chapters.find(c => c.id === this.expandedChapterId);
        if (chapter) {
          chapter.has_topics = true;
        }
        
        // Select the new topic
        this.selectTopic(newTopic);
        this.closeNewTopicModal();
        this.isAddingTopic = false;
      },
      error: (err) => {
        console.error('Error creating topic:', err);
        this.errorMessage = 'Failed to create topic. Please try again.';
        this.isAddingTopic = false;
      }
    });
  }

  // Modal methods for new content (when no content exists yet)
  openNewContentModal() {
    if (!this.selectedTopicId || !this.expandedChapterId) {
      this.errorMessage = 'Please select a topic first';
      return;
    }
    this.newContentText = '';
    this.showNewContentModal = true;
  }

  closeNewContentModal() {
    this.showNewContentModal = false;
    this.newContentText = '';
  }

  createNewContent() {
    if (!this.selectedTopicId || !this.expandedChapterId) {
      this.errorMessage = 'Please select a topic first';
      return;
    }
    
    if (!this.newContentText || !this.newContentText.trim()) {
      this.errorMessage = 'Content is required';
      return;
    }
    
    this.isAddingContent = true;
    this.errorMessage = '';
    
    this.contentService.createContentManual(
      this.courseId,
      this.subjectId,
      this.expandedChapterId,
      this.selectedTopicId,
      this.newContentText.trim()
    ).subscribe({
      next: (response) => {
        // Update content display
        this.content = response.content || this.newContentText;
        
        // Process content for LaTeX equations
        if (this.content) {
          this.processedContent = this.mathRendererService.processContent(this.content);
          this.needsMathJaxUpdate = true; // Mark for MathJax rendering
        }
        
        // Mark topic as having content
        if (this.selectedTopic) {
          this.selectedTopic.has_content = true;
        }
        
        this.closeNewContentModal();
        this.isAddingContent = false;
      },
      error: (err) => {
        console.error('Error creating content:', err);
        this.errorMessage = 'Failed to create content. Please try again.';
        this.isAddingContent = false;
      }
    });
  }
}

import { Component, OnInit, OnDestroy, AfterViewChecked } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CourseService } from '../services/course.service';
import { SubjectService } from '../services/subject.service';
import { ChapterService } from '../services/chapter.service';
import { TopicService } from '../services/topic.service';
import { ContentService } from '../services/content.service';
import { MathRendererService } from '../services/math-renderer.service';
import { AuthService } from '../services/auth/auth.service';
import {
  faHome, faBook, faLayerGroup, faEye, faMagic,
  faBookOpen, faChevronRight, faChevronDown, faChevronUp,
  faFileAlt, faSpinner, faInfoCircle, faChevronLeft, faList,
  faEdit, faTrash, faPlus
} from '@fortawesome/free-solid-svg-icons';
import { Subscription } from 'rxjs';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { MarkdownModule } from 'ngx-markdown';

@Component({
  selector: 'app-course-content',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule, FontAwesomeModule, MarkdownModule],
  templateUrl: './course-content.component.html',
  styleUrls: ['./course-content.component.css'],
})
export class CourseContentComponent implements OnInit, OnDestroy, AfterViewChecked {
  editChapterForm: FormGroup;
  editTopicForm: FormGroup;
  editContentForm: FormGroup;
  newChapterForm: FormGroup;
  newTopicForm: FormGroup;
  newContentForm: FormGroup;

  courseId: number;
  courseName: string = '';
  subjectId: number;
  subjectName: string = '';
  subjects: any[] = [];
  chapters: any[] = [];
  expandedChapterId: number | null = null;
  topics: { [chapterId: number]: any[] } = {};
  selectedTopicId: number | null = null;
  selectedTopic: any = null;
  content: string | null = null;
  processedContent: string | null = null;
  isGeneratingChapters: boolean = false;
  isGeneratingTopics: boolean = false;
  generatingChapterId: number | null = null;
  isGeneratingContent: boolean = false;
  errorMessage: string = '';
  isSidebarOpen: boolean = true;
  isLoadingSubjects: boolean = false;
  isLoadingChapters: boolean = false;
  isLoadingContent: boolean = false;
  showEditChapterModal: boolean = false;
  showDeleteChapterModal: boolean = false;
  showEditTopicModal: boolean = false;
  showDeleteTopicModal: boolean = false;
  showEditContentModal: boolean = false;
  showDeleteContentConfirm: boolean = false;
  isDeletingChapter: boolean = false;
  isDeletingTopic: boolean = false;
  isDeletingContent: boolean = false;
  showNewChapterModal: boolean = false;
  showNewTopicModal: boolean = false;
  showNewContentModal: boolean = false;
  isAddingChapter: boolean = false;
  isAddingTopic: boolean = false;
  isAddingContent: boolean = false;

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

  private subscriptions = new Subscription();
  private needsMathJaxUpdate = false;
  private editingChapter: any = null;
  private editingTopic: any = null;

  constructor(
    private courseService: CourseService,
    private subjectService: SubjectService,
    private chapterService: ChapterService,
    private topicService: TopicService,
    private contentService: ContentService,
    public mathRendererService: MathRendererService,
    private route: ActivatedRoute,
    private router: Router,
    private formBuilder: FormBuilder
  ) {
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
    this.subjectId = +this.route.snapshot.paramMap.get('subject_id')!;

    this.editChapterForm = this.formBuilder.group({
      name: ['', Validators.required]
    });

    this.editTopicForm = this.formBuilder.group({
      name: ['', Validators.required]
    });

    this.editContentForm = this.formBuilder.group({
      content: ['', Validators.required]
    });

    this.newChapterForm = this.formBuilder.group({
      name: ['', Validators.required]
    });

    this.newTopicForm = this.formBuilder.group({
      name: ['', Validators.required]
    });

    this.newContentForm = this.formBuilder.group({
      content: ['', Validators.required]
    });
  }

  ngOnInit() {
    this.loadInitialData();
    
    this.subscriptions.add(
      this.route.paramMap.subscribe(params => {
        const newCourseId = +params.get('course_id')!;
        const newSubjectId = +params.get('subject_id')!;
        const topicId = params.get('topic_id');
        
        if (newCourseId !== this.courseId || newSubjectId !== this.subjectId) {
          this.courseId = newCourseId;
          this.subjectId = newSubjectId;
          this.loadInitialData();
        }
        
        if (topicId) {
          this.selectTopicById(+topicId);
        }
      })
    );
    
    this.adjustSidebarForScreenSize();
    window.addEventListener('resize', this.adjustSidebarForScreenSize.bind(this));
  }
  
  ngOnDestroy() {
    this.subscriptions.unsubscribe();
    window.removeEventListener('resize', this.adjustSidebarForScreenSize.bind(this));
  }
  
  ngAfterViewChecked() {
    if (this.needsMathJaxUpdate) {
      this.mathRendererService.renderMathJax();
      this.needsMathJaxUpdate = false;
      
      setTimeout(() => {
        this.mathRendererService.renderMathJax();
      }, 500);
    }
  }
  
  loadInitialData() {
    this.isLoadingSubjects = true;
    
    this.subscriptions.add(
      this.courseService.getCourseDetails(this.courseId).subscribe({
        next: (course) => {
          this.courseName = course.name;
        },
        error: (err) => console.error('Error loading course details:', err)
      })
    );
    
    this.subscriptions.add(
      this.subjectService.getSubjectDetails(this.courseId, this.subjectId).subscribe({
        next: (subject) => {
          this.subjectName = subject.name;
        },
        error: (err) => console.error('Error loading subject details:', err)
      })
    );
    
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
          
          const chapterWithTopics = this.chapters.find(c => c.has_topics);
          if (chapterWithTopics) {
            this.toggleChapter(chapterWithTopics.id);
          } else if (this.chapters.length > 0) {
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
    if (this.expandedChapterId === chapterId) {
      this.expandedChapterId = null;
      return;
    }
    
    this.expandedChapterId = chapterId;
    
    if (this.topics[chapterId]) {
      return;
    }
    
    this.loadTopics(chapterId);
  }
  
  loadTopics(chapterId: number) {
    const chapter = this.chapters.find(c => c.id === chapterId);
    
    if (!chapter?.has_topics) {
      this.generateTopics(chapterId);
      return;
    }
    
    this.subscriptions.add(
      this.topicService.getTopics(this.courseId, this.subjectId, chapterId).subscribe({
        next: (topics) => {
          this.topics[chapterId] = topics;
          
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
    
    this.updateUrlWithTopicId(topic.id);
    
    if (window.innerWidth < 768) {
      this.isSidebarOpen = false;
      
      setTimeout(() => {
        window.scrollTo(0, 0);
      }, 100);
    }
  }
  
  selectTopicById(topicId: number) {
    for (const chapterId in this.topics) {
      const topic = this.topics[chapterId].find(t => t.id === topicId);
      if (topic) {
        this.expandedChapterId = +chapterId;
        this.selectTopic(topic);
        return;
      }
    }
    
    this.findChapterForTopic(topicId);
  }
  
  findChapterForTopic(topicId: number) {
    const checkNextChapter = (index: number) => {
      if (index >= this.chapters.length) {
        console.error('Topic not found in any chapter:', topicId);
        return;
      }
      
      const chapter = this.chapters[index];
      
      this.topicService.getTopics(this.courseId, this.subjectId, chapter.id).subscribe({
        next: (topics) => {
          const topic = topics.find((t: any) => t.id === topicId);
          if (topic) {
            this.topics[chapter.id] = topics;
            this.expandedChapterId = chapter.id;
            this.selectTopic(topic);
          } else {
            checkNextChapter(index + 1);
          }
        },
        error: () => {
          checkNextChapter(index + 1);
        }
      });
    };
    
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
          
          if (content) {
            this.processedContent = this.mathRendererService.processContent(content);
            this.needsMathJaxUpdate = true;
          }
          
          this.isLoadingContent = false;
          
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
          this.loadChapters();
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
          if (chapter) {
            chapter.has_topics = true;
          }
          
          this.topicService.getTopics(this.courseId, this.subjectId, chapterId).subscribe({
            next: (topics) => {
              this.topics[chapterId] = topics;
              this.isGeneratingTopics = false;
              this.generatingChapterId = null;
              
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
          if (this.selectedTopic) {
            this.selectedTopic.has_content = true;
          }
          
          this.contentService.getContent(
            this.courseId, 
            this.subjectId, 
            this.expandedChapterId!, 
            this.selectedTopicId!
          ).subscribe({
            next: (content) => {
              this.content = content;
              
              if (content) {
                this.processedContent = this.mathRendererService.processContent(content);
                this.needsMathJaxUpdate = true;
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
    const url = `/courses/${this.courseId}/subjects/${this.subjectId}/content/${topicId}`;
    window.history.replaceState({}, '', url);
  }
  
  toggleSidebar() {
    this.isSidebarOpen = !this.isSidebarOpen;
    
    if (!this.isSidebarOpen && window.innerWidth < 768) {
      setTimeout(() => {
        const contentArea = document.querySelector('.flex-1.overflow-y-auto');
        if (contentArea) {
          contentArea.scrollTop = 0;
        }
      }, 300);
    }

    if (this.isSidebarOpen && window.innerWidth < 768) {
      setTimeout(() => {
        const sidebar = document.querySelector('.bg-gray-900.text-white');
        if (sidebar) {
          sidebar.scrollTop = 0;
        }
      }, 100);
    }
  }
  
  adjustSidebarForScreenSize() {
    if (window.innerWidth < 768) {
      this.isSidebarOpen = false;
    } else {
      this.isSidebarOpen = true;
    }
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

  getChapterNameById(chapterId: number | null): string {
    if (!chapterId || !this.chapters) return '';
    const chapter = this.chapters.find(c => c.id === chapterId);
    return chapter ? chapter.name : 'Course Outline';
  }

  openEditChapterModal(chapter: any, event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    this.editingChapter = { ...chapter };
    this.editChapterForm.setValue({ name: chapter.name });
    this.showEditChapterModal = true;
  }

  closeEditChapterModal() {
    this.showEditChapterModal = false;
    this.editingChapter = null;
    this.editChapterForm.reset();
  }

  updateChapter() {
    if (this.editChapterForm.invalid) {
      this.errorMessage = 'Chapter name is required';
      return;
    }

    this.chapterService.updateChapter(
      this.courseId,
      this.subjectId,
      this.editingChapter.id,
      this.editChapterForm.value.name
    ).subscribe({
      next: () => {
        const index = this.chapters.findIndex(c => c.id === this.editingChapter.id);
        if (index !== -1) {
          this.chapters[index].name = this.editChapterForm.value.name;
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
      event.stopPropagation();
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
        this.chapters = this.chapters.filter(c => c.id !== this.editingChapter.id);
        
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

  openEditTopicModal(topic: any, event?: Event) {
    if (event) {
      event.stopPropagation();
    }
    this.editingTopic = { ...topic };
    this.editTopicForm.setValue({ name: topic.name });
    this.showEditTopicModal = true;
  }

  closeEditTopicModal() {
    this.showEditTopicModal = false;
    this.editingTopic = null;
    this.editTopicForm.reset();
  }

  updateTopic() {
    if (this.editTopicForm.invalid || !this.expandedChapterId) {
      this.errorMessage = 'Topic name is required';
      return;
    }

    this.topicService.updateTopic(
      this.courseId,
      this.subjectId,
      this.expandedChapterId,
      this.editingTopic.id,
      this.editTopicForm.value.name
    ).subscribe({
      next: () => {
        const topicsArray = this.topics[this.expandedChapterId!];
        if (topicsArray) {
          const index = topicsArray.findIndex((t: any) => t.id === this.editingTopic.id);
          if (index !== -1) {
            topicsArray[index].name = this.editTopicForm.value.name;
            
            if (this.selectedTopicId === this.editingTopic.id) {
              this.selectedTopic.name = this.editTopicForm.value.name;
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
      event.stopPropagation();
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
        if (this.topics[this.expandedChapterId!]) {
          this.topics[this.expandedChapterId!] = this.topics[this.expandedChapterId!]
            .filter((t: any) => t.id !== this.editingTopic.id);
        }
        
        if (this.selectedTopicId === this.editingTopic.id) {
          this.selectedTopicId = null;
          this.selectedTopic = null;
          this.content = null;
          
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

  openEditContentModal() {
    if (!this.content) return;
    this.editContentForm.setValue({ content: this.content });
    this.showEditContentModal = true;
  }

  closeEditContentModal() {
    this.showEditContentModal = false;
    this.editContentForm.reset();
  }

  updateContent() {
    if (this.editContentForm.invalid || !this.selectedTopicId || !this.expandedChapterId) {
      this.errorMessage = 'Content is required';
      return;
    }

    const newContent = this.editContentForm.value.content;
    this.contentService.updateContent(
      this.courseId,
      this.subjectId,
      this.expandedChapterId,
      this.selectedTopicId,
      newContent
    ).subscribe({
      next: (response) => {
        this.content = response.content || newContent;
        
        if (this.content) {
          this.processedContent = this.mathRendererService.processContent(this.content);
          this.needsMathJaxUpdate = true;
        }
        
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
        this.content = null;
        
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

  openNewChapterModal() {
    this.newChapterForm.reset();
    this.showNewChapterModal = true;
  }

  closeNewChapterModal() {
    this.showNewChapterModal = false;
  }

  createNewChapter() {
    if (this.newChapterForm.invalid) {
      this.errorMessage = 'Chapter name is required';
      return;
    }
    
    this.isAddingChapter = true;
    this.errorMessage = '';
    
    const newChapterName = this.newChapterForm.value.name;
    this.chapterService.createChapter(this.courseId, this.subjectId, newChapterName).subscribe({
      next: (newChapter) => {
        this.chapters.push(newChapter);
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

  openNewTopicModal() {
    if (!this.expandedChapterId) {
      this.errorMessage = 'Please select a chapter first';
      return;
    }
    this.newTopicForm.reset();
    this.showNewTopicModal = true;
  }

  closeNewTopicModal() {
    this.showNewTopicModal = false;
  }

  createNewTopic() {
    if (!this.expandedChapterId) {
      this.errorMessage = 'Please select a chapter first';
      return;
    }
    
    if (this.newTopicForm.invalid) {
      this.errorMessage = 'Topic name is required';
      return;
    }
    
    this.isAddingTopic = true;
    this.errorMessage = '';
    
    const newTopicName = this.newTopicForm.value.name;
    this.topicService.createTopic(this.courseId, this.subjectId, this.expandedChapterId, newTopicName).subscribe({
      next: (newTopic) => {
        if (!this.topics[this.expandedChapterId!]) {
          this.topics[this.expandedChapterId!] = [];
        }
        
        this.topics[this.expandedChapterId!].push(newTopic);
        
        const chapter = this.chapters.find(c => c.id === this.expandedChapterId);
        if (chapter) {
          chapter.has_topics = true;
        }
        
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

  openNewContentModal() {
    if (!this.selectedTopicId || !this.expandedChapterId) {
      this.errorMessage = 'Please select a topic first';
      return;
    }
    this.newContentForm.reset();
    this.showNewContentModal = true;
  }

  closeNewContentModal() {
    this.showNewContentModal = false;
  }

  createNewContent() {
    if (!this.selectedTopicId || !this.expandedChapterId) {
      this.errorMessage = 'Please select a topic first';
      return;
    }
    
    if (this.newContentForm.invalid) {
      this.errorMessage = 'Content is required';
      return;
    }
    
    this.isAddingContent = true;
    this.errorMessage = '';
    
    const newContent = this.newContentForm.value.content;
    this.contentService.createContentManual(
      this.courseId,
      this.subjectId,
      this.expandedChapterId,
      this.selectedTopicId,
      newContent
    ).subscribe({
      next: (response) => {
        this.content = response.content || newContent;
        
        if (this.content) {
          this.processedContent = this.mathRendererService.processContent(this.content);
          this.needsMathJaxUpdate = true;
        }
        
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

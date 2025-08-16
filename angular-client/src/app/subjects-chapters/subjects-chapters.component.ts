import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';
import { SubjectService } from '../services/subject.service';
import { ChapterService } from '../services/chapter.service';
import { TopicService } from '../services/topic.service';
import { 
  faHome, faBook, faLayerGroup, faEye, faMagic, 
  faBookOpen, faInfoCircle, faChevronRight 
} from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-subjects-chapters',
  standalone: false,
  templateUrl: './subjects-chapters.component.html',
  styleUrls: ['./subjects-chapters.component.css']
})
export class SubjectsChaptersComponent implements OnInit {
  // FontAwesome icons
  faHome = faHome;
  faBook = faBook;
  faLayerGroup = faLayerGroup;
  faEye = faEye;
  faMagic = faMagic;
  faBookOpen = faBookOpen;
  faInfoCircle = faInfoCircle;
  faChevronRight = faChevronRight;
  
  subjects: any[] = [];
  chapters: any[] = [];
  topics: { [chapterId: number]: any[] } = {}; // Store topics for each chapter
  courseId: number;
  courseName: string = '';
  selectedSubjectId: number | null = null;
  selectedSubjectName: string = '';
  selectedChapterId: number | null = null;
  selectedChapterName: string = '';
  isGenerating: boolean = false;
  generatingSubjectId: number | null = null;
  generatingChapterId: number | null = null;
  showTopics: boolean = false;

  constructor(
    private courseService: CourseService,
    private subjectService: SubjectService,
    private chapterService: ChapterService,
    private topicService: TopicService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
  }

  ngOnInit() {
    // Fetch course details to get course name
    this.courseService.getCourseDetails(this.courseId).subscribe((course: any) => {
      this.courseName = course.name;
    });

    // Fetch subjects for the given course
    this.subjectService.getSubjects(this.courseId).subscribe((subjects: any[]) => {
      this.subjects = subjects;
      console.log('Loaded subjects:', subjects);
    });
  }

  viewChapters(subjectId: number) {
    // Set the selected subject ID and name
    this.selectedSubjectId = subjectId;
    const selectedSubject = this.subjects.find(subject => subject.id === subjectId);
    this.selectedSubjectName = selectedSubject ? selectedSubject.name : '';

    // Fetch chapters for the selected subject
    this.chapterService.getChapters(this.courseId, subjectId).subscribe((chapters: any[]) => {
      this.chapters = chapters;
      console.log('Loaded chapters:', chapters);
      
      // Reset topics when loading new chapters
      this.topics = {};
      this.selectedChapterId = null;
      this.showTopics = false;
    });

    const chaptersSection = document.getElementById("chaptersSection");
    if (chaptersSection) {
      chaptersSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  generateChapters(subjectId: number) {
    // Show loading state
    this.generatingSubjectId = subjectId;
    this.isGenerating = true;
    
    // Get selected subject to determine if updating or generating
    const subject = this.subjects.find(s => s.id === subjectId);
    const actionVerb = subject && subject.has_chapters ? 'updating' : 'generating';
    
    // Trigger chapter generation for the subject and refresh chapters
    this.chapterService.generateChapters(this.courseId, subjectId).subscribe({
      next: () => {
        // Mark this subject as having chapters in our local data
        if (subject) {
          subject.has_chapters = true;
        }
        this.viewChapters(subjectId); // Refresh the chapter list after generating
        this.isGenerating = false;
        this.generatingSubjectId = null;
      },
      error: (error) => {
        console.error(`Error ${actionVerb} chapters:`, error);
        this.isGenerating = false;
        this.generatingSubjectId = null;
      }
    });
  }

  viewTopics(chapterId: number) {
    if (!this.selectedSubjectId) {
      console.error('No subject selected');
      return;
    }
    
    this.selectedChapterId = chapterId;
    const selectedChapter = this.chapters.find(chapter => chapter.id === chapterId);
    this.selectedChapterName = selectedChapter ? selectedChapter.name : '';

    // Using non-null assertion since we check selectedSubjectId above
    const subjectId = this.selectedSubjectId;
    
    // Check if we already loaded topics for this chapter
    if (this.topics[chapterId]) {
      this.showTopics = true;
      const topicsSection = document.getElementById("topicsSection");
      if (topicsSection) {
        topicsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
      return;
    }
    
    // Fetch topics for the selected chapter
    this.topicService.getTopics(this.courseId, subjectId, chapterId).subscribe({
      next: (topics: any[]) => {
        if (topics && topics.length > 0) {
          console.log('Found topics:', topics);
          this.topics[chapterId] = topics;
          this.showTopics = true;
          
          // Scroll to topics section
          const topicsSection = document.getElementById("topicsSection");
          if (topicsSection) {
            topicsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        } else {
          console.log('No topics found, generating topics first');
          this.generateTopics(chapterId);
        }
      },
      error: (error) => {
        console.error('Error getting topics:', error);
        // If failed to get topics, try generating them
        this.generateTopics(chapterId);
      }
    });
  }

  generateTopics(chapterId: number) {
    if (!this.selectedSubjectId) {
      console.error('No subject selected');
      return;
    }
    
    // Show loading state
    this.generatingChapterId = chapterId;
    this.isGenerating = true;
    
    // Store the subject ID in a local variable to ensure it's not null
    const subjectId = this.selectedSubjectId;
    
    // Get selected chapter to determine if updating or generating
    const chapter = this.chapters.find(c => c.id === chapterId);
    const actionVerb = chapter && chapter.has_topics ? 'updating' : 'generating';
    
    this.topicService.generateTopics(this.courseId, subjectId, chapterId).subscribe({
      next: () => {
        // Mark this chapter as having topics in our local data
        if (chapter) {
          chapter.has_topics = true;
        }
        
        // Once topics are generated, get the topics
        this.topicService.getTopics(this.courseId, subjectId, chapterId).subscribe({
          next: (topics: any[]) => {
            this.isGenerating = false;
            this.generatingChapterId = null;
            
            if (topics && topics.length > 0) {
              // Store the topics and show them
              this.topics[chapterId] = topics;
              this.showTopics = true;
              this.selectedChapterId = chapterId; // Ensure selectedChapterId is set
              
              // Scroll to topics section
              const topicsSection = document.getElementById("topicsSection");
              if (topicsSection) {
                topicsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }
            } else {
              console.error('No topics were generated');
            }
          },
          error: (error) => {
            console.error('Error getting topics after generation:', error);
            this.isGenerating = false;
            this.generatingChapterId = null;
          }
        });
      },
      error: (error) => {
        console.error(`Error ${actionVerb} topics:`, error);
        this.isGenerating = false;
        this.generatingChapterId = null;
      }
    });
  }
  
  viewContent(topicId: number) {
    if (!this.selectedSubjectId || !this.selectedChapterId) {
      console.error('Subject or chapter not selected');
      return;
    }
    
    // Navigate to the new unified content view
    this.router.navigate([
      `/courses/${this.courseId}/subjects/${this.selectedSubjectId}/content/${topicId}`
    ]);
  }
}

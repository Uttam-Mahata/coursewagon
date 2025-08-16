import { Component, OnInit, OnDestroy } from '@angular/core';
import { CourseService } from '../services/course.service';
import { SubjectService } from '../services/subject.service';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth/auth.service';
import { faHome, faBook, faPlus, faExclamationTriangle, faExclamationCircle, faMagic, faEye, faEdit, faTrash, faImage, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-courses',
    templateUrl: './courses.component.html',
    styleUrls: ['./courses.component.css'],
    standalone: false
})
export class CoursesComponent implements OnInit, OnDestroy {
  // FontAwesome icons
  faHome = faHome;
  faBook = faBook;
  faPlus = faPlus;
  faExclamationTriangle = faExclamationTriangle;
  faExclamationCircle = faExclamationCircle;
  faMagic = faMagic;
  faEye = faEye;
  faEdit = faEdit;
  faTrash = faTrash;
  faImage = faImage;
  faSpinner = faSpinner;

  courses: any[] = [];
  isLoading: boolean = true;
  errorMessage: string | null = null;
  
  // CRUD modals
  showEditModal: boolean = false;
  showDeleteModal: boolean = false;
  
  // CRUD data
  editingCourse: any = null;
  deletingCourse: any = null;

  // Track subscriptions to prevent memory leaks
  private subscriptions: Subscription[] = [];

  constructor(
    private courseService: CourseService, 
    private subjectService: SubjectService,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit() {
    // Subscribe to auth changes to detect new logins
    this.subscriptions.push(
      this.authService.currentUser$.subscribe(user => {
        if (user) {
          // Force refresh courses when user changes
          this.loadCourses(true);
        } else {
          // Clear courses when logged out
          this.courses = [];
        }
      })
    );
    
    // Initial load
    this.loadCourses();
  }
  
  ngOnDestroy() {
    // Clean up subscriptions
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  loadCourses(forceRefresh = false) {
    this.isLoading = true;
    this.errorMessage = null;
    
    this.subscriptions.push(
      this.courseService.getMyCourses(forceRefresh).subscribe({
        next: (courses: any[]) => {
          this.courses = courses;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error fetching courses:', error);
          this.errorMessage = 'Failed to load courses. Please try again later.';
          this.isLoading = false;
        }
      })
    );
  }

  generateSubjects(courseId: number) {
    const course = this.courses.find(c => c.id === courseId);
    const actionVerb = course && course.has_subjects ? 'updating' : 'generating';
    
    // Show that we're generating content for this course
    course.isGenerating = true;
    
    this.subjectService.generateSubjects(courseId).subscribe({
      next: () => {
        if (course) {
          // Update the local course data to reflect that it now has subjects
          course.has_subjects = true;
          course.isGenerating = false;
        }
        
        // Navigate only if we're generating for the first time, otherwise stay on the page
        if (actionVerb === 'generating') {
          this.router.navigate([`/courses/${courseId}/subjects`]);
        }
      },
      error: (error) => {
        if (course) {
          course.isGenerating = false;
        }
        console.error(`Error ${actionVerb} subjects:`, error);
        if (error.status === 403) {
          this.errorMessage = 'You need to set your Google API key in your profile first.';
        } else {
          this.errorMessage = `Failed to ${actionVerb.replace('ing', '')} subjects. Please try again.`;
        }
      }
    });
  }
  
  viewSubjects(courseId: number) {
    // Navigate to the new subjects component
    this.router.navigate([`/courses/${courseId}/subjects`]);
  }
  
  navigateToCourseCreation() {
    this.router.navigate(['/create-course']);
  }
  
  navigateToProfile() {
    this.router.navigate(['/profile']);
  }

  // Course CRUD Operations
  
  // Update
  openEditModal(course: any) {
    this.editingCourse = { ...course };
    this.showEditModal = true;
  }

  closeEditModal() {
    this.showEditModal = false;
    this.editingCourse = null;
  }

  updateCourse() {
    if (!this.editingCourse || !this.editingCourse.name.trim()) {
      this.errorMessage = 'Course name is required';
      return;
    }

    this.courseService.updateCourse(
      this.editingCourse.id, 
      this.editingCourse.name, 
      this.editingCourse.description
    ).subscribe({
      next: () => {
        this.closeEditModal();
        this.loadCourses(); // Refresh courses list
      },
      error: (err) => {
        console.error('Error updating course:', err);
        this.errorMessage = 'Failed to update course. Please try again.';
      }
    });
  }

  // Delete
  openDeleteModal(course: any) {
    this.deletingCourse = course;
    this.showDeleteModal = true;
  }

  closeDeleteModal() {
    this.showDeleteModal = false;
    this.deletingCourse = null;
  }

  deleteCourse() {
    if (!this.deletingCourse) {
      return;
    }

    this.courseService.deleteCourse(this.deletingCourse.id).subscribe({
      next: () => {
        this.closeDeleteModal();
        this.loadCourses(); // Refresh courses list
      },
      error: (err) => {
        console.error('Error deleting course:', err);
        this.errorMessage = 'Failed to delete course. Please try again.';
      }
    });
  }

  generateCourseImage(courseId: number, event?: Event) {
    // Stop event propagation if provided
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }
    
    // Find the course and mark it as generating an image
    const course = this.courses.find(c => c.id === courseId);
    if (course) {
      course.isGeneratingImage = true;
    }
    
    this.courseService.generateCourseImage(courseId).subscribe({
      next: (updatedCourse) => {
        console.log('Received updated course with image:', updatedCourse);
        
        // Update the course in our array with new image URL
        const index = this.courses.findIndex(c => c.id === courseId);
        if (index !== -1 && updatedCourse && updatedCourse.image_url) {
          // Add timestamp to URL to prevent caching issues
          this.courses[index].image_url = updatedCourse.image_url + '?t=' + new Date().getTime();
          this.courses[index].isGeneratingImage = false;
          console.log('Updated course image URL:', this.courses[index].image_url);
        } else {
          console.warn('Failed to update course image - missing data:', updatedCourse);
          if (course) {
            course.isGeneratingImage = false;
          }
        }
      },
      error: (error) => {
        console.error('Error generating course image:', error);
        
        // Update status regardless of error
        if (course) {
          course.isGeneratingImage = false;
        }
        
        if (error.status === 403) {
          this.errorMessage = 'You need to set your Google API key in your profile first.';
        } else {
          this.errorMessage = 'Failed to generate image. Please try again.';
        }
      }
    });
  }
}

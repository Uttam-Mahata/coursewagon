import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CourseService } from '../services/course.service';
import { SubjectService } from '../services/subject.service';
import { faHome, faBook, faLayerGroup, faEye, faMagic, faInfoCircle, faChevronRight, faEdit, faTrash, faPlus, faImage, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { AuthService } from '../services/auth/auth.service';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

@Component({
  selector: 'app-subjects',
  templateUrl: './subjects.component.html',
  styleUrls: ['./subjects.component.css'],
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule, FontAwesomeModule]
})
export class SubjectsComponent implements OnInit {
  createSubjectForm: FormGroup;
  editSubjectForm: FormGroup;

  faHome = faHome;
  faBook = faBook;
  faLayerGroup = faLayerGroup;
  faEye = faEye;
  faMagic = faMagic;
  faInfoCircle = faInfoCircle;
  faChevronRight = faChevronRight;
  faEdit = faEdit;
  faTrash = faTrash;
  faPlus = faPlus;
  faImage = faImage;
  faSpinner = faSpinner;
  
  courseId: number;
  courseName: string = '';
  subjects: any[] = [];
  
  isGenerating: boolean = false;
  generatingSubjectId: number | null = null;
  errorMessage: string | null = null;
  isLoading: boolean = true;
  userHasApiKey: boolean = false;
  
  showEditSubjectModal: boolean = false;
  showDeleteSubjectModal: boolean = false;
  showCreateSubjectModal: boolean = false;
  isDeletingSubject: boolean = false;

  editingSubject: any = null;

  constructor(
    private courseService: CourseService,
    private subjectService: SubjectService,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private formBuilder: FormBuilder
  ) {
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
    this.createSubjectForm = this.formBuilder.group({
      name: ['', Validators.required]
    });
    this.editSubjectForm = this.formBuilder.group({
      name: ['', Validators.required]
    });
  }

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.userHasApiKey = !!user?.has_api_key;
    });
    
    this.courseService.getCourseDetails(this.courseId).subscribe({
      next: (course) => {
        this.courseName = course.name;
      },
      error: (err) => console.error('Error loading course details:', err)
    });

    this.loadSubjects();
  }

  loadSubjects() {
    this.isLoading = true;
    this.errorMessage = null;
    
    this.subjectService.getSubjects(this.courseId).subscribe({
      next: (subjects) => {
        this.subjects = subjects;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading subjects:', err);
        this.errorMessage = 'Failed to load subjects. Please try again.';
        this.isLoading = false;
      }
    });
  }
  
  generateSubjects() {
    this.isGenerating = true;
    this.errorMessage = null;
    
    this.subjectService.generateSubjects(this.courseId).subscribe({
      next: () => {
        this.isGenerating = false;
        this.loadSubjects();
      },
      error: (error) => {
        this.isGenerating = false;
        console.error('Error generating subjects:', error);
        if (error.status === 403) {
          this.errorMessage = 'You need to set your Google API key in your profile first.';
        } else {
          this.errorMessage = 'Failed to generate subjects. Please try again.';
        }
      }
    });
  }
  
  generateSubjectImage(subjectId: number, event?: Event) {
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }
    
    if (!this.userHasApiKey) {
      this.errorMessage = 'You need to set your Google API key in your profile first.';
      return;
    }
    
    const subject = this.subjects.find(s => s.id === subjectId);
    if (subject) {
      subject.isGeneratingImage = true;
    }
    
    this.subjectService.generateSubjectImage(this.courseId, subjectId).subscribe({
      next: (updatedSubject) => {
        const index = this.subjects.findIndex(s => s.id === subjectId);
        if (index !== -1) {
          const timestamp = new Date().getTime();
          const imageUrlWithTimestamp = updatedSubject.image_url.includes('?') 
            ? `${updatedSubject.image_url}&t=${timestamp}` 
            : `${updatedSubject.image_url}?t=${timestamp}`;

          this.subjects[index] = { 
            ...this.subjects[index],
            image_url: imageUrlWithTimestamp,
            isGeneratingImage: false
          };
          
          this.subjects = [...this.subjects];
        }
      },
      error: (error) => {
        console.error('Error generating subject image:', error);
        if (subject) {
          subject.isGeneratingImage = false;
        }
        if (error.status === 403) {
          this.errorMessage = 'You need to set your Google API key in your profile first.';
        } else {
          this.errorMessage = 'Failed to generate image. Please try again.';
        }
      }
    });
  }
  
  generateAllSubjectImages() {
    if (!this.userHasApiKey) {
      this.errorMessage = 'You need to set your Google API key in your profile first.';
      return;
    }
    
    this.subjects.forEach(subject => {
      subject.isGeneratingImage = true;
    });
    
    this.subjectService.generateAllSubjectImages(this.courseId).subscribe({
      next: (response) => {
        if (response && response.results && Array.isArray(response.results)) {
          const timestamp = new Date().getTime();
          
          const updatedSubjectsMap = new Map();
          response.results.forEach((updatedSubject: any) => {
            if (updatedSubject && updatedSubject.id && updatedSubject.image_url) {
              const imageUrlWithTimestamp = updatedSubject.image_url.includes('?') 
                ? `${updatedSubject.image_url}&t=${timestamp}` 
                : `${updatedSubject.image_url}?t=${timestamp}`;
              
              updatedSubjectsMap.set(updatedSubject.id, {
                ...updatedSubject,
                image_url: imageUrlWithTimestamp
              });
            }
          });
          
          this.subjects = this.subjects.map(subject => {
            const updatedSubject = updatedSubjectsMap.get(subject.id);
            if (updatedSubject) {
              return { ...subject, ...updatedSubject, isGeneratingImage: false };
            }
            return { ...subject, isGeneratingImage: false };
          });
        } else {
          this.subjects = this.subjects.map(subject => ({ 
            ...subject, 
            isGeneratingImage: false 
          }));
        }
      },
      error: (error) => {
        console.error('Error generating all subject images:', error);
        this.subjects = this.subjects.map(subject => ({ 
          ...subject, 
          isGeneratingImage: false 
        }));
        
        if (error.status === 403) {
          this.errorMessage = 'You need to set your Google API key in your profile first.';
        } else {
          this.errorMessage = 'Failed to generate images. Please try again.';
        }
      }
    });
  }
  
  viewSubjectContent(subjectId: number) {
    this.router.navigate([`/courses/${this.courseId}/subjects/${subjectId}/content`]);
  }
  
  goBack() {
    this.router.navigate(['/courses']);
  }
  
  openCreateSubjectModal() {
    this.createSubjectForm.reset();
    this.showCreateSubjectModal = true;
  }
  
  closeCreateSubjectModal() {
    this.showCreateSubjectModal = false;
  }
  
  submitNewSubject() {
    if (this.createSubjectForm.invalid) {
      this.errorMessage = 'Subject name is required';
      return;
    }
    
    const newSubjectName = this.createSubjectForm.value.name;
    this.subjectService.createSubject(this.courseId, newSubjectName).subscribe({
      next: (newSubject) => {
        this.subjects.push(newSubject);
        this.closeCreateSubjectModal();
      },
      error: (err) => {
        console.error('Error creating subject:', err);
        this.errorMessage = 'Failed to create subject. Please try again.';
      }
    });
  }
  
  openEditSubjectModal(subject: any) {
    this.editingSubject = { ...subject };
    this.editSubjectForm.setValue({ name: subject.name });
    this.showEditSubjectModal = true;
  }

  closeEditSubjectModal() {
    this.showEditSubjectModal = false;
    this.editingSubject = null;
    this.editSubjectForm.reset();
  }

  updateSubject() {
    if (this.editSubjectForm.invalid) {
      this.errorMessage = 'Subject name is required';
      return;
    }

    const updatedName = this.editSubjectForm.value.name;
    this.subjectService.updateSubject(
      this.courseId,
      this.editingSubject.id,
      updatedName
    ).subscribe({
      next: () => {
        const index = this.subjects.findIndex(s => s.id === this.editingSubject.id);
        if (index !== -1) {
          this.subjects[index].name = updatedName;
        }
        this.closeEditSubjectModal();
      },
      error: (err) => {
        console.error('Error updating subject:', err);
        this.errorMessage = 'Failed to update subject. Please try again.';
      }
    });
  }
  
  openDeleteSubjectModal(subject: any) {
    this.editingSubject = subject;
    this.showDeleteSubjectModal = true;
  }

  closeDeleteSubjectModal() {
    this.showDeleteSubjectModal = false;
    this.editingSubject = null;
  }

  deleteSubject() {
    if (!this.editingSubject) return;
    
    this.isDeletingSubject = true;
    
    this.subjectService.deleteSubject(
      this.courseId,
      this.editingSubject.id
    ).subscribe({
      next: () => {
        this.subjects = this.subjects.filter(s => s.id !== this.editingSubject.id);
        this.closeDeleteSubjectModal();
        this.isDeletingSubject = false;
      },
      error: (err) => {
        console.error('Error deleting subject:', err);
        this.errorMessage = 'Failed to delete subject. Please try again.';
        this.isDeletingSubject = false;
      }
    });
  }
}

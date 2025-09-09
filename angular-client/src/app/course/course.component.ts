import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CourseService } from '../services/course.service';
import { AuthService } from '../services/auth/auth.service';
import { 
  faExclamationTriangle, faExclamationCircle, faBook, faMagic, 
  faChalkboardTeacher, faBrain, faTasks, faMobileAlt, faClock, faKey,
  faMicrophone, faStop, faPlay, faTrash, faCheckCircle
} from '@fortawesome/free-solid-svg-icons';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
    selector: 'app-course',
    templateUrl: './course.component.html',
    styleUrls: ['./course.component.css'],
    standalone: false
})
export class CourseComponent implements OnInit {
  courseForm: FormGroup;
  isLoading: boolean = false;
  errorMessage: string = '';

  faExclamationTriangle = faExclamationTriangle;
  faExclamationCircle = faExclamationCircle;
  faBook = faBook;
  faMagic = faMagic;
  faChalkboardTeacher = faChalkboardTeacher;
  faBrain = faBrain;
  faTasks = faTasks;
  faMobileAlt = faMobileAlt;
  faClock = faClock;
  faKey = faKey;
  faMicrophone = faMicrophone;
  faStop = faStop;
  faPlay = faPlay;
  faTrash = faTrash;
  faCheckCircle = faCheckCircle;

  isRecording: boolean = false;
  mediaRecorder: MediaRecorder | null = null;
  audioBlob: Blob | null = null;
  audioChunks: BlobPart[] = [];

  constructor(
    private courseService: CourseService, 
    private router: Router,
    private authService: AuthService,
    private formBuilder: FormBuilder
  ) {
    this.courseForm = this.formBuilder.group({
      courseName: ['', Validators.required]
    });
  }

  ngOnInit() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn('Audio recording not supported in this browser');
    }
  }

  generateCourse() {
    if (this.courseForm.invalid) {
      this.errorMessage = 'Course name is required';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const courseName = this.courseForm.value.courseName;
    this.courseService.addCourse(courseName).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/courses']);
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Error creating course:', error);
        this.errorMessage = error.error?.error || 'Failed to create course. Please try again.';
      }
    });
  }

  navigateToProfile() {
    this.router.navigate(['/profile']);
  }

  async startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.audioChunks = [];
      
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };
      
      this.mediaRecorder.onstop = () => {
        this.audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };
      
      this.mediaRecorder.start();
      this.isRecording = true;
      this.errorMessage = '';
      
    } catch (error) {
      console.error('Error starting recording:', error);
      this.errorMessage = 'Unable to access microphone. Please check permissions.';
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
    }
  }

  playRecording() {
    if (this.audioBlob) {
      const audioUrl = URL.createObjectURL(this.audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    }
  }

  clearRecording() {
    this.audioBlob = null;
    this.audioChunks = [];
    this.errorMessage = '';
  }

  generateCourseFromAudio() {
    if (!this.audioBlob) {
      this.errorMessage = 'No audio recording found';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.courseService.addCourseFromAudio(this.audioBlob).subscribe({
      next: (response) => {
        this.isLoading = false;
        console.log('Course created from audio:', response);
        this.router.navigate(['/courses']);
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Error creating course from audio:', error);
        this.errorMessage = error.error?.error || 'Failed to create course from audio. Please try again.';
      }
    });
  }
}

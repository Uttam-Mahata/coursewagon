import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-course',
  templateUrl: './course.component.html',
  styleUrls: ['./course.component.css']
})
export class CourseComponent {
  courseName: string = '';

  constructor(private courseService: CourseService, private router: Router) {}

  generateCourse() {
    this.courseService.addCourse(this.courseName).subscribe(() => {
      this.router.navigate(['/courses']);  // Navigate to the course list
    });
  }
}

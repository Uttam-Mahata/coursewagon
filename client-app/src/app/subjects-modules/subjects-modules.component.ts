import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../services/course.service';

@Component({
  selector: 'app-subjects-modules',
  templateUrl: './subjects-modules.component.html',
  styleUrls: ['./subjects-modules.component.css']
})
export class SubjectsModulesComponent implements OnInit {
  subjects: any[] = [];
  modules: any[] = [];
  courseId: number;
  courseName: string = '';
  selectedSubjectId: number | null = null;
  selectedSubjectName: string = '';

  constructor(
    private courseService: CourseService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.courseId = +this.route.snapshot.paramMap.get('course_id')!;
  }

  ngOnInit() {
    // Fetch course details to get course name
    this.courseService.getCourseDetails(this.courseId).subscribe((courses: any) => {
      this.courseName = courses.name;
    });

    // Fetch subjects for the given course
    this.courseService.getSubjects(this.courseId).subscribe((subjects: any[]) => {
      this.subjects = subjects;
    });
  }

  viewModules(subjectId: number) {
    // Set the selected subject ID and name
    this.selectedSubjectId = subjectId;
    const selectedSubject = this.subjects.find(subject => subject.id === subjectId);
    this.selectedSubjectName = selectedSubject ? selectedSubject.name : '';

    // Fetch modules for the selected subject
    this.courseService.getModules(this.courseId, subjectId).subscribe((modules: any[]) => {
      this.modules = modules;
    });

    const modulesSection = document.getElementById("modulesSection");
    if (modulesSection) {
      modulesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  generateModules(subjectId: number) {
    // Trigger module generation for the subject and refresh modules
    this.courseService.generateModules(this.courseId, subjectId).subscribe(() => {
      this.viewModules(subjectId); // Refresh the module list after generating
    });
  }

  viewChapters(moduleId: number) {
    this.router.navigate([`/courses/${this.courseId}/subjects/${this.selectedSubjectId}/modules/${moduleId}/chapters-topics`]);
  }

  generateChapters(moduleId: number) {
    this.courseService.generateChapters(this.courseId, this.selectedSubjectId!, moduleId).subscribe(() => {
      // Optionally refresh or show success message
      // Show a success message alert
      alert('Chapters generated successfully!');
    });
  }
  

  
  
}

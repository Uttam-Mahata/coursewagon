
# Course Wagon - Angular Application

CourseWagon is a web application designed to streamline course management and subject generation using Generative AI. This Angular application interacts with a Flask backend to manage courses, subjects, modules, chapters, topics, subtopics, and their respective content.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Service Methods](#service-methods)
- [Real-Life Applications](#real-life-applications)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Angular application leverages the `CourseService` to communicate with the backend API. It allows users to perform CRUD operations on various educational entities, making it easy for educators and content creators to manage their course offerings efficiently.

## Features
- **Course Management:** Add, retrieve, and manage courses.
- **Dynamic Content Generation:** Generate subjects, modules, chapters, topics, and subtopics using AI.
- **Data Retrieval:** Fetch details about courses, subjects, modules, chapters, topics, and their content.

## Installation

To set up the Angular application locally, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/CourseWagon-Angular.git
   cd CourseWagon-Angular
   ```

2. **Install Dependencies:**
   Ensure you have [Node.js](https://nodejs.org/) installed, then run:
   ```bash
   npm install
   ```

3. **Configure API URL:**
   Ensure the `apiUrl` in `src/app/course.service.ts` points to your Flask backend:
   ```typescript
   private apiUrl = 'http://127.0.0.1:5000/courses'; // Base URL for the Flask app
   ```

4. **Run the Application:**
   ```bash
   ng serve
   ```
   Open your browser and navigate to `http://localhost:4200` to view the application.

## Usage

### Service Methods

The `CourseService` provides the following methods to interact with the Flask backend:

- **addCourse(name: string):** Adds a new course.
- **getCourses():** Retrieves the list of all courses.
- **getCourseDetails(courseId: number):** Retrieves detailed information about a specific course.
- **getModuleDetails(courseId: number, subjectId: number, moduleId: number):** Retrieves details of a specific module.
- **getTopicDetails(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number):** Retrieves details of a specific topic.
- **generateSubjects(courseId: number):** Generates subjects for a specified course.
- **getSubjects(courseId: number):** Retrieves subjects for a specified course.
- **generateModules(courseId: number, subjectId: number):** Generates modules for a specified subject.
- **getModules(courseId: number, subjectId: number):** Retrieves modules for a specified subject.
- **generateChapters(courseId: number, subjectId: number, moduleId: number):** Generates chapters for a specified module.
- **getChapters(courseId: number, subjectId: number, moduleId: number):** Retrieves chapters for a specified module.
- **generateTopics(courseId: number, subjectId: number, moduleId: number, chapterId: number):** Generates topics for a specified chapter.
- **getTopics(courseId: number, subjectId: number, moduleId: number, chapterId: number):** Retrieves topics for a specified chapter.
- **generateSubtopics(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number):** Generates subtopics for a specified topic.
- **getSubtopics(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number):** Retrieves subtopics for a specified topic.
- **generateContent(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number, subtopicId: number):** Generates content for a specified subtopic.
- **getContent(courseId: number, subjectId: number, moduleId: number, chapterId: number, topicId: number, subtopicId: number):** Retrieves content for a specified subtopic.

### Example Usage
Here's how to use the `CourseService` in your Angular components:

```typescript
import { Component, OnInit } from '@angular/core';
import { CourseService } from './course.service';

@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html',
  styleUrls: ['./course-list.component.css']
})
export class CourseListComponent implements OnInit {
  courses: any[] = [];

  constructor(private courseService: CourseService) {}

  ngOnInit(): void {
    this.loadCourses();
  }

  loadCourses(): void {
    this.courseService.getCourses().subscribe(data => {
      this.courses = data;
    });
  }

  addCourse(courseName: string): void {
    this.courseService.addCourse(courseName).subscribe(() => {
      this.loadCourses(); // Reload courses after adding
    });
  }
}
```

## Real-Life Applications
- **Educational Institutions:** Helps streamline curriculum creation and management.
- **Online Learning Platforms:** Expands course offerings based on market demands.
- **Content Creators:** Facilitates the quick addition of relevant subjects and topics.

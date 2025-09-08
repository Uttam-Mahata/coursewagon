# CourseWagon Angular/TypeScript Technical Interview Questions

## Angular Core Concepts

### Component & Module Architecture
1. **How does your Angular application's module structure work? Explain the purpose of standalone components vs NgModule-based architecture.**
2. **What are the differences between `OnInit`, `AfterViewInit`, and `OnDestroy` lifecycle hooks? Where have you used them in CourseWagon?**
3. **Explain the component communication patterns you've implemented. How do parent-child components share data?**
4. **What is the purpose of `ChangeDetectionStrategy.OnPush` and have you considered using it for performance optimization?**
5. **How do you handle memory leaks with subscriptions? Show examples from your services.**

### Routing & Guards
6. **Explain your routing architecture. How do you implement lazy loading for feature modules?**
7. **Walk through your authentication guard implementation. How does `AuthGuard` determine if a user can access a route?**
8. **What's the difference between `CanActivate`, `CanDeactivate`, and `CanLoad` guards?**
9. **How do you handle route parameters and query parameters in your course detail pages?**
10. **Explain the purpose of `NonAuthGuard` and `AdminGuard`. How do they work together with AuthGuard?**

### Services & Dependency Injection
11. **Explain Angular's dependency injection system. What's the difference between `providedIn: 'root'` vs providing in a module?**
12. **How do you manage singleton services vs instances per component?**
13. **Walk through your `AuthService` implementation. How do you handle JWT token management?**
14. **How do you handle HTTP interceptors for adding authentication headers to API requests?**
15. **Explain the purpose of your various service layers (auth, course, content, chapter). How do they interact?**

## RxJS & Reactive Programming

### Observables & Operators
16. **What's the difference between `Subject`, `BehaviorSubject`, and `ReplaySubject`? Where have you used each?**
17. **Explain common RxJS operators you've used: `map`, `filter`, `switchMap`, `mergeMap`, `catchError`, `tap`**
18. **How do you handle error handling in HTTP requests using RxJS?**
19. **What's the difference between `subscribe()` and `async` pipe? When do you use each?**
20. **How do you prevent memory leaks with subscriptions? Show your unsubscribe patterns.**
21. **Explain how you handle race conditions with `switchMap` vs `mergeMap` in search functionality.**

### State Management
22. **How do you manage application state without using NgRx/Akita? What patterns do you follow?**
23. **Explain how you handle caching in your services. Do you cache API responses?**
24. **How do you share state between unrelated components?**
25. **What's your approach to handling optimistic updates in the UI?**

## TypeScript Deep Dive

### Type System
26. **Explain TypeScript interfaces vs types. When do you use each?**
27. **What are generics in TypeScript? Show examples from your codebase.**
28. **How do you handle null/undefined safety? Do you use strict null checks?**
29. **Explain union types and intersection types with examples from your models.**
30. **What are type guards and how have you implemented them?**
31. **How do you type HTTP responses from your backend API?**

### Advanced TypeScript
32. **What are decorators in TypeScript/Angular? Explain @Component, @Injectable, @Input, @Output**
33. **Explain the difference between `public`, `private`, and `protected` access modifiers.**
34. **What are async/await patterns? How do they compare to Promises and Observables?**
35. **How do you handle type inference vs explicit typing? What's your coding style?**
36. **Explain mapped types and conditional types if you've used them.**

## Firebase Integration

37. **How does Firebase Authentication work in your app? Walk through the login flow.**
38. **How do you handle Firebase Auth state persistence across page refreshes?**
39. **Explain how you integrate Firebase Auth tokens with your backend API.**
40. **How do you handle Firebase Storage for user uploads vs Azure Storage?**
41. **What security rules have you implemented for Firebase?**

## Performance & Optimization

42. **What techniques have you used to optimize Angular app performance?**
43. **How do you handle lazy loading of images and components?**
44. **Explain your build optimization strategies. What's in your angular.json configuration?**
45. **How do you handle bundle size optimization? Have you analyzed your bundle?**
46. **What's your strategy for code splitting?**
47. **How do you optimize change detection cycles?**

## Forms & Validation

48. **What's the difference between template-driven and reactive forms? Which do you use and why?**
49. **How do you implement custom validators?**
50. **Explain your form validation error handling strategy.**
51. **How do you handle dynamic forms if needed for course creation?**
52. **What's your approach to form state management?**

## HTTP & API Integration

53. **How do you handle CORS issues during development?**
54. **Explain your HTTP error handling strategy. How do you handle different status codes?**
55. **How do you implement request/response interceptors?**
56. **What's your strategy for API versioning on the frontend?**
57. **How do you handle file uploads to both Azure and Firebase?**
58. **Explain how you handle pagination in API requests.**

## Testing

59. **What's your unit testing strategy? Do you use Jasmine/Karma?**
60. **How do you mock services and HTTP requests in tests?**
61. **What's the difference between unit tests, integration tests, and e2e tests?**
62. **How do you test observables and async operations?**
63. **What's your code coverage target?**

## Security

64. **How do you prevent XSS attacks in Angular?**
65. **What security measures have you implemented for API communication?**
66. **How do you handle sensitive data like API keys in the frontend?**
67. **Explain your authentication token refresh strategy.**
68. **How do you prevent CSRF attacks?**

## CSS & Styling

69. **How does Tailwind CSS integration work with Angular?**
70. **What's your approach to responsive design?**
71. **How do you handle dark mode if implemented?**
72. **Explain Angular Material Design integration and customization.**
73. **What's ViewEncapsulation in Angular? (Emulated, None, ShadowDom)**

## Build & Deployment

74. **Explain your build process. What happens when you run `npm run build`?**
75. **How do you handle environment-specific configurations?**
76. **What's your CI/CD pipeline for deploying to Firebase Hosting?**
77. **How do you handle production error logging and monitoring?**
78. **What's your strategy for handling breaking API changes?**

## Architecture & Design Patterns

79. **What design patterns have you implemented? (Singleton, Factory, Observer)**
80. **Explain your folder structure and why you organized it this way.**
81. **How do you handle separation of concerns in your application?**
82. **What's your approach to code reusability?**
83. **How do you handle cross-cutting concerns like logging and error handling?**

## Modern Angular (v17-19)

84. **What new features from Angular 17-19 are you using? (Signals, Deferred Views, Control Flow)**
85. **Have you migrated to the new control flow syntax (@if, @for, @switch)?**
86. **What's your understanding of Angular Signals vs RxJS?**
87. **How do you handle standalone components vs traditional modules?**
88. **What's your migration strategy for new Angular versions?**

## Specific to Your Project

89. **Walk through the user journey from landing page to course enrollment.**
90. **How does the AI content generation integration work from the frontend perspective?**
91. **Explain your role-based access control implementation (Student, Admin, Instructor).**
92. **How do you handle real-time updates if any (WebSockets, Server-Sent Events)?**
93. **What challenges did you face with the payment integration if implemented?**
94. **How do you handle offline functionality or poor network conditions?**
95. **Explain your approach to handling course progress tracking.**
96. **How do you optimize the video/content delivery for courses?**
97. **What's your strategy for handling multilingual support if needed?**
98. **How do you ensure accessibility (a11y) compliance?**
99. **What performance metrics do you track and how?**
100. **If you could refactor one part of the application, what would it be and why?**

## Behavioral Technical Questions

101. **Describe a complex bug you encountered and how you debugged it.**
102. **How do you stay updated with Angular's rapid release cycle?**
103. **What tools do you use for development? (VS Code extensions, Chrome DevTools, etc.)**
104. **How do you approach code reviews?**
105. **What's your git workflow and branching strategy?**

## System Design & Scalability

106. **How would you scale this application to handle 100,000 concurrent users?**
107. **What caching strategies would you implement?**
108. **How would you handle real-time collaborative features?**
109. **Design a notification system for course updates.**
110. **How would you implement a recommendation engine for courses?**

---

## Tips for the Interview

1. **Be ready to live code** - They might ask you to implement a small feature or debug code
2. **Know your project inside out** - Every service, component, and design decision
3. **Prepare code examples** - Have specific code snippets ready to discuss
4. **Understand the WHY** - Not just what you did, but why you chose that approach
5. **Be honest about trade-offs** - Every decision has pros and cons
6. **Show enthusiasm** - Demonstrate passion for Angular and web development
7. **Ask questions** - Show interest in their tech stack and challenges

## Key Areas to Review

- **Angular Documentation**: Especially latest features in v17-19
- **RxJS Operators**: Practice common patterns
- **TypeScript Handbook**: Advanced types and patterns
- **Your Code**: Review every service and component you wrote
- **Performance**: Be ready to discuss Web Vitals and optimization techniques
- **Security**: OWASP Top 10 for web applications

---
layout: default
title: Contributing
nav_order: 10
description: "How to contribute to CourseWagon project"
---

# Contributing to CourseWagon
{: .no_toc }

Thank you for your interest in contributing to CourseWagon! This guide will help you get started.
{: .fs-6 .fw-300 }

## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Welcome Contributors! 🎉

CourseWagon is an open-source project, and we welcome contributions of all kinds:

- 🐛 Bug reports
- ✨ Feature requests
- 📝 Documentation improvements
- 🔧 Code contributions
- 🎨 UI/UX improvements
- 🧪 Testing and quality assurance
- 🌍 Translations (coming soon)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

- Be respectful and considerate
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Spamming or advertising
- Any conduct that violates our community standards

### Enforcement

Violations of the Code of Conduct can be reported to [contact@coursewagon.live](mailto:contact@coursewagon.live). All complaints will be reviewed and investigated promptly.

---

## Getting Started

### Prerequisites

Before contributing, make sure you have:

1. **GitHub account**: [Sign up here](https://github.com/join)
2. **Development environment**: See [Developer Guide](developer-guide)
3. **Git knowledge**: Basic understanding of Git and GitHub
4. **Familiarity with tech stack**: Angular, FastAPI, or documentation

### Finding Issues to Work On

**Good First Issues:**
- Look for issues labeled [`good first issue`](https://github.com/Uttam-Mahata/coursewagon/labels/good%20first%20issue)
- These are beginner-friendly and well-documented
- Great for first-time contributors

**Help Wanted:**
- Issues labeled [`help wanted`](https://github.com/Uttam-Mahata/coursewagon/labels/help%20wanted)
- These need community assistance
- May be more complex

**Browse All Issues:**
- [Open Issues](https://github.com/Uttam-Mahata/coursewagon/issues)
- [Feature Requests](https://github.com/Uttam-Mahata/coursewagon/labels/enhancement)
- [Bug Reports](https://github.com/Uttam-Mahata/coursewagon/labels/bug)

---

## How to Contribute

### 1. Reporting Bugs 🐛

**Before reporting:**
- Search [existing issues](https://github.com/Uttam-Mahata/coursewagon/issues)
- Check if bug is already fixed in latest version
- Verify it's reproducible

**When reporting:**

Use this template:

```markdown
**Bug Description**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g., Windows 10, macOS 14.2]
- Browser: [e.g., Chrome 120, Firefox 121]
- CourseWagon Version: [e.g., 1.0.0]

**Additional Context**
Any other context about the problem.
```

### 2. Suggesting Features ✨

**Before suggesting:**
- Check [existing feature requests](https://github.com/Uttam-Mahata/coursewagon/labels/enhancement)
- Think about how it fits the project vision
- Consider if others would benefit

**When suggesting:**

Use this template:

```markdown
**Feature Description**
Clear description of the feature.

**Problem It Solves**
What problem does this feature solve?

**Proposed Solution**
How you think it should work.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Mockups, examples, or references.
```

### 3. Contributing Code 🔧

#### Step 1: Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/coursewagon.git
cd coursewagon

# Add upstream remote
git remote add upstream https://github.com/Uttam-Mahata/coursewagon.git
```

#### Step 2: Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance tasks

Examples:
- `feature/add-dark-mode`
- `fix/login-button-alignment`
- `docs/update-api-reference`

#### Step 3: Make Your Changes

**Follow our coding standards:**
- See [Developer Guide - Coding Standards](developer-guide#coding-standards)
- Write clean, readable code
- Add comments for complex logic
- Follow existing patterns

**Test your changes:**
```bash
# Frontend tests
cd angular-client
npm test

# Backend tests
cd python-server
python -m pytest tests/
```

#### Step 4: Commit Your Changes

**Use conventional commits:**

```bash
git add .
git commit -m "feat: add dark mode toggle"
```

**Commit message format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semi-colons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```bash
feat(ui): add dark mode toggle to settings
fix(auth): resolve token refresh infinite loop
docs(api): update authentication endpoint documentation
refactor(services): improve error handling in course service
test(api): add integration tests for content generation
chore(deps): update Angular to version 19.1
```

#### Step 5: Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

**On GitHub:**
1. Go to your fork
2. Click "Compare & pull request"
3. Fill in the PR template
4. Submit the pull request

**PR template:**

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issue
Fixes #(issue number)

## How Has This Been Tested?
Describe the tests you ran.

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where needed
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] Any dependent changes have been merged

## Screenshots (if applicable)
Add screenshots for UI changes.
```

#### Step 6: Review Process

**What happens next:**

1. **Automated checks run**
   - CI/CD pipeline
   - Tests
   - Code quality checks

2. **Code review**
   - Maintainer reviews your code
   - May request changes
   - Discussion in PR comments

3. **Address feedback**
   - Make requested changes
   - Push updates to same branch
   - Reply to comments

4. **Approval and merge**
   - Once approved, PR is merged
   - Your contribution is live!
   - You're added to contributors list

**Tips for review:**
- Be responsive to feedback
- Ask questions if unclear
- Be patient and respectful
- Learn from suggestions

---

## Contributing to Documentation 📝

Documentation is crucial! You can help by:

**Improving existing docs:**
- Fix typos and grammar
- Clarify confusing sections
- Add missing information
- Update outdated content

**Adding new docs:**
- Tutorial guides
- Code examples
- Architecture explanations
- Troubleshooting guides

**Documentation locations:**
- `docs/` - Main documentation
- `README.md` - Project overview
- `CLAUDE.md` - AI assistant instructions
- Code comments - Inline documentation

**Style guide:**
- Clear and concise
- Use examples
- Include screenshots
- Keep it beginner-friendly
- Use proper Markdown formatting

---

## Design Contributions 🎨

We welcome UI/UX improvements:

**What you can contribute:**
- UI mockups
- User flow diagrams
- Icon designs
- Color schemes
- Accessibility improvements

**Tools we use:**
- Figma (preferred)
- Adobe XD
- Sketch
- Hand-drawn sketches are fine too!

**Process:**
1. Open an issue with your design
2. Get feedback from maintainers
3. Refine based on feedback
4. Implementation (you or another contributor)

---

## Becoming a Maintainer

Active contributors may be invited to become maintainers.

**Responsibilities:**
- Review pull requests
- Triage issues
- Help other contributors
- Make architectural decisions
- Maintain code quality

**Path to maintainership:**
1. Make consistent contributions
2. Show good judgment
3. Help the community
4. Express interest

---

## Development Guidelines

### Frontend (Angular)

**Component structure:**
```typescript
@Component({
  selector: 'app-feature',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './feature.component.html',
  styleUrls: ['./feature.component.css']
})
export class FeatureComponent implements OnInit, OnDestroy {
  // Implementation
}
```

**Best practices:**
- Use standalone components
- Implement OnDestroy for cleanup
- Use async pipe when possible
- Type everything with TypeScript
- Write unit tests

### Backend (Python/FastAPI)

**Endpoint structure:**
```python
@router.get("/endpoint/{id}")
async def get_resource(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> ResourceResponse:
    """
    Get resource by ID.
    
    Args:
        id: Resource identifier
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Resource object
        
    Raises:
        HTTPException: If resource not found
    """
    # Implementation
```

**Best practices:**
- Use type hints
- Write docstrings
- Handle errors properly
- Use dependency injection
- Write tests

---

## Testing Guidelines

### Frontend Testing

**Unit tests:**
```typescript
describe('CourseService', () => {
  it('should fetch courses', () => {
    // Test implementation
  });
});
```

**Component tests:**
```typescript
describe('CourseListComponent', () => {
  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
```

### Backend Testing

**API tests:**
```python
def test_get_courses(client, auth_headers):
    response = client.get("/api/courses", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**Integration tests:**
```python
def test_course_creation_flow(client, auth_headers):
    # Test complete flow
    pass
```

---

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Self-reviewed the code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] Added/updated tests
- [ ] All tests pass locally
- [ ] No merge conflicts

### PR Best Practices

**Do:**
- Keep PRs focused and small
- Write clear descriptions
- Link related issues
- Update documentation
- Add tests
- Respond to feedback

**Don't:**
- Mix unrelated changes
- Submit broken code
- Ignore review comments
- Force push after review (unless asked)

---

## Community

### Communication Channels

**GitHub:**
- [Issues](https://github.com/Uttam-Mahata/coursewagon/issues)
- [Discussions](https://github.com/Uttam-Mahata/coursewagon/discussions)
- [Pull Requests](https://github.com/Uttam-Mahata/coursewagon/pulls)

**Email:**
- [contact@coursewagon.live](mailto:contact@coursewagon.live)

### Getting Help

**Stuck on something?**

1. Check documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Reach out to maintainers

**Helping others:**
- Answer questions in Discussions
- Review pull requests
- Improve documentation
- Share your knowledge

---

## Recognition

### Contributors

All contributors are recognized:

- Listed in README.md
- Mentioned in release notes
- Added to GitHub contributors
- Credited in documentation

### Hall of Fame

Outstanding contributors may receive:
- Special recognition
- Invitation to maintainer team
- Early access to features
- Exclusive swag (when available)

---

## License

By contributing, you agree that your contributions will be licensed under the same [MIT License](https://github.com/Uttam-Mahata/coursewagon/blob/main/LICENSE) that covers the project.

---

## Questions?

Have questions about contributing?

- 📧 Email: [contact@coursewagon.live](mailto:contact@coursewagon.live)
- 💬 Discussions: [GitHub Discussions](https://github.com/Uttam-Mahata/coursewagon/discussions)
- 📖 Docs: [Developer Guide](developer-guide)

---

## Thank You! 🙏

Every contribution, no matter how small, makes CourseWagon better. Thank you for being part of our community!

---

**Ready to contribute?** Check out [good first issues](https://github.com/Uttam-Mahata/coursewagon/labels/good%20first%20issue) to get started!

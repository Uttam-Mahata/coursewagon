# Contributing to CourseWagon

Thank you for your interest in contributing to CourseWagon! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## 📜 Code of Conduct

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/coursewagon.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit and push to your fork
7. Submit a pull request

## 🤝 How to Contribute

### Reporting Bugs

- Use the issue tracker to report bugs
- Describe the bug in detail
- Include steps to reproduce
- Mention your environment (OS, browser, versions)
- Add screenshots if applicable

### Suggesting Enhancements

- Use the issue tracker to suggest enhancements
- Clearly describe the feature and its benefits
- Explain why this enhancement would be useful

### Code Contributions

- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it
- Follow the development setup guide
- Write clean, documented code
- Add tests for new features
- Update documentation as needed

## 💻 Development Setup

### Backend (python-server/)

```bash
# Install dependencies
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run development server
uvicorn app:app --reload
```

### Frontend (angular-client/)

```bash
# Install dependencies
npm install

# Run development server
npm start
```

See [CLAUDE.md](https://github.com/coursewagon/coursewagon/blob/main/CLAUDE.md) for detailed development instructions.

## 📏 Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable names

### TypeScript/Angular (Frontend)

- Follow Angular style guide
- Use TypeScript strict mode
- Write descriptive component and service names
- Keep components focused on presentation
- Move business logic to services

### General

- Write self-documenting code
- Add comments for complex logic
- Keep files under 500 lines when possible
- Use consistent naming conventions

## 📝 Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(auth): add password reset functionality
fix(content): resolve LaTeX rendering issue
docs(readme): update installation instructions
refactor(api): simplify course service logic
```

## 🔄 Pull Request Process

1. **Update Documentation**: Ensure relevant docs are updated
2. **Add Tests**: Include tests for new features or bug fixes
3. **Follow Code Style**: Ensure your code follows our standards
4. **Write Clear Description**: Explain what changes you made and why
5. **Link Issues**: Reference related issues (e.g., "Fixes #123")
6. **Request Review**: Tag relevant maintainers for review
7. **Address Feedback**: Respond to review comments promptly
8. **Squash Commits**: Clean up commit history if requested

### Pull Request Template

Your PR should include:

- **Description**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Testing**: How was this tested?
- **Screenshots**: Visual changes (if applicable)
- **Checklist**: Confirm you've completed all requirements

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_auth_routes.py

# Run with coverage
python -m pytest --cov=app tests/
```

### Frontend Tests

```bash
# Run unit tests
npm test

# Run in watch mode
npm run watch
```

## 📚 Resources

- [Project Documentation](https://github.com/coursewagon/coursewagon/blob/main/CLAUDE.md)
- [Angular Style Guide](https://angular.io/guide/styleguide)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Python PEP 8](https://peps.python.org/pep-0008/)

## ❓ Questions?

If you have questions, feel free to:
- Open an issue with the `question` label
- Start a discussion in the repository

## 🙏 Thank You!

Your contributions help make CourseWagon better for everyone. We appreciate your time and effort!

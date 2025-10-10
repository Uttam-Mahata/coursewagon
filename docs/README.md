# CourseWagon Documentation

This directory contains the complete documentation for CourseWagon, powered by Jekyll and the Just the Docs theme.

## 📚 Documentation Structure

- **index.md** - Home page and overview
- **getting-started.md** - Setup and installation guide
- **architecture.md** - System architecture and design
- **api-reference.md** - Complete API documentation
- **user-guide.md** - User manual and tutorials
- **developer-guide.md** - Contributing and development guide
- **deployment.md** - Production deployment guide
- **features.md** - Feature list and capabilities
- **faq.md** - Frequently asked questions
- **contributing.md** - Contribution guidelines

## 🌐 Live Documentation

The documentation is deployed to GitHub Pages at:
**https://uttam-mahata.github.io/coursewagon/**

## 🛠️ Local Development

### Prerequisites

- Ruby 3.1 or higher
- Bundler gem

### Setup

```bash
cd docs
bundle install
```

### Run Locally

```bash
bundle exec jekyll serve
```

Then open http://localhost:4000/coursewagon/ in your browser.

### Build for Production

```bash
bundle exec jekyll build
```

The built site will be in `_site/` directory.

## 📝 Writing Documentation

### Markdown Files

All documentation is written in Markdown with YAML front matter:

```markdown
---
layout: default
title: Page Title
nav_order: 1
description: "Page description"
---

# Page Title

Content goes here...
```

### Front Matter Options

- **layout**: Always use `default`
- **title**: Page title (shows in navigation)
- **nav_order**: Order in sidebar (1, 2, 3, etc.)
- **description**: SEO meta description
- **permalink**: Custom URL (optional)

### Navigation

Pages are automatically added to the sidebar based on:
- `title` - Display name
- `nav_order` - Sort order

### Table of Contents

Add a table of contents to any page:

```markdown
## Table of Contents
{: .no_toc .text-delta }

1. TOC
{:toc}
```

### Styling

Just the Docs provides utility classes:

```markdown
{: .fs-9 }         # Large font size
{: .fs-6 .fw-300 } # Smaller font, light weight
{: .btn }          # Button style
{: .label }        # Label style
```

### Code Blocks

Use fenced code blocks with language:

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### Admonitions

Create callouts:

```markdown
{: .note }
This is a note

{: .warning }
This is a warning
```

## 🎨 Theme

We use [Just the Docs](https://github.com/just-the-docs/just-the-docs) theme with custom configuration in `_config.yml`.

### Theme Features

- 📱 Responsive design
- 🔍 Built-in search
- 📊 Syntax highlighting
- 🎨 Customizable colors
- 📑 Automatic navigation

## 🚀 Deployment

Documentation is automatically deployed via GitHub Actions when:
- Changes are pushed to `main` branch
- Changes are in the `docs/` directory

The workflow:
1. Checks out the repository
2. Sets up Ruby and dependencies
3. Builds Jekyll site
4. Deploys to GitHub Pages

## 📦 Dependencies

See `Gemfile` for all dependencies:
- Jekyll 4.3
- Just the Docs theme
- Jekyll SEO Tag
- Jekyll Sitemap

## 🤝 Contributing

To contribute to documentation:

1. Edit or create Markdown files in `docs/`
2. Test locally with `bundle exec jekyll serve`
3. Submit a pull request
4. Documentation will auto-deploy after merge

See [Contributing Guide](contributing.md) for more details.

## 📄 License

Documentation is part of the CourseWagon project and licensed under the MIT License.

---

For questions about documentation, contact [contact@coursewagon.live](mailto:contact@coursewagon.live).

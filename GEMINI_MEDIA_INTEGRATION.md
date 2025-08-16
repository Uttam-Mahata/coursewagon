# Enhanced Gemini Integration for Media Placement in Content

## Overview

This enhancement integrates Gemini AI with media upload functionality to allow intelligent placement of images and videos within course content. The system now supports:

1. **Media-Aware Content Generation**: Gemini generates content with placeholders for existing media files
2. **Media Placement Suggestions**: AI suggests where media should be placed for optimal learning
3. **Intelligent Media Insertion**: Automatic insertion of media at specific positions or sections
4. **Seamless Integration**: Media files are naturally embedded into the markdown content

## How It Works

### 1. Media-Aware Content Generation

When generating content, the system now:

```python
# Check if there are existing media files for this topic
existing_media = self.media_repo.get_media_by_content_id(topic_id)
media_placeholders = ""

if include_media_placeholders and existing_media:
    media_placeholders = self._generate_media_placeholders(existing_media)
```

**Example Media Placeholder Instructions for Gemini:**
```
**MEDIA PLACEMENT INSTRUCTIONS:**
The following media files are available for this topic. Please integrate them naturally into the content where appropriate:

1. **Image**: diagram.png - Network Architecture Diagram
   - Use placeholder: {MEDIA_123} where you want this image to appear
   - File URL: https://storage.blob.core.windows.net/coursewagon-images/diagram.png
   - Alt text: Network architecture diagram showing client-server communication

2. **Video**: tutorial.mp4 - Step-by-step Tutorial
   - Use placeholder: {MEDIA_124} where you want this video to appear
   - File URL: https://storage.blob.core.windows.net/coursewagon-images/tutorial.mp4

**IMPORTANT**: Replace the placeholders {MEDIA_X} with appropriate markdown/HTML code for the media files.
```

### 2. Content Generation Flow

1. **User uploads media files** → Files stored in Azure Blob Storage
2. **User clicks "Generate Content"** → System checks for existing media
3. **Gemini receives enhanced prompt** → Includes media placement instructions
4. **Gemini generates content** → With {MEDIA_X} placeholders
5. **System processes placeholders** → Replaces with actual embed codes
6. **Content is saved** → With media naturally integrated

### 3. Media Placement Suggestions

Users can get AI-powered suggestions for media placement:

```python
def generate_content_with_media_suggestions(self, course_id, subject_id, chapter_id, topic_id):
    prompt = f"""
    Analyze the topic "{topic.name}" and suggest where images or videos would be most beneficial for learning.
    
    Provide suggestions in the following format:
    
    ## Media Placement Suggestions
    
    ### 1. [Section Name]
    **Suggested Media Type**: [image/video]
    **Purpose**: [explain why this media would help learning]
    **Recommended Content**: [describe what the media should show]
    **Placement**: [where in the content this should appear]
    """
```

**Example AI Response:**
```markdown
## Media Placement Suggestions

### 1. Introduction to Neural Networks
**Suggested Media Type**: image
**Purpose**: Visual representation helps students understand the basic structure
**Recommended Content**: A simple diagram showing input layer, hidden layer, and output layer
**Placement**: Right after the first paragraph explaining neural network basics

### 2. Backpropagation Algorithm
**Suggested Media Type**: video
**Purpose**: Step-by-step demonstration of the algorithm in action
**Recommended Content**: Animation showing how errors propagate backward through the network
**Placement**: After the mathematical explanation of backpropagation
```

### 4. Intelligent Media Insertion

The system supports inserting media at specific positions:

```python
def insert_media_at_position(self, topic_id, media_id, position, section_identifier=None):
    # If section identifier is provided, find that section
    if section_identifier:
        content_text = self._insert_media_in_section(content.content, media, section_identifier)
    else:
        # Insert at specific position
        content_text = self._insert_media_at_position(content.content, media, position)
```

## Frontend Integration

### 1. Enhanced UI Components

The Angular frontend now includes:

- **"Get Media Suggestions" button**: Shows when media files exist but no content
- **Media suggestions modal**: Displays AI-generated placement recommendations
- **"Insert Media" button**: On each media file for direct insertion
- **Enhanced content generation**: Automatically includes media placeholders

### 2. User Workflow

#### Scenario 1: Upload Media First, Then Generate Content
1. User uploads images/videos for a topic
2. User clicks "Generate Content"
3. System automatically includes media placeholders in Gemini prompt
4. Generated content includes media naturally embedded

#### Scenario 2: Get AI Suggestions for Media Placement
1. User uploads media files
2. User clicks "Get Media Suggestions"
3. AI analyzes topic and suggests optimal media placement
4. User can then generate content with these suggestions

#### Scenario 3: Insert Media into Existing Content
1. User has existing content
2. User uploads new media files
3. User clicks "Insert Media" on specific media file
4. Media is automatically inserted at the end of content

## API Endpoints

### New Endpoints Added

```typescript
// Generate content with media suggestions
POST /courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/generate_content_with_media_suggestions

// Insert media at specific position
POST /courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/insert_media
{
  "media_id": 123,
  "position": 1500,  // Optional: character position
  "section_identifier": "Introduction"  // Optional: section name
}

// Enhanced content generation with options
POST /courses/{course_id}/subjects/{subject_id}/chapters/{chapter_id}/topics/{topic_id}/generate_content
{
  "include_media_placeholders": true
}
```

## Benefits

### 1. **Improved Learning Experience**
- Media is contextually placed within content
- No manual copy-pasting of embed codes
- Natural flow between text and media

### 2. **AI-Powered Optimization**
- Gemini suggests optimal media placement
- Content and media work together for better learning
- Intelligent integration based on topic context

### 3. **Streamlined Workflow**
- Reduced manual work for content creators
- Automatic media embedding
- Smart suggestions for media placement

### 4. **Flexible Integration**
- Works with existing media upload system
- Backward compatible with current content
- Supports both automatic and manual placement

## Example Usage

### Step 1: Upload Media
```
User uploads:
- network_diagram.png (Network architecture diagram)
- tutorial_video.mp4 (Step-by-step tutorial)
- code_example.png (Code snippet with syntax highlighting)
```

### Step 2: Generate Content with Media
```
Gemini receives enhanced prompt:
"Generate content for 'Neural Networks' topic. 
Available media: network_diagram.png, tutorial_video.mp4, code_example.png
Place media naturally in the content using {MEDIA_123}, {MEDIA_124}, {MEDIA_125} placeholders"
```

### Step 3: Generated Content
```markdown
# Neural Networks

Neural networks are computational models inspired by biological neural networks...

## Basic Structure

A neural network consists of layers of interconnected nodes...

{MEDIA_123}  <!-- Network diagram automatically inserted here -->

## Training Process

The training process involves...

{MEDIA_124}  <!-- Tutorial video automatically inserted here -->

## Implementation Example

Here's a simple implementation:

{MEDIA_125}  <!-- Code example automatically inserted here -->
```

### Step 4: Final Rendered Content
```markdown
# Neural Networks

Neural networks are computational models inspired by biological neural networks...

## Basic Structure

A neural network consists of layers of interconnected nodes...

![Network architecture diagram showing client-server communication](https://storage.blob.core.windows.net/coursewagon-images/network_diagram.png)
*Network architecture diagram showing client-server communication*

## Training Process

The training process involves...

<video controls width="100%">
  <source src="https://storage.blob.core.windows.net/coursewagon-images/tutorial_video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
*Step-by-step tutorial*

## Implementation Example

Here's a simple implementation:

![Code snippet with syntax highlighting](https://storage.blob.core.windows.net/coursewagon-images/code_example.png)
*Code snippet with syntax highlighting*
```

## Technical Implementation Details

### 1. Media Repository Integration
```python
class ContentService:
    def __init__(self, db: Session):
        self.media_repo = MediaRepository(db)  # Added media repository
```

### 2. Placeholder Processing
```python
def _process_media_placeholders(self, content, media_files):
    for media in media_files:
        placeholder = f"{{MEDIA_{media.id}}}"
        if placeholder in content:
            embed_code = self._generate_embed_code(media)
            content = content.replace(placeholder, embed_code)
    return content
```

### 3. Section-Based Insertion
```python
def _insert_media_in_section(self, content, media, section_identifier):
    # Find the section using regex
    section_pattern = rf"(^#+\s*{re.escape(section_identifier)}.*?)(?=^#+\s|$)"
    match = re.search(section_pattern, content, re.MULTILINE | re.DOTALL)
    
    if match:
        # Insert media at the end of the section
        embed_code = self._generate_embed_code(media)
        new_section = section_content.rstrip() + "\n\n" + embed_code + "\n"
        return content[:section_start] + new_section + content[section_end:]
```

## Future Enhancements

### 1. **Advanced Media Placement**
- Drag-and-drop interface for media placement
- Visual content editor with media preview
- Multiple media insertion points

### 2. **AI-Enhanced Features**
- Automatic media generation suggestions based on content
- Smart cropping and resizing of images
- Video thumbnail generation

### 3. **Content Optimization**
- A/B testing for media placement effectiveness
- Analytics on media engagement
- Personalized media recommendations

### 4. **Collaborative Features**
- Media placement comments and suggestions
- Version control for media placement
- Team collaboration on content-media integration

This enhanced integration transforms the content creation process from a manual, disconnected workflow to an intelligent, AI-powered system that seamlessly integrates text and media for optimal learning outcomes.
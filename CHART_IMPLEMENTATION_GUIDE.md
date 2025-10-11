# Chart and Graph Implementation Guide

## Overview

CourseWagon now supports interactive charts and graphs in course content using **Chart.js** in addition to the existing **Mermaid.js** diagrams. This provides rich data visualization capabilities for educational content.

## Architecture

### Frontend Components

1. **ChartRendererService** (`angular-client/src/app/services/chart-renderer.service.ts`)
   - Parses chart data blocks from markdown content
   - Renders Chart.js charts dynamically
   - Manages chart lifecycle (create, update, destroy)

2. **CourseContentComponent** (Updated)
   - Integrates chart rendering into content display
   - Calls `chartRendererService.processContent()` to parse chart blocks
   - Calls `chartRendererService.renderCharts()` in `ngAfterViewChecked()`
   - Cleans up charts in `ngOnDestroy()`

### Backend Components

1. **ContentService** (`python-server/services/content_service.py`)
   - Updated Gemini AI prompt to generate Chart.js configurations
   - Provides instructions for both Mermaid diagrams and Chart.js charts

2. **GeminiHelper** (`python-server/utils/gemini_helper.py`)
   - Generates content with embedded chart configurations
   - No changes needed - works with updated prompts

## How It Works

### 1. Content Generation Flow

```
User triggers content generation
    ↓
Backend calls Gemini AI with updated prompt
    ↓
Gemini generates markdown + Mermaid diagrams + Chart.js JSON configs
    ↓
Content stored in database
    ↓
Frontend retrieves content
    ↓
MathRendererService processes LaTeX
    ↓
ChartRendererService parses and renders charts
    ↓
ngx-markdown renders markdown + Mermaid diagrams
```

### 2. Chart Data Format

Charts are embedded in markdown using fenced code blocks with the `chart-json` language identifier:

````markdown
```chart-json
{
  "type": "bar",
  "data": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [{
      "label": "Revenue",
      "data": [12000, 19000, 15000, 22000],
      "backgroundColor": "rgba(54, 162, 235, 0.5)",
      "borderColor": "rgba(54, 162, 235, 1)",
      "borderWidth": 1
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "Quarterly Revenue"
      }
    }
  }
}
```
````

### 3. Rendering Process

1. **ChartRendererService.processContent()** - Parses content and replaces chart blocks with placeholder divs:
   ```html
   <div class="chart-container" data-chart-id="chart-123456" data-chart-config="..."></div>
   ```

2. **ChartRendererService.renderCharts()** - Creates Chart.js instances:
   - Finds all `.chart-container` elements
   - Extracts chart configuration from data attributes
   - Creates canvas element
   - Instantiates Chart.js with the configuration

3. **Cleanup** - Destroys charts on component destruction to prevent memory leaks

## Supported Chart Types

### Chart.js Charts (Interactive)

- **bar** - Vertical bar charts
- **line** - Line charts for trends
- **pie** - Pie charts for proportions
- **doughnut** - Doughnut charts
- **radar** - Radar/spider charts
- **polarArea** - Polar area charts
- **bubble** - Bubble charts
- **scatter** - Scatter plots

**Best for:** Statistical data, performance metrics, comparisons, distributions, trends

### Mermaid.js Diagrams (Existing)

- Flowchart, Sequence Diagram, Class Diagram, State Diagram
- Entity Relationship Diagram, Gantt Chart
- User Journey, Timeline, MindMaps
- And more...

**Best for:** Process flows, architecture diagrams, relationships, workflows

## Usage Examples

### Example 1: Bar Chart for Algorithm Complexity Comparison

````markdown
## Time Complexity Comparison

```chart-json
{
  "type": "bar",
  "data": {
    "labels": ["Bubble Sort", "Quick Sort", "Merge Sort", "Heap Sort"],
    "datasets": [{
      "label": "Average Case (n log n)",
      "data": [100, 13, 13, 13],
      "backgroundColor": "rgba(255, 99, 132, 0.6)"
    }, {
      "label": "Best Case",
      "data": [10, 13, 13, 13],
      "backgroundColor": "rgba(75, 192, 192, 0.6)"
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "Sorting Algorithm Time Complexity"
      }
    },
    "scales": {
      "y": {
        "title": {
          "display": true,
          "text": "Operations (thousands)"
        }
      }
    }
  }
}
```
````

### Example 2: Line Chart for Performance Trends

````markdown
## Model Training Progress

```chart-json
{
  "type": "line",
  "data": {
    "labels": ["Epoch 1", "Epoch 2", "Epoch 3", "Epoch 4", "Epoch 5"],
    "datasets": [{
      "label": "Training Accuracy",
      "data": [0.65, 0.78, 0.85, 0.89, 0.92],
      "borderColor": "rgb(75, 192, 192)",
      "tension": 0.1
    }, {
      "label": "Validation Accuracy",
      "data": [0.63, 0.76, 0.82, 0.86, 0.88],
      "borderColor": "rgb(255, 99, 132)",
      "tension": 0.1
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "Model Training Metrics"
      }
    },
    "scales": {
      "y": {
        "min": 0,
        "max": 1,
        "title": {
          "display": true,
          "text": "Accuracy"
        }
      }
    }
  }
}
```
````

### Example 3: Pie Chart for Distribution

````markdown
## Programming Language Usage

```chart-json
{
  "type": "pie",
  "data": {
    "labels": ["Python", "JavaScript", "Java", "C++", "Others"],
    "datasets": [{
      "data": [35, 25, 20, 10, 10],
      "backgroundColor": [
        "rgba(255, 99, 132, 0.8)",
        "rgba(54, 162, 235, 0.8)",
        "rgba(255, 206, 86, 0.8)",
        "rgba(75, 192, 192, 0.8)",
        "rgba(153, 102, 255, 0.8)"
      ]
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "Language Distribution in Projects"
      },
      "legend": {
        "position": "right"
      }
    }
  }
}
```
````

### Example 4: Combining Charts with Mermaid Diagrams

````markdown
## System Architecture and Performance

### Architecture Diagram

<pre class="mermaid">
graph TB
    A[Client] -->|HTTP| B[Load Balancer]
    B --> C[Web Server 1]
    B --> D[Web Server 2]
    C --> E[Database]
    D --> E
</pre>

### Performance Metrics

```chart-json
{
  "type": "line",
  "data": {
    "labels": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
    "datasets": [{
      "label": "Requests per Second",
      "data": [120, 80, 200, 350, 400, 280],
      "borderColor": "rgb(75, 192, 192)",
      "fill": true,
      "backgroundColor": "rgba(75, 192, 192, 0.2)"
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "Daily Request Pattern"
      }
    }
  }
}
```
````

## AI Prompt Guidelines

The Gemini AI prompt has been updated with these instructions:

1. **Use Chart.js for statistical/numerical visualizations**
   - Performance comparisons
   - Benchmark results
   - Statistical distributions
   - Time series data
   - Survey results

2. **Use Mermaid for structural diagrams**
   - Process flows
   - System architecture
   - State machines
   - Relationships

3. **Chart Configuration Requirements**
   - Must be valid JSON
   - Must include `type`, `data`, and `options`
   - `data` must have `labels` and `datasets`
   - Use appropriate colors with transparency
   - Include descriptive titles and labels

## Styling

Charts are styled with CSS in `course-content.component.css`:

```css
.chart-container {
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  max-width: 100%;
  overflow: hidden;
}

.chart-error {
  color: #ef4444;
  padding: 1rem;
  background-color: #fee2e2;
  border-left: 3px solid #ef4444;
  border-radius: 0.375rem;
}
```

## Testing

### Manual Testing Steps

1. **Generate New Content**
   - Create a course with a topic that would benefit from charts (e.g., "Algorithm Performance Analysis")
   - Click "Generate Content"
   - Verify charts are displayed correctly

2. **Edit Existing Content**
   - Add a chart configuration manually to existing content
   - Save and verify rendering

3. **Test Different Chart Types**
   - Create content with bar, line, pie, and other chart types
   - Verify all types render correctly

4. **Test Responsive Behavior**
   - View charts on different screen sizes
   - Verify charts remain readable on mobile

### Example Test Content

Create a new topic and add this content:

````markdown
# Performance Analysis

## Algorithm Comparison

```chart-json
{
  "type": "bar",
  "data": {
    "labels": ["Linear Search", "Binary Search", "Hash Table"],
    "datasets": [{
      "label": "Time Complexity (Operations)",
      "data": [1000, 10, 1],
      "backgroundColor": [
        "rgba(255, 99, 132, 0.6)",
        "rgba(54, 162, 235, 0.6)",
        "rgba(75, 192, 192, 0.6)"
      ]
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "Search Algorithm Performance"
      }
    },
    "scales": {
      "y": {
        "type": "logarithmic"
      }
    }
  }
}
```
````

## Troubleshooting

### Charts Not Rendering

1. **Check Browser Console** - Look for JavaScript errors
2. **Verify JSON Format** - Ensure chart configuration is valid JSON
3. **Check Chart Type** - Ensure type is one of the supported types
4. **Inspect HTML** - Verify chart containers are created with correct data attributes

### Chart Rendering Errors

If you see "Error rendering chart. Invalid configuration.":
- Validate the JSON syntax
- Ensure all required fields are present (type, data, labels, datasets)
- Check data array lengths match labels array length

### Performance Issues

If charts cause lag:
- Limit number of data points (< 100 recommended)
- Reduce number of charts per page
- Use appropriate chart types for data size

## Future Enhancements

Potential improvements:

1. **Chart Editing UI** - Visual chart builder in the content editor
2. **More Chart Libraries** - Add D3.js for advanced visualizations
3. **Export Charts** - Allow users to download charts as images
4. **Interactive Features** - Add tooltips, zooming, panning
5. **Data Import** - Allow CSV/JSON data upload for charts
6. **Chart Templates** - Pre-configured chart templates for common use cases

## References

- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [Mermaid.js Documentation](https://mermaid.js.org/)
- [ngx-markdown Documentation](https://github.com/jfcere/ngx-markdown)

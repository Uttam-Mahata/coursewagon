#!/usr/bin/env python3
"""Test script to verify chart content processing"""

import sys
sys.path.insert(0, '/home/uttam/coursewagon/python-server')

from utils.gemini_helper import chart_content, mermaid_content

# Test content with chart-json block
test_content = """
# Algorithm Performance

Here is a comparison of time complexities:

```chart-json
{
  "type": "line",
  "data": {
    "labels": ["1", "2", "4", "8", "16", "32", "64", "128", "256"],
    "datasets": [
      {
        "label": "O(1)",
        "data": [1, 1, 1, 1, 1, 1, 1, 1, 1],
        "borderColor": "rgba(75, 192, 192, 1)",
        "fill": false
      },
      {
        "label": "O(log n)",
        "data": [0, 1, 2, 3, 4, 5, 6, 7, 8],
        "borderColor": "rgba(54, 162, 235, 1)",
        "fill": false
      },
      {
        "label": "O(n)",
        "data": [1, 2, 4, 8, 16, 32, 64, 128, 256],
        "borderColor": "rgba(255, 99, 132, 1)",
        "fill": false
      }
    ]
  },
  "options": {
    "responsive": true,
    "maintainAspectRatio": false,
    "plugins": {
      "title": {
        "display": true,
        "text": "Time Complexity Comparison"
      }
    }
  }
}
```

And here's a mermaid diagram:

```mermaid
graph LR
    A[Input] --> B[Process]
    B --> C[Output]
```

More content here.
"""

print("Original Content:")
print("=" * 80)
print(test_content)
print("\n" + "=" * 80)

# Process mermaid content
processed = mermaid_content(test_content)
print("\nAfter mermaid_content():")
print("=" * 80)
print(processed)
print("\n" + "=" * 80)

# Process chart content
processed = chart_content(processed)
print("\nAfter chart_content():")
print("=" * 80)
print(processed)
print("\n" + "=" * 80)

# Check if chart div exists
if '<div class="chart-container"' in processed:
    print("\n✓ SUCCESS: Chart div created!")
    print("✓ Chart container found in processed content")
else:
    print("\n✗ FAILED: No chart div found!")

# Check if mermaid pre tag exists
if '<pre class="mermaid">' in processed:
    print("✓ SUCCESS: Mermaid diagram converted!")
else:
    print("✗ FAILED: No mermaid pre tag found!")

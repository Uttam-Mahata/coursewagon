import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class MermaidService {
  private readonly VALID_DIAGRAM_TYPES = [
    'graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram',
    'erDiagram', 'journey', 'gantt', 'pie', 'quadrantChart', 'requirementDiagram',
    'gitGraph', 'c4Diagram', 'mindmap', 'timeline'
  ];

  constructor() { }

  /**
   * Validates if a mermaid diagram code has proper syntax
   * @param code The mermaid diagram code to validate
   * @returns True if the code appears to be valid, false otherwise
   */
  validateMermaidCode(code: string): boolean {
    if (!code || typeof code !== 'string') {
      return false;
    }

    // Check if diagram starts with a valid diagram type
    const firstLine = code.trim().split('\n')[0].trim();
    const hasValidStart = this.VALID_DIAGRAM_TYPES.some(type => 
      firstLine.startsWith(type) || firstLine.match(new RegExp(`^${type}\\s+`))
    );

    if (!hasValidStart) {
      console.warn('Invalid mermaid diagram type:', firstLine);
      return false;
    }

    // Check for balanced brackets and quotes
    const brackets = { '{': '}', '(': ')', '[': ']' };
    const stack: string[] = [];
    let inQuotes = false;
    let quoteChar = '';

    for (let i = 0; i < code.length; i++) {
      const char = code[i];
      
      // Handle quotes
      if ((char === '"' || char === "'") && (i === 0 || code[i-1] !== '\\')) {
        if (!inQuotes) {
          inQuotes = true;
          quoteChar = char;
        } else if (char === quoteChar) {
          inQuotes = false;
        }
        continue;
      }
      
      // Skip characters inside quotes
      if (inQuotes) continue;
      
      // Handle brackets
      if ('{(['.includes(char)) {
        stack.push(brackets[char as keyof typeof brackets]);
      } else if ('})]'.includes(char)) {
        if (stack.pop() !== char) {
          console.warn('Unbalanced brackets in mermaid diagram');
          return false;
        }
      }
    }
    
    // If we have unclosed brackets or quotes
    if (stack.length > 0 || inQuotes) {
      console.warn('Unclosed brackets or quotes in mermaid diagram');
      return false;
    }

    return true;
  }

  /**
   * Add error handling to mermaid diagrams in markdown
   * @param markdownContent The markdown content containing mermaid diagrams
   * @returns Processed markdown with error handling for diagrams
   */
  processMermaidInMarkdown(markdownContent: string): string {
    if (!markdownContent) return '';
    
    return markdownContent.replace(
      /<pre class="mermaid">([\s\S]*?)<\/pre>/g, 
      (match, diagramCode) => {
        const trimmedCode = diagramCode.trim();
        
        // If diagram code passes validation
        if (this.validateMermaidCode(trimmedCode)) {
          return `<pre class="mermaid">\n${trimmedCode}\n</pre>`;
        }
        
        // Return a message for invalid diagrams
        return '<div class="mermaid-error-message">Diagram cannot be displayed due to syntax errors</div>';
      }
    );
  }
}

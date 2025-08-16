import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class MathRendererService {
  
  constructor() { }

  /**
   * Process markdown content to handle math expressions
   * Uses a mixed approach:
   * - KaTeX for inline and simple equations
   * - MathJax for multiline/complex equations
   * 
   * @param content Markdown content with LaTeX expressions
   * @returns Processed content
   */
  processContent(content: string): string {
    if (!content) return '';

    // First, preserve any escaped dollar signs
    let processed = content.replace(/\\\$/g, '___ESCAPED_DOLLAR___');

    // Special handling for cases/piecewise functions which are common in fuzzy logic
    processed = this.processCasesEquations(processed);

    // Process multiline equations
    processed = processed.replace(/\$\$([\s\S]*?)\$\$/g, (match, equation) => {
      // If equation contains multiple lines, use MathJax
      if (equation.includes('\n') || equation.includes('\\begin{cases}')) {
        // Ensure equation has proper spacing and formatting
        return `<div class="mathjax-block tex2jax_process">\n$$${equation}$$\n</div>`;
      }
      return match; // Keep the original $$ delimiters for KaTeX to handle
    });

    // Fix table content and ensure LaTeX delimiters are preserved
    processed = processed.replace(/\|\s*\$(.*?)\$\s*\|/g, '| \\$$1\\$ |');

    // Add proper spacing around equations for better rendering
    processed = processed
      // Add spacing around block equations if not already present
      .replace(/([^\n])\$\$/g, '$1\n$$')
      .replace(/\$\$([^\n])/g, '$$\n$1')
      // Clean up excessive newlines
      .replace(/\n{3,}/g, '\n\n');

    // Check for cases where delimiters might have been incorrectly processed
    processed = processed.replace(/\$([\s\S]*?)\$/g, (match, equation) => {
      // If any equation has lost its delimiters, fix it
      return `$${equation}$`;
    });
    
    // Restore escaped dollar signs
    processed = processed.replace(/___ESCAPED_DOLLAR___/g, '\\$');

    return processed;
  }
  
  /**
   * Special processing for cases/piecewise functions which are common in fuzzy logic
   * @param content Content to process
   * @returns Processed content with properly formatted cases
   */
  private processCasesEquations(content: string): string {
    // Find all equations with \begin{cases} ... \end{cases}
    return content.replace(/\$\$([\s\S]*?\\begin\{cases\}[\s\S]*?\\end\{cases\}[\s\S]*?)\$\$/g, (match, equation) => {
      // Always use MathJax for cases equations
      return `<div class="mathjax-block cases-equation tex2jax_process">\n$$${equation}$$\n</div>`;
    });
  }
  
  /**
   * Manually trigger MathJax rendering after component updates
   * This should be called in ngAfterViewInit or after content changes
   */
  renderMathJax(): void {
    if (typeof window !== 'undefined' && (window as any).MathJax) {
      const MathJax = (window as any).MathJax;
      setTimeout(() => {
        MathJax.typesetPromise && MathJax.typesetPromise();
      }, 100);
    }
  }
} 
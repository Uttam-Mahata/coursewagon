import { Injectable } from '@angular/core';
import { Chart, ChartConfiguration, registerables } from 'chart.js';

@Injectable({
  providedIn: 'root'
})
export class ChartRendererService {
  private charts: Map<string, Chart> = new Map();

  constructor() {
    // Register all Chart.js components
    Chart.register(...registerables);
  }

  /**
   * Parse content for chart data blocks and return processed content
   * Chart blocks should be in format:
   * ```chart-json
   * {
   *   "type": "bar",
   *   "data": {...},
   *   "options": {...}
   * }
   * ```
   */
  processContent(content: string): string {
    if (!content) return content;

    // Replace chart blocks with placeholder divs
    const chartRegex = /```chart-json\s*\n([\s\S]*?)```/g;
    let chartIndex = 0;
    
    return content.replace(chartRegex, (match, chartDataStr) => {
      const chartId = `chart-${Date.now()}-${chartIndex++}`;
      // Store chart data in a data attribute (escaped)
      const escapedData = this.escapeHtml(chartDataStr.trim());
      return `<div class="chart-container" data-chart-id="${chartId}" data-chart-config="${escapedData}"></div>`;
    });
  }

  /**
   * Render all charts in the DOM
   */
  renderCharts(): void {
    // Wait for DOM to be ready
    setTimeout(() => {
      const chartContainers = document.querySelectorAll('.chart-container');
      
      chartContainers.forEach((container) => {
        const chartId = container.getAttribute('data-chart-id');
        const chartConfigStr = container.getAttribute('data-chart-config');
        
        if (!chartId || !chartConfigStr) return;

        // Destroy existing chart if it exists
        if (this.charts.has(chartId)) {
          this.charts.get(chartId)?.destroy();
        }

        try {
          const chartConfig = JSON.parse(this.unescapeHtml(chartConfigStr));
          
          // Create canvas element
          const canvas = document.createElement('canvas');
          canvas.id = chartId;
          container.innerHTML = '';
          container.appendChild(canvas);

          // Create chart
          const ctx = canvas.getContext('2d');
          if (ctx) {
            const chart = new Chart(ctx, chartConfig);
            this.charts.set(chartId, chart);
          }
        } catch (error) {
          console.error('Error rendering chart:', error);
          container.innerHTML = '<div class="chart-error">Error rendering chart. Invalid configuration.</div>';
        }
      });
    }, 100);
  }

  /**
   * Destroy all charts (cleanup)
   */
  destroyAllCharts(): void {
    this.charts.forEach(chart => chart.destroy());
    this.charts.clear();
  }

  /**
   * Escape HTML for data attributes
   */
  private escapeHtml(text: string): string {
    const map: { [key: string]: string } = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  }

  /**
   * Unescape HTML from data attributes
   */
  private unescapeHtml(text: string): string {
    const map: { [key: string]: string } = {
      '&amp;': '&',
      '&lt;': '<',
      '&gt;': '>',
      '&quot;': '"',
      '&#039;': "'"
    };
    return text.replace(/&amp;|&lt;|&gt;|&quot;|&#039;/g, m => map[m]);
  }

  /**
   * Validate chart configuration
   */
  validateChartConfig(config: any): boolean {
    return config && 
           typeof config === 'object' && 
           config.type && 
           config.data &&
           config.data.labels &&
           config.data.datasets;
  }
}

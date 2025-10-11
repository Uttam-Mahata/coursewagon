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
   * Render all charts in the DOM
   * Charts are already converted to div.chart-container by backend
   */
  renderCharts(): void {
    // Wait for DOM to be ready
    setTimeout(() => {
      const chartContainers = document.querySelectorAll('.chart-container:not([data-chart-rendered])');
      
      chartContainers.forEach((container) => {
        const chartId = container.getAttribute('data-chart-id');
        const chartConfigStr = container.getAttribute('data-chart-config');
        
        if (!chartId || !chartConfigStr) return;

        // Destroy existing chart if it exists
        if (this.charts.has(chartId)) {
          this.charts.get(chartId)?.destroy();
        }

        try {
          // Parse the configuration
          const chartConfig = JSON.parse(chartConfigStr);
          
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
            // Mark as rendered to avoid re-rendering
            container.setAttribute('data-chart-rendered', 'true');
          }
        } catch (error) {
          console.error('Error rendering chart:', error, chartConfigStr);
          container.innerHTML = '<div class="chart-error">Error rendering chart. Invalid configuration.</div>';
          container.setAttribute('data-chart-rendered', 'true');
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

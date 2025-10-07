import { Component, OnInit, HostListener } from '@angular/core';

@Component({
  selector: 'app-help-center',
  standalone: false,
  templateUrl: './help-center.component.html',
  styleUrl: './help-center.component.css'
})
export class HelpCenterComponent implements OnInit {
  searchQuery: string = '';
  openFaqs: boolean[] = new Array(21).fill(false);
  showBackToTop: boolean = false;

  ngOnInit(): void {
    // Scroll to top on component load
    window.scrollTo(0, 0);
  }

  @HostListener('window:scroll', [])
  onWindowScroll() {
    // Show back to top button when scrolled down 300px
    this.showBackToTop = window.pageYOffset > 300;
  }

  toggleFaq(index: number): void {
    this.openFaqs[index] = !this.openFaqs[index];
  }

  onSearch(): void {
    // Search functionality can be implemented here
    // For now, it's a placeholder for future enhancement
    console.log('Searching for:', this.searchQuery);
  }

  scrollToSection(sectionId: string): void {
    const element = document.getElementById(sectionId);
    if (element) {
      const offset = 80; // Adjust for fixed header if any
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  }

  scrollToTop(): void {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
}

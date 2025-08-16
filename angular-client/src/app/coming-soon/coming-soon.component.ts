import { Component } from '@angular/core';
import { faTools, faArrowLeft } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-coming-soon',
  templateUrl: './coming-soon.component.html',
  styleUrl: './coming-soon.component.css',
  standalone: false
})
export class ComingSoonComponent {
  faTools = faTools;
  faArrowLeft = faArrowLeft;
}

import { Component } from '@angular/core';
import { faTools, faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-coming-soon',
  templateUrl: './coming-soon.component.html',
  styleUrl: './coming-soon.component.css',
  standalone: true,
  imports: [FontAwesomeModule, RouterModule]
})
export class ComingSoonComponent {
  faTools = faTools;
  faArrowLeft = faArrowLeft;
}

import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-how-it-works',
  templateUrl: './how-it-works.component.html',
  styleUrls: ['./how-it-works.component.css'],
  standalone: false
})
export class HowItWorksComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
    // Scroll to top on component load
    window.scrollTo(0, 0);
  }

}

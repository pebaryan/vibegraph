import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-landing-home',
  templateUrl: './landing-home.component.html',
  styleUrls: ['./landing-home.component.scss']
})
export class LandingHomeComponent implements OnInit {
  constructor(private router: Router) {}

  ngOnInit(): void {
    // If user has already visited, redirect to query editor
    const hasSeen = localStorage.getItem('hasSeenLanding');
    if (hasSeen === 'true') {
      this.router.navigate(['/query']);
      return;
    }
    // Mark as seen
    localStorage.setItem('hasSeenLanding', 'true');
  }
}

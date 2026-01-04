import { Component } from '@angular/core';
import { AppState } from '@app/state/app.state';

import { OnInit } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';


@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.css']
})
export class NavigationComponent implements OnInit {
  selectedEntity: any = null;
  displayedColumns: string[] = [];
  dataSource = new MatTableDataSource<any>([]);

  constructor(public state: AppState) {}

  ngOnInit() {
    this.state.result$.subscribe(res => {
      if (Array.isArray(res) && res.length > 0) {
        this.displayedColumns = Object.keys(res[0]);
        this.dataSource.data = res;
      } else {
        this.displayedColumns = [];
        this.dataSource.data = [];
      }
    });
  }

  selectEntity(entity: any) {
    this.selectedEntity = entity;
  }
}


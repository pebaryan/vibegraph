import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';
import { MonacoEditorModule } from 'ngx-monaco-editor';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatListModule } from '@angular/material/list';
import { MatTableModule } from '@angular/material/table';

import { AppComponent } from '@app/app.component';
import { QueryEditorComponent } from '@app/components/query-editor/query-editor.component';
import { GraphViewComponent } from '@app/components/graph-view/graph-view.component';
import { NavigationComponent } from '@app/components/navigation/navigation.component';
import { QueryHistoryComponent } from '@app/components/query-history/query-history.component';
import { QueryResultsComponent } from '@app/components/query-results/query-results.component';

const routes: Routes = [
  { path: '', redirectTo: 'query', pathMatch: 'full' },
  { path: 'query', component: QueryEditorComponent },
  { path: 'graph', component: GraphViewComponent },
  { path: 'nav', component: NavigationComponent },
  { path: '**', redirectTo: 'query' }
];

@NgModule({
  declarations: [
    AppComponent,
    QueryEditorComponent,
    GraphViewComponent,
    NavigationComponent,
    QueryHistoryComponent,
    QueryResultsComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatListModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}

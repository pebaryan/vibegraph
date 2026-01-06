import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatListModule } from '@angular/material/list';
import { MatRadioModule } from '@angular/material/radio';
import { MatOptionModule } from '@angular/material/core';
import { MatTableModule } from '@angular/material/table';
import {MatCardModule} from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';

import { MonacoEditorModule } from 'ngx-monaco-editor-v2';

import { AppComponent } from '@app/app.component';
import { QueryEditorComponent } from '@app/components/query-editor/query-editor.component';
import { SettingsComponent } from '@app/components/settings/settings.component';
import { GraphViewComponent } from '@app/components/graph-view/graph-view.component';
import { NavigationComponent } from '@app/components/navigation/navigation.component';
import { QueryHistoryComponent } from '@app/components/query-history/query-history.component';
import { QueryResultsComponent } from '@app/components/query-results/query-results.component';
import { GraphListComponent } from '@app/components/graph-list/graph-list.component';
import { GraphDialogComponent } from '@app/components/graph-dialog/graph-dialog.component';
import { LandingHomeComponent } from '@app/components/landing-home/landing-home.component';
import { SearchComponent } from '@app/components/search/search.component';

const routes: Routes = [
  { path: '', component: LandingHomeComponent },
  { path: 'query', component: QueryEditorComponent },
  { path: 'graph', component: GraphViewComponent },
  { path: 'graphs', component: GraphListComponent },
  { path: 'search', component: SearchComponent },
    { path: 'settings', component: SettingsComponent }
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
    QueryResultsComponent,
    GraphListComponent,
    GraphDialogComponent,
    LandingHomeComponent,
    SearchComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    MatToolbarModule,
    MatDialogModule,
    MatSnackBarModule,
    MatFormFieldModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatListModule,
    MatRadioModule,
    MatOptionModule,
    MatTableModule,
    MatCardModule,
    MatSelectModule,
    MonacoEditorModule.forRoot()
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}

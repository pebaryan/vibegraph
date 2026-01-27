import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { HttpClientModule } from "@angular/common/http";
import { RouterModule, Routes } from "@angular/router";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatDialogModule } from "@angular/material/dialog";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatInputModule } from "@angular/material/input";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatListModule } from "@angular/material/list";
import { MatRadioModule } from "@angular/material/radio";
import { MatOptionModule } from "@angular/material/core";
import { MatTableModule } from "@angular/material/table";
import { MatCardModule } from "@angular/material/card";
import { MatSelectModule } from "@angular/material/select";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { MatTabsModule } from "@angular/material/tabs";
import { MatExpansionModule } from "@angular/material/expansion";

import { MonacoEditorModule } from "ngx-monaco-editor-v2";
import { MomentModule } from 'ngx-moment';

import { AppComponent } from '@app/app.component';
import { QueryEditorComponent } from '@app/components/query-editor/query-editor.component';
import { GraphViewComponent } from '@app/components/graph-view/graph-view.component';
import { GraphNavigationComponent } from '@app/components/graph-navigation/graph-navigation.component';
import { AddTripleComponent } from '@app/components/add-triple/add-triple.component';
import { QueryHistoryComponent } from '@app/components/query-history/query-history.component';
import { QueryResultsComponent } from '@app/components/query-results/query-results.component';
import { GraphListComponent } from '@app/components/graph-list/graph-list.component';
import { GraphDialogComponent } from '@app/components/graph-dialog/graph-dialog.component';
import { LandingHomeComponent } from '@app/components/landing-home/landing-home.component';
import { SearchComponent } from '@app/components/search/search.component';
import { SettingsComponent } from '@app/components/settings/settings.component';
import { ExtractComponent } from "@app/components/extract/extract.component";
import { PrefixDialogComponent } from "./components/prefix-dialog/prefix-dialog.component";
import { ConfirmDialogComponent } from "./components/confirm-dialog/confirm-dialog.component";
import { SnackbarComponent } from "./components/snackbar/snackbar.component";

const routes: Routes = [
  { path: '', component: LandingHomeComponent },
  { path: 'query', component: QueryEditorComponent },
  { path: 'graph', component: GraphViewComponent },
  { path: 'graphs', component: GraphListComponent },
  { path: 'search', component: SearchComponent },
  { path: 'extract', component: ExtractComponent },
  { path: 'graph-navigation', component: GraphNavigationComponent },
  { path: "history", component: QueryHistoryComponent },
  { path: 'settings', component: SettingsComponent },
  { path: '**', redirectTo: 'graphs' }
];

@NgModule({
  declarations: [
    AppComponent,
    AddTripleComponent,
    QueryEditorComponent,
    GraphViewComponent,
    GraphNavigationComponent,
    QueryHistoryComponent,
    QueryResultsComponent,
    GraphListComponent,
    GraphDialogComponent,
    PrefixDialogComponent,
    ConfirmDialogComponent,
    SnackbarComponent,
    LandingHomeComponent,
    SearchComponent,
    ExtractComponent,
    SettingsComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
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
    MatCheckboxModule,
    MatAutocompleteModule,
    MatTabsModule,
    MatExpansionModule,
    MonacoEditorModule.forRoot(),
    MomentModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}

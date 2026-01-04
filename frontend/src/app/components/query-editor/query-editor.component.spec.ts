import { ComponentFixture, TestBed } from '@angular/core/testing';
import { QueryEditorComponent } from './query-editor.component';
import { QueryService } from '@app/services/query.service';
import { AppState } from '@app/state/app.state';
import { of, throwError } from 'rxjs';

class MockQueryService {
  execute(query: string) {
    return of({ rows: [] });
  }
}

class MockAppState {
  setLastResult = jasmine.createSpy('setLastResult');
  addToHistory = jasmine.createSpy('addToHistory');
}

describe('QueryEditorComponent', () => {
  let component: QueryEditorComponent;
  let fixture: ComponentFixture<QueryEditorComponent>;
  let mockService: MockQueryService;
  let mockState: MockAppState;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [QueryEditorComponent],
      providers: [
        { provide: QueryService, useClass: MockQueryService },
        { provide: AppState, useClass: MockAppState }
      ]
    }).compileComponents();

    mockService = TestBed.inject(QueryService) as any;
    mockState = TestBed.inject(AppState) as any;
    fixture = TestBed.createComponent(QueryEditorComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should execute query and update state', () => {
    component.query = 'SELECT * WHERE {}';
    component.execute();
    expect(component.loading).toBeTrue();
    expect(mockService.execute).toHaveBeenCalledWith(component.query);
    // After async completion
    fixture.whenStable().then(() => {
      expect(component.loading).toBeFalse();
      expect(mockState.setLastResult).toHaveBeenCalled();
      expect(mockState.addToHistory).toHaveBeenCalledWith(component.query);
    });
  });
});

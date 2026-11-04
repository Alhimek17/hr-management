import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EmployeeCardComponent } from './employee-card.component';

describe('EmployeeCardComponent', () => {
  let fixture: ComponentFixture<EmployeeCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EmployeeCardComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(EmployeeCardComponent);
  });

  it('renders name and number', () => {
    fixture.componentInstance.fullName = 'Иванов И.И.';
    fixture.componentInstance.employeeNumber = '12345';
    fixture.detectChanges();
    
    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Иванов И.И.');
    expect(text).toContain('12345');
  });
});
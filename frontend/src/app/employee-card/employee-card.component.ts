import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-employee-card',
  standalone: true,
  template: `<div class="card">{{ fullName }} — {{ employeeNumber }}</div>`,
})
export class EmployeeCardComponent {
  @Input() fullName = '';
  @Input() employeeNumber = '';
}
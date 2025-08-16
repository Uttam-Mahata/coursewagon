import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'filterById',
  standalone: false
})
export class FilterByIdPipe implements PipeTransform {
  transform(items: any[] | null, id: number | null): any {
    if (!items || !id) return null;
    return items.find(item => item.id === id);
  }
}

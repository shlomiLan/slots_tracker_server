import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import 'rxjs/add/operator/do'
import 'rxjs/add/operator/map'
/*
  Generated class for the ApiServiceProvider provider.

  See https://angular.io/guide/dependency-injection for more info on providers
  and Angular DI.
*/
@Injectable()
export class ApiServiceProvider {
  private baseURL = 'http://localhost:5000/';

  constructor(public http: HttpClient) {
  }

  getExpenses(){
    return this.http.get(this.baseURL + 'expenses/')
    .do((response: Response) => console.log(response))
  }

}

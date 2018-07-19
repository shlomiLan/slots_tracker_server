import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';


@Injectable()
export class ApiServiceProvider {
  private baseURL = 'http://127.0.0.1:5000/';

  constructor(public http: HttpClient) {
  }

  getExpenses(){
    return this.http.get(this.baseURL + 'expenses/')
  }

  getPayMethods(){
    return this.http.get(this.baseURL + 'pay_methods/')
  }

  creatOrUpdateExpense(data){
    let id = this.get_id(data);
    this.clean_data(data);
    let url = this.baseURL;

    if (id){
      url = url + id;
    }
    
    return this.http.post(this.baseURL + 'expenses/', data);
  }

  createOrUpdatePayMethod(data){
    let id = this.get_id(data);
    this.clean_data(data);
    let url = this.baseURL;

    if (id){
      url = url + id;
    }

    return this.http.post(this.baseURL + 'pay_methods/', data);
  }

  get_id(data){
    if (this.data_has_id(data)){
      return data._id.$oid
    }

    return undefined;
  }

  data_has_id(data){
    if (data){
      if (data._id){
        if (data._id.$oid){
          return true;
        }
      }
    }

    return false;
  }

  clean_data(data){
    if (this.data_has_id(data)){
      delete data._id
    }
  }
}

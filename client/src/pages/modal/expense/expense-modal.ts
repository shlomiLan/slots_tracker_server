import { Component } from '@angular/core';
import { FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { IonicPage, NavParams, ViewController } from 'ionic-angular';

@IonicPage()
@Component({
  template: `
    <ion-header>
      <ion-navbar>
        <ion-title>Modal</ion-title>
        <ion-buttons end>
          <button ion-button (click)="closeModal()">Close</button>
        </ion-buttons>
      </ion-navbar>
    </ion-header>

    <ion-content padding>
      <form [formGroup]="expense" (ngSubmit)="saveData()">
        <ion-item>
          <ion-label>Amount:</ion-label>
          <ion-input formControlName="amount" type="number"></ion-input>
        </ion-item>
        <ion-item>
          <ion-label>Descreption:</ion-label>
          <ion-input formControlName="descreption" type="text"></ion-input>
        </ion-item>
        <ion-item>
          <ion-label>Pay method:</ion-label>
          <ion-select [formControlName]="pay_method" (ionChange)="payMethodChange($event);" interface="popover">
            <ion-option *ngFor="let item of methods.controls" [value]="item.value._id">
              {{item.value.name}}
            </ion-option>
          </ion-select>
        </ion-item>
        <button ion-button type="submit" [disabled]="!expense.valid">Submit</button>
    </form>
    </ion-content>
  `
})

export class ExpenseModalPage {
  private expense : FormGroup;
  private methods : FormArray;


  constructor( private navParams: NavParams, private formBuilder: FormBuilder, private viewCtrl: ViewController ) {
    this.expense = this.formBuilder.group(this.navParams.get('data'));
    this.methods = this.formBuilder.array(this.navParams.get('methods'));
    // Modify the pay_method data for the select element
    this.expense.controls['pay_method'].setValue(this.expense.value.pay_method._id);
  }

  saveData(){
    this.expense.controls['pay_method'].setValue({"_id": this.expense.value.pay_method});
    this.viewCtrl.dismiss(this.expense.value);
  }

  closeModal(){
    this.viewCtrl.dismiss();
  }

  payMethodChange(value){
    this.expense.controls['pay_method'].setValue(value);
  }
}

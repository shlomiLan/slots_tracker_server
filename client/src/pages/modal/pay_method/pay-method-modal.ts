import { Component } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
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
      <form [formGroup]="pay_method" (ngSubmit)="saveData()">
        <ion-item>
          <ion-label>Name:</ion-label>
          <ion-input formControlName="name" type="text"></ion-input>
        </ion-item>
        <button ion-button type="submit" [disabled]="!pay_method.valid">Submit</button>
      </form>
    </ion-content>
  `
})

export class PayMethodModalPage {
  private pay_method : FormGroup;

  constructor( private navParams: NavParams, private formBuilder: FormBuilder, private viewCtrl: ViewController ) {
    this.pay_method = this.formBuilder.group(this.navParams.get('data'));
  }

  saveData(){
    this.viewCtrl.dismiss(this.pay_method.value);
  }

  closeModal(){
    this.viewCtrl.dismiss();
  }
}

// <ion-item>
//   <ion-label>Pay method:</ion-label>
//   <ion-input formControlName="pay_method" type="text"></ion-input>
// </ion-item>
// <ion-item>
//   <ion-label>Timestamp:</ion-label>
//   <ion-input formControlName="timestamp" type="text"></ion-input>
//   <!-- <ion-datetime displayFormat="DD MMM YYYY" pickerFormat="DD MMM YYYY"></ion-datetime> -->
// </ion-item>

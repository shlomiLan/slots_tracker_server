import { Component } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { IonicPage, NavParams, ViewController } from 'ionic-angular';

/**
 * Generated class for the ModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

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
          <ion-input formControlName="pay_method" type="text"></ion-input>
        </ion-item>
        <ion-item>
          <ion-label>Timestamp:</ion-label>
          <ion-input formControlName="timestamp" type="text"></ion-input>
          <!-- <ion-datetime displayFormat="DD MMM YYYY" pickerFormat="DD MMM YYYY"></ion-datetime> -->
       </ion-item>

        <ion-item>
          <ion-label>Board:</ion-label>
          <ion-input formControlName="board" type="text"></ion-input>
        </ion-item>
        <button ion-button type="submit" [disabled]="!expense.valid">Submit</button>
      </form>
    </ion-content>
  `
})

export class ModalPage {
  private expense : FormGroup;

  constructor( private navParams: NavParams, private formBuilder: FormBuilder, private viewCtrl: ViewController ) {
    this.expense = this.formBuilder.group(this.navParams.get('data'));
  }

  saveData(){
    this.viewCtrl.dismiss(this.expense.value);
  }

  closeModal(){
    this.viewCtrl.dismiss();
  }
}

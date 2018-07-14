import { Component } from '@angular/core';
import { NavController, ModalController, NavParams, ModalOptions } from 'ionic-angular';
import { ApiServiceProvider } from '../../providers/api-service/api-service'


@Component({
  selector: 'page-expenses',
  templateUrl: 'expenses.html'
})

export class ExpensesPage {
  selectedItem: any;
  icons: string[];
  items: any;

  constructor(public navCtrl: NavController, public navParams: NavParams, public modalCtrl: ModalController,
              private api: ApiServiceProvider) {

    // Inittialize data
    this.getExpenses();
  }

  // Logic for creating or updating expense
  editOrCreateExpense(data = undefined) {
    if (!data){
      // TODO: Remove this section to return an empty structure
      data = {amount: undefined, descreption: ''}
      // pay_method: '', timestamp: '', board: ''}
    }

    const myModalOptions: ModalOptions = {
      enableBackdropDismiss: false
    }

    let modal = this.modalCtrl.create('ModalPage', {data: data}, myModalOptions);
      modal.onDidDismiss(data => {
        if (data){
          this.api.creatOrUpdateExpense(data).subscribe();
          // TODO: find way to do automatically
          // this.getExpenses();
        }
      });

      modal.present();
  }

  getExpenses() {
    this.api.getExpenses().subscribe(response => this.items = response);
  }
}

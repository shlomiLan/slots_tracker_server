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
  items: any; //Array<{amount: number, descreption: string, pay_method: string, timestamp: string, board: string}>;

  constructor(public navCtrl: NavController, public navParams: NavParams, public modalCtrl: ModalController,
              private api: ApiServiceProvider) {

    this.getExpenses();
    this.items = []
  }

  editOrCreateExpense(data = undefined, index = undefined) {
    const myModalOptions: ModalOptions = {
      enableBackdropDismiss: false
    }

    if (!data){
      data = {amount: undefined, descreption: '', pay_method: '', timestamp: '', board: ''}
    }

    let modal = this.modalCtrl.create('ModalPage', {data: data}, myModalOptions);
      modal.onDidDismiss(data => {
        if (data){
          if (index){
            this.items[index] = data;
          }else{
            this.items.push(data);
          }
        }
      });

      modal.present();
  }

  getExpenses() {
    this.api.getExpenses().subscribe(response => this.items = response);
  }
}

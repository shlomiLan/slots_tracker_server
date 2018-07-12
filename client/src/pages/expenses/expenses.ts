import { Component } from '@angular/core';
import { NavController, ModalController, Platform, NavParams, ViewController } from 'ionic-angular';



@Component({
  selector: 'page-expenses',
  templateUrl: 'expenses.html'
})

export class ExpensesPage {
  selectedItem: any;
  icons: string[];
  items: Array<{amount: number, descreption: string, pay_method: string, timestamp: string, board: string}>;

  constructor(public navCtrl: NavController, public navParams: NavParams, public modalCtrl: ModalController) {
    // If we navigated to this page, we will have an item available as a nav param
    this.selectedItem = navParams.get('item');

    this.items = [];

    this.items = [
      { amount: 100, descreption: 'Random text', pay_method: 'Visa', timestamp: '1/1/2000', board: 'Board 1'},
      { amount:  50, descreption: 'Random text', pay_method: 'Visa', timestamp: '1.1.2000', board: 'Board 2'},
      { amount: 300, descreption: 'Random text', pay_method: 'Visa', timestamp: '1.1.2000', board: 'Board 3'},
      { amount: 600, descreption: 'Random text', pay_method: 'Visa', timestamp: '1.1.2000', board: 'Board 1'},
      { amount:  10, descreption: 'Random text', pay_method: 'Visa', timestamp: '1.1.2000', board: 'Board 2'},
      { amount: 100, descreption: 'Random text', pay_method: 'Visa', timestamp: '1.1.2000', board: 'Board 3'},
    ];


  }

  editOrCreateExpense(data = undefined, index = undefined) {
    if (!data){
      data = {amount: undefined, descreption: '', pay_method: '', timestamp: '', board: ''}
    }

    let modal = this.modalCtrl.create('ModalPage', {data: data});
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
}

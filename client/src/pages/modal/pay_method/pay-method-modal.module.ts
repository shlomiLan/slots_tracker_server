import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { PayMethodModalPage } from './pay-method-modal';

@NgModule({
  declarations: [
    PayMethodModalPage
  ],
  imports: [
    IonicPageModule.forChild(PayMethodModalPage),
  ],
})
export class ModalPageModule {}

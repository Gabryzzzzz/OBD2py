import { HostListener, Injectable } from '@angular/core';

@Injectable({providedIn: 'root'})
export class ResponsiveService {

  pc_mode: boolean = true;

  constructor() { }

  setup_platform(){
    if(window.innerWidth < window.innerHeight){
      this.pc_mode = false;
    } else{
      this.pc_mode = true;
    }
  }

  get_width(){
    return window.innerWidth;
  }

  get_height(){
    return window.innerHeight;
  }

}

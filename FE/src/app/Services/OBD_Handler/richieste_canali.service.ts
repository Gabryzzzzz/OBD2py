import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';

@Injectable({providedIn: 'root'})
export class RichiesteCanaliService {
  constructor(private socket: Socket) {
  }

  abilita_canale(canale: string, abilita: boolean) {
    let data: richiesta_canali = {
      canale: canale,
      abilita: abilita
    }
    this.socket.emit('enable_channel', data);
  }

}

/*

*/

//interface
export interface richiesta_canali {
  canale: string;
  abilita: boolean;
}

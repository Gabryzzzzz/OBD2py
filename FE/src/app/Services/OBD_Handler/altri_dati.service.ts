import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';

@Injectable({providedIn: 'root'})
export class AltriDatiService {
  constructor(private socket: Socket) {
  }

  getMessage() {
    return this.socket.fromEvent<altri_dati, any>("altri_dati").pipe(map(data => data));
  }

}

/*

*/

//interface
export interface altri_dati {
  km_percorsi: number;
}

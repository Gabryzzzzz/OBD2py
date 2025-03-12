import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';

@Injectable({providedIn: 'root'})
export class ConsumiCarburanteService {
  constructor(private socket: Socket) {
  }

  getMessage() {
    return this.socket.fromEvent<consumi_carburante, any>("consumi").pipe(map(data => data));
  }

}

/*

*/

//interface
export interface consumi_carburante {
  livello_carburante: number;
  consumo_istantaneo: number;
  pressione_carburante: number;
}

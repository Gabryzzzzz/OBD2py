import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';

@Injectable({providedIn: 'root'})
export class EmissioniService {
  constructor(private socket: Socket) {
  }

  getMessage() {
    return this.socket.fromEvent<emissioni, any>("emissioni").pipe(map(data => data));
  }

}

/*

*/

//interface
export interface emissioni {
  sensore_o2_banco_1_sensore_1: number;
  pressione_vapori_evap: number;
  temp_catalizzatore: number;
}

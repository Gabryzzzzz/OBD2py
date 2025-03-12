import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';

@Injectable({providedIn: 'root'})
export class MotorePrestazioniService {
  constructor(private socket: Socket) {
  }

  getMessage() {
    return this.socket.fromEvent<motore_prestazioni, any>("motore").pipe(map(data => data));
  }

}

/*
        rpm: obd.commands.RPM,
        velocita: obd.commands.SPEED,
        acceleratore: obd.commands.THROTTLE_POS,
        pressione_map: obd.commands.MAP,
        flusso_maf: obd.commands.MAF
*/

//interface
export interface motore_prestazioni {
  rpm: number;
  velocita: number;
  acceleratore: number;
  pressione_map: number;
  flusso_maf: number;
}

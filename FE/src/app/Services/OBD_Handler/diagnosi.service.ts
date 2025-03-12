import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';

@Injectable({providedIn: 'root'})
export class DiagnosiService {
  constructor(private socket: Socket) {
  }

  getMessage() {
    return this.socket.fromEvent<diagnosi, any>("diagnostica").pipe(map(data => data));
  }

}

/*
codici_errore_dtc: obd.commands.GET_DTC,
        stato_mil: obd.commands.GET_DTC,
        tensione_ecu: obd.commands.CONTROL_MODULE_VOLTAGE,
        tempo_reset_ecu: obd.commands.RUN_TIME
*/

//interface
export interface diagnosi {
  codici_errore_dtc: string;
  stato_mil: string;
  tensione_ecu: number;
  tempo_reset_ecu: number;
}

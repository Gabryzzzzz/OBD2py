import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';

@Injectable({providedIn: 'root'})
export class TemperatureSensoriService {
  constructor(private socket: Socket) {
  }

  getMessage() {
    return this.socket.fromEvent<remperature_sensori, any>("temperature").pipe(map(data => data));
  }

}

/*
  temp_liquido_refrigerante: obd.commands.COOLANT_TEMP,
        temp_olio_motore: obd.commands.OIL_TEMP,
        temp_aspirazione: obd.commands.INTAKE_TEMP,
        temp_ambiente: obd.commands.AMBIANT_AIR_TEMP
*/

//interface
export interface remperature_sensori {
  temp_liquido_refrigerante: number;
  temp_olio_motore: number;
  temp_aspirazione: number;
  temp_ambiente: number;
}

import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';
import { obd_data } from '../Models/Interfaces/obd.interface';

@Injectable()
export class ObdService {

  constructor(private socket: Socket) {
  }

  getMessage() {
    return this.socket.fromEvent<obd_data, any>("obd_data").pipe(map(data => data));
  }
}

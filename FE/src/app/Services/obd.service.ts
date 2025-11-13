import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';
import { obd_data } from '../Models/Interfaces/obd.interface';

@Injectable()
export class ObdService {

  configuration_subj = this.socket.fromEvent<string, any>("config").pipe(map(data => data));

  constructor(private socket: Socket) {

  }

  getMessage() {
    return this.socket.fromEvent<obd_data, any>("obd_data").pipe(map(data => data));
  }

  //get configuration
  getConfiguration() {
    this.socket.emit("get_config");
  }

  //set configuration
  setConfiguration(config: config_obd) {
    this.socket.emit("set_config", JSON.stringify(config));
  }

  //restart obd request
  restart_obd() {
    this.socket.emit("restart_obd");
  }

  //stop_obd
  stop_obd() {
    this.socket.emit("stop_obd");
  }

}

export interface config_obd {
  OBD_PORT: string;
  UPDATE_INTERVAL: number;
  SHOW_PRINTS: boolean;
  TRY_TIMES: number;
  TRY_SLEEP: number;
  TRY_ENABLED: boolean;
  LED_CONFIG: string;
}

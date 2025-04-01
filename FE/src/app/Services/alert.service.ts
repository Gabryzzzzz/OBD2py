import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { Subject } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable()
export class AlertService {
  constructor(private socket: Socket) {}

  //build a subject to send the errors to the component
  errors_subject = new Subject<alert_interface>();

  getMessage() {
    return this.socket
      .fromEvent<alert_interface, any>('popup_channel')
      .pipe(map((data) => {
        this.errors_subject.next(data);
        console.log(data);
      }));
  }
}

export interface alert_interface {
  type: string;
  //category of the error
  title: string;
  //message of the error
  message: string;
  //timestamp of the error
  timestamp: Date;
}

import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs/operators';

@Injectable()
export class SocketService {

  constructor(private socket: Socket) {
  }

  sendMessage(channel: string, msg: string) {
    this.socket.emit(channel, msg);
  }

  getMessage(channel: string) {
    return this.socket.fromEvent(channel).pipe(map(data => data));
  }
}

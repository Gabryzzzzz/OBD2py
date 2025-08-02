import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';

@Injectable({providedIn: 'root'})
export class SocketRequestsService {
  constructor(private socket: Socket) { }

  //test send on channel test
  test_send() {
    this.socket.emit('test', 'test');
  }

  //test receiver
  test_led(data: string) {
    return this.socket.emit('test_led', data);
  }

  //test receiver
  test_receiver() {
    return this.socket.fromEvent<string, any>('test');
  }

  //send local ip request
  get_local_ip() {
    this.socket.emit('request_ip', 'request_ip');
  }

  //local ip receiver
  get_local_ip_receiver() {
    return this.socket.fromEvent<any, any>('local_ip');
  }

}

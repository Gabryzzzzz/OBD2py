import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';

@Injectable({
  providedIn: 'root',
})
export class SocketConnectionService {
  private primaryUrl = 'http://localhost:5000';
  private secondaryUrl = 'http://localhost:5001';
  private currentUrl = this.primaryUrl;

  constructor(public socket: Socket) {
    this.connect();
  }

  private connect() {
    this.socket.ioSocket.io.opts.hostname = new URL(this.currentUrl).hostname;
    this.socket.ioSocket.io.opts.port = new URL(this.currentUrl).port;
    this.socket.connect();

    this.socket.on('connect_error', () => {
      if (this.currentUrl === this.primaryUrl) {
        this.currentUrl = this.secondaryUrl;
        this.socket.disconnect();
        this.connect();
      }
    });
  }
}

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

  //test send on channel test
  get_position() {
    return this.socket.fromEvent<string, any>('posizione');
  }

  //send local ip request
  get_local_ip() {
    this.socket.emit('request_ip', 'request_ip');
  }

  //local ip receiver
  get_local_ip_receiver() {
    return this.socket.fromEvent<any, any>('local_ip');
  }

  /**
   * Requests historical data for a specific category within a date range.
   * @param category The name of the data category (e.g., 'motore_prestazioni').
   * @param startDate The start of the date range in 'YYYY-MM-DD HH:MM:SS' format.
   * @param endDate The end of the date range in 'YYYY-MM-DD HH:MM:SS' format.
   */
  requestDataByRange(category: string, startDate: string, endDate: string) {
    const payload = {
      category,
      startDate,
      endDate
    };
    this.socket.emit('get_data_by_range', payload);
  }

  /**
   * Listens for the result of a data range request.
   * @returns An observable that emits the data array.
   */
  getDataRangeResult() {
    return this.socket.fromEvent<any[], any>('data_range_result');
  }
}

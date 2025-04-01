import { Injectable } from '@angular/core';

@Injectable({providedIn: 'root'})
export class UtilsService {
  constructor() { }

  //get local ip address of client
  async get_public_ip() {
    const response = await fetch('https://api64.ipify.org?format=json');
    const data = await response.json();
    return data.ip;
  }

  // getLocalIp(): Promise<string> {
  //   return new Promise<string>((resolve, reject) => {
  //     const pc = new RTCPeerConnection({ iceServers: [] });
  //     pc.createDataChannel("");

  //     pc.onicecandidate = (event) => {
  //       if (event.candidate) {
  //         const candidate = event.candidate.candidate;
  //         const ipMatch = candidate.match(/(\d+\.\d+\.\d+\.\d+)/);
  //         if (ipMatch) {
  //           resolve(ipMatch[1]);
  //         }
  //       }
  //       pc.close();
  //     };

  //     pc.createOffer()
  //       .then((offer) => pc.setLocalDescription(offer))
  //       .catch((error) => reject(error));
  //   });
  // }

}

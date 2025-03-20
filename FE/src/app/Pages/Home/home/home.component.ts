import { Component, OnInit } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map } from 'rxjs';
import { obd_data } from 'src/app/Models/Interfaces/obd.interface';
import { ObdService } from 'src/app/Services/obd.service';
import {
  motore_prestazioni,
  MotorePrestazioniService,
} from 'src/app/Services/OBD_Handler/motore_prestazioni.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  standalone: false,
})
export class HomeComponent implements OnInit {
  maxRpm: number = 7200; // RPM massimo
  rpmPercentage: number = 0; // Altezza della barra
  rpmColor: string = 'green'; // Colore iniziale

  maxThrottle: number = 100; // RPM massimo
  throttlePercentage: number = 0; // Altezza della barra
  throttleColor: string = 'green'; // Colore iniziale

  obd_data: motore_prestazioni | undefined;

  constructor(private motore: MotorePrestazioniService) {}

  ngOnChanges() {}

  handle_rpm() {
    if (this.obd_data != undefined) {
      // Calcola l'altezza in percentuale
      this.rpmPercentage = (this.obd_data!.rpm / this.maxRpm) * 100;

      if (this.rpmPercentage > 100) {
        this.rpmPercentage = 100;
      }

      // Cambia colore da verde a rosso
      const red = Math.min(
        255,
        Math.floor((this.obd_data!.rpm / this.maxRpm) * 255)
      );
      const green = Math.max(0, 255 - red);
      this.rpmColor = `rgb(${red}, ${green}, 0)`;
      // console.log(this.rpmColor)
    }
  }

  handle_throttle() {
    if (this.obd_data != undefined) {
      // Calcola l'altezza in percentuale
      this.throttlePercentage =
        (this.obd_data!.acceleratore / this.maxThrottle) * 100;

      if (this.throttlePercentage > 100) {
        this.throttlePercentage = 100;
      }

      // Cambia colore da verde a rosso
      const red = Math.min(
        255,
        Math.floor((this.obd_data!.acceleratore / this.maxThrottle) * 255)
      );
      const green = Math.max(0, 255 - red);
      this.throttleColor = `rgb(${red}, ${green}, 0)`;
      // console.log(this.throttleColor)
      console.log(this.obd_data!.acceleratore);
      console.log(this.throttlePercentage);
    }
  }

  ngOnInit(): void {
    this.motore.getMessage().subscribe((data) => {
      console.log(data);
      this.obd_data = data;
      this.handle_rpm();
      this.handle_throttle();
    });
  }
}

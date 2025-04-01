import { Component, inject, OnInit, PLATFORM_ID } from '@angular/core';
import {
  motore_prestazioni,
  MotorePrestazioniService,
} from 'src/app/Services/OBD_Handler/motore_prestazioni.service';
import { SocketRequestsService } from 'src/app/Services/socketRequests.service';
import { UtilsService } from 'src/app/Services/utils.service';

@Component({
  selector: 'app-cruscotto',
  templateUrl: './cruscotto.component.html',
  styleUrls: ['./cruscotto.component.css'],
  standalone: false,
})
export class CruscottoComponent implements OnInit {
  maxRpm: number = 7200; // RPM massimo
  rpmPercentage: number = 0; // Altezza della barra
  rpmColor: string = 'green'; // Colore iniziale

  minThrottle: number = 0; // Accelletatore minimo
  maxThrottle: number = 100; // Accelletatore massimo
  throttlePercentage: number = 0; // Altezza della barra
  throttleColor: string = 'green'; // Colore iniziale

  speed: number = 0; // Velocità
  rpm: number = 0; // RPM
  throttle: number = 0; // Acceleratore
  setup_throttle_visible: boolean = false;

  //test
  test_mode: boolean = false;
  test_fixed_throttle: number = 0;
  test_fixed_rpm: number = 0;
  test_fixed_speed: number = 0;

  visible_test_page: boolean = false;

  parse_int = parseInt;

  obd_data: motore_prestazioni | undefined;

  data: any;

  // options: any;

  // platformId = inject(PLATFORM_ID);

  // initChart() {
  //   if (isPlatformBrowser(this.platformId)) {
  //     const documentStyle = getComputedStyle(document.documentElement);
  //     const textColor = documentStyle.getPropertyValue('--p-text-color');
  //     const textColorSecondary = documentStyle.getPropertyValue(
  //       '--p-text-muted-color'
  //     );
  //     const surfaceBorder = documentStyle.getPropertyValue(
  //       '--p-content-border-color'
  //     );

  //     this.data = {
  //       labels: [
  //         'January',
  //         'February',
  //         'March',
  //         'April',
  //         'May',
  //         'June',
  //         'July',
  //       ],
  //       datasets: [
  //         {
  //           label: 'First Dataset',
  //           data: [65, 59, 80, 81, 56, 55, 40],
  //           fill: false,
  //           borderColor: documentStyle.getPropertyValue('--p-cyan-500'),
  //           tension: 0.4,
  //         },
  //         {
  //           label: 'Second Dataset',
  //           data: [28, 48, 40, 19, 86, 27, 90],
  //           fill: false,
  //           borderColor: documentStyle.getPropertyValue('--p-gray-500'),
  //           tension: 0.4,
  //         },
  //       ],
  //     };

  //     this.options = {
  //       maintainAspectRatio: false,
  //       aspectRatio: 0.6,
  //       plugins: {
  //         legend: {
  //           labels: {
  //             color: textColor,
  //           },
  //         },
  //       },
  //       scales: {
  //         x: {
  //           ticks: {
  //             color: textColorSecondary,
  //           },
  //           grid: {
  //             color: surfaceBorder,
  //             drawBorder: false,
  //           },
  //         },
  //         y: {
  //           ticks: {
  //             color: textColorSecondary,
  //           },
  //           grid: {
  //             color: surfaceBorder,
  //             drawBorder: false,
  //           },
  //         },
  //       },
  //     };
  //     this.cd.markForCheck();
  //   }
  // }

  constructor(
    private motore: MotorePrestazioniService,
    private socket_requests: SocketRequestsService,
    private utils_service: UtilsService
  ) {}

  ngOnChanges() {}

  //local and public ips
  local_ip: string = '';
  public_ip: string = '';
  get_ips() {
    this.socket_requests.get_local_ip();
    this.utils_service.get_public_ip().then((data) => {
      this.public_ip = data;
    });
  }

  async handle_speed_animation() {
    if (this.obd_data != undefined) {
      while (this.speed != this.obd_data!.velocita) {
        if (this.speed < this.obd_data!.velocita) {
          this.speed++;
        } else {
          this.speed--;
        }
        // await new Promise((r) => setTimeout(r, 2));
      }
    }
  }

  async hanfle_rpm_animation() {
    if (this.obd_data != undefined) {
      while (this.rpm != this.obd_data!.rpm) {
        if (this.rpm < this.obd_data!.rpm) {
          this.rpm++;
        } else {
          this.rpm--;
        }
        // await new Promise((r) => setTimeout(r, 0.1));
      }
    }
  }

  async handle_throttle_animation() {
    if (this.obd_data != undefined) {
      while (this.throttle != this.obd_data!.acceleratore) {
        if (this.throttle < this.obd_data!.acceleratore) {
          this.throttle++;
        } else {
          this.throttle--;
        }
        // await new Promise((r) => setTimeout(r, 5));
      }
    }
  }

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
      this.hanfle_rpm_animation();
    }
  }

  setup_throttle(fase: number, setup_html: number) {
    console.log(this.obd_data!.acceleratore);
    if (fase == 1) {
      if (setup_html != 0) {
        this.minThrottle = setup_html;
      } else {
        this.minThrottle = this.obd_data!.acceleratore;
      }
    }
    if (fase == 2) {
      if (setup_html != 0) {
        this.maxThrottle = setup_html;
      } else {
        this.maxThrottle = this.obd_data!.acceleratore;
      }
      this.setup_throttle_visible = false;
    }
    //log min e max throttle
    console.log(this.minThrottle);
    console.log(this.maxThrottle);
  }

  handle_throttle() {
    if (this.obd_data != undefined) {
      // Calcola l'altezza in percentuale
      // this.throttlePercentage =
      //   (this.obd_data!.acceleratore / this.maxThrottle) * 100;

      // if (this.throttlePercentage > 100) {
      //   this.throttlePercentage = 100;
      // }

      // // Cambia colore da verde a rosso
      // const red = Math.min(
      //   255,
      //   Math.floor((this.obd_data!.acceleratore / this.maxThrottle) * 255)
      // );
      // const green = Math.max(0, 255 - red);
      // this.throttleColor = `rgb(${red}, ${green}, 0)`;
      // this.handle_throttle_animation();
      // console.log(this.throttleColor)
      // console.log(this.obd_data!.acceleratore);
      // console.log(this.throttlePercentage);

      //rebuild using min and max throttle
      this.throttlePercentage =
        ((this.obd_data!.acceleratore - this.minThrottle) /
          (this.maxThrottle - this.minThrottle)) *
        100;
      if (this.throttlePercentage > 100) {
        this.throttlePercentage = 100;
      }
      const red = Math.min(
        255,
        Math.floor(
          ((this.obd_data!.acceleratore - this.minThrottle) /
            (this.maxThrottle - this.minThrottle)) *
            255
        )
      );
      const green = Math.max(0, 255 - red);
      this.throttleColor = `rgb(${red}, ${green}, 0)`;
      this.handle_throttle_animation();
    }
  }

  ngOnInit(): void {
    this.socket_requests.get_local_ip_receiver().subscribe((data) => {
      this.local_ip = data.ip;
    });
    this.get_ips();
    this.motore.getMessage().subscribe((data) => {
      if (!this.test_mode) {
        // console.log(data);
        this.obd_data = data;
        this.handle_rpm();
        this.handle_speed_animation();
        this.handle_throttle();
      }
    });
  }

  handle_test_mode(setup = 0) {
    if (this.test_mode) {
      if (setup == 1) {
        // this.test_fixed_throttle = this.obd_data!.acceleratore;
        // this.test_fixed_rpm = this.obd_data!.rpm;
        // this.test_fixed_speed = this.obd_data!.velocita;
        this.obd_data!.acceleratore = this.test_fixed_throttle;
        this.obd_data!.rpm = this.test_fixed_rpm;
        this.obd_data!.velocita = this.test_fixed_speed;
      }
      // console.log('test_mode');
      // console.log('obd data', this.obd_data);
      this.handle_rpm();
      this.handle_speed_animation();
      this.handle_throttle();
    }
  }
}

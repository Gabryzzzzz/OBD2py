import { Component, inject, OnDestroy, OnInit, PLATFORM_ID, ViewChild } from '@angular/core';
import { AltriDatiService } from 'src/app/Services/OBD_Handler/altri_dati.service';
import { ApexOptions } from 'ng-apexcharts';
import {
  motore_prestazioni,
  MotorePrestazioniService,
} from 'src/app/Services/OBD_Handler/motore_prestazioni.service';
import { RichiesteCanaliService } from 'src/app/Services/OBD_Handler/richieste_canali.service';
import { SocketRequestsService } from 'src/app/Services/socketRequests.service';
import { UtilsService } from 'src/app/Services/utils.service';

import {ApexAxisChartSeries, ApexChart, ApexXAxis, ApexDataLabels, ApexStroke, ApexGrid, ApexFill, ApexLegend} from "ng-apexcharts";

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  stroke: ApexStroke;
  fill: ApexFill;
  legend: ApexLegend;
  // Add other types for better intellisense
  [key: string]: any;
};

export interface cruscotto_configuration {
  throttle_data: {
    min: number;
    max: number;
  };
  unit_flag_benzina: boolean;
}

@Component({
  selector: 'app-cruscotto',
  templateUrl: './cruscotto.component.html',
  styleUrls: ['./cruscotto.component.css'],
  standalone: false,
})
export class CruscottoComponent implements OnInit, OnDestroy {

  public speedThrottleChartOptions: ChartOptions;
  public rpmChartOptions: ChartOptions;
  private chartUpdateInterval: any;
  title: any;

  maxRpm: number = 7200; // RPM massimo
  rpmPercentage: number = 0; // Altezza della barra
  rpmColor: string = 'green'; // Colore iniziale

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

  km_A: number = 0;

  parse_int = parseInt;

  obd_data: motore_prestazioni | undefined;

  configuration: cruscotto_configuration = {
    throttle_data: {
      min: 0,
      max: 100,
    },
    unit_flag_benzina: true,
  };

  constructor(
    private motore: MotorePrestazioniService,
    private altri_dati_service: AltriDatiService,
    private socket_requests: SocketRequestsService,
    private abilita_canali_service: RichiesteCanaliService,
    private utils_service: UtilsService
  ) {
     this.speedThrottleChartOptions = {
      fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.9, stops: [0, 90, 100] } },
      series: [
        { name: "Velocità (km/h)", data: [] },
        { name: "Acceleratore (%)", data: [] }
      ],
      chart: {
        type: "line",
        height: 180,
        animations: { enabled: true, easing: 'linear', dynamicAnimation: { speed: 0 } },
        toolbar: { show: false } // Hide the options menu
      },
      xaxis: { type: "datetime" },
      dataLabels: { enabled: false },
      stroke: { curve: "smooth", width: 2 },
      grid: {
        borderColor: '#e7e7e7'
      },
      legend: { show: false }, // Hide the legend
      tooltip: { enabled: true},
      colors: ["#f44336", "#ff9800", "#4caf50"] //Add this line
    };
    this.rpmChartOptions = {
      series: [ { name: "RPM", data: [] } ],
      chart: {
        type: "area",
        height: 180,
        animations: { enabled: true, easing: 'linear', dynamicAnimation: { speed: 0 } },
        toolbar: { show: false } // Hide the options menu
      },
      xaxis: { type: "datetime" },
      dataLabels: { enabled: false },
      stroke: { curve: "smooth", width: 2 },
      fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.9, stops: [0, 90, 100] } },
      legend: { show: false }, // Hide the legend
      tooltip: { enabled: true},
      colors: ["#f44336", "#ff9800", "#4caf50"] //Add this line
    };
    this.setup_configuration();
  }

  ngOnDestroy(): void {
    this.abilita_canali_service.abilita_canale("motore", false)
    this.abilita_canali_service.abilita_canale("altri_dati", false)
    // Clear the interval when the component is destroyed to prevent memory leaks
    if (this.chartUpdateInterval) {
      clearInterval(this.chartUpdateInterval);
    }
  }

  test_led(data: string){
    this.socket_requests.test_led(data);
  }

  setup_configuration() {
    //if the item is not in local storage, set the default values
    if (!localStorage.getItem('configuration')) {
      localStorage.setItem('configuration', JSON.stringify(this.configuration));
    } else {
      const configuration = localStorage.getItem('configuration');
      if (configuration) {
        const configuration_obj = JSON.parse(
          configuration
        ) as cruscotto_configuration;
        this.configuration = configuration_obj;
      }
    }
  }

  update_configuration() {
    //update the local storage with the new values
    localStorage.setItem('configuration', JSON.stringify(this.configuration));
  }

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

  handle_unit_benzina() {
    this.configuration.unit_flag_benzina = !this.configuration.unit_flag_benzina;
    this.update_configuration();
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
        this.configuration.throttle_data.min = setup_html;
      } else {
        this.configuration.throttle_data.min = this.obd_data!.acceleratore;
      }
    }
    if (fase == 2) {
      if (setup_html != 0) {
        this.configuration.throttle_data.max = setup_html;
      } else {
        this.configuration.throttle_data.max = this.obd_data!.acceleratore;
      }
      this.setup_throttle_visible = false;
    }
    //log min e max throttle
    console.log(this.configuration.throttle_data.min);
    console.log(this.configuration.throttle_data.max);

    //set in local storage bot values in the same object
    this.update_configuration();
  }

  handle_throttle() {
    if (this.obd_data != undefined) {

      this.throttlePercentage =
        ((this.obd_data!.acceleratore - this.configuration.throttle_data.min) /
          (this.configuration.throttle_data.max - this.configuration.throttle_data.min)) *
        100;
      if (this.throttlePercentage > 100) {
        this.throttlePercentage = 100;
      }
      const red = Math.min(
        255,
        Math.floor(
          ((this.obd_data!.acceleratore -  this.configuration.throttle_data.min) /
            ( this.configuration.throttle_data.max -  this.configuration.throttle_data.min)) *
            255
        )
      );
      const green = Math.max(0, 255 - red);
      this.throttleColor = `rgb(${red}, ${green}, 0)`;
      this.handle_throttle_animation();
    }
  }



  ngOnInit(): void {
    // Start fetching chart data periodically
    this.chartUpdateInterval = setInterval(() => {
      this.fetchChartData();
    },  this.DELAY_CHART); // Run every 5 seconds

    this.abilita_canali_service.abilita_canale('motore', true)
    this.abilita_canali_service.abilita_canale('altri_dati', true)
    this.socket_requests.get_local_ip_receiver().subscribe((data) => {
      this.local_ip = data.ip;
    });
    this.get_ips();
    this.altri_dati_service.getMessage().subscribe((res) => {
      this.km_A = res.km_percorsi;
    })

    this.socket_requests.getDataRangeResult().subscribe(data => {
      this.updateChart(data);
    });

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

  /**
   * Fetches the last 5 seconds of engine data from the backend.
   */

  DELAY_CHART = 1000

  private fetchChartData() {
    const now = new Date();
    const fiveSecondsAgo = new Date(now.getTime() - this.DELAY_CHART);

    const endDate = this.formatDateForBackend(now);
    const startDate = this.formatDateForBackend(fiveSecondsAgo);

    this.socket_requests.requestDataByRange('motore_prestazioni', startDate, endDate);
  }

  /**
   * Updates the chart with new data received from the backend.
   * @param data The array of data points.
   */
  private updateChart(data: any[]) {
    const MAX_DATA_POINTS = 60;
    // Get references to the current series data arrays for both charts
    const speedData = this.speedThrottleChartOptions.series[0].data as [number, number][];
    const throttleData = this.speedThrottleChartOptions.series[1].data as [number, number][];
    const rpmData = this.rpmChartOptions.series[0].data as [number, number][];

    data.forEach(item => {
      const timestamp = new Date(item.Timestamp).getTime();
      // Push the new data points into the existing arrays
      speedData.push([timestamp, item.velocita]);
      throttleData.push([timestamp, item.acceleratore]);
      rpmData.push([timestamp, item.rpm]);
    });

    // If the number of data points exceeds the limit, remove the oldest ones.
    if (rpmData.length > MAX_DATA_POINTS) {
      const toRemove = rpmData.length - MAX_DATA_POINTS;
      // The splice() method changes the contents of an array by removing or replacing existing elements.
      speedData.splice(0, toRemove);
      throttleData.splice(0, toRemove);
      rpmData.splice(0, toRemove);
    }

    // To trigger a chart update, we create a new array with the updated data series.
    this.speedThrottleChartOptions.series = [
      { name: "Velocità (km/h)", data: [...speedData] },
      { name: "Acceleratore (%)", data: [...throttleData] }
    ];
    this.rpmChartOptions.series = [
      { name: "RPM", data: [...rpmData] }
    ];
  }

  /**
   * Formats a Date object into the 'YYYY-MM-DD HH:MM:SS' string format required by the backend.
   */
  private formatDateForBackend(date: Date): string {
    const pad = (num: number) => num.toString().padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  }
}

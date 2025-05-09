import { Component, OnInit } from '@angular/core';
import { config_obd, ObdService } from 'src/app/Services/obd.service';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css'],
  standalone: false,
})
export class SettingsComponent implements OnInit {

  config: config_obd | undefined = undefined;

  port_list = [
    "COM0",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "/dev/ttyUSB0",
    "/dev/ttyUSB1",
    "/dev/ttyUSB2",
    "/dev/ttyUSB3"
  ]

  time_config_list = [
    0,
    0.1,
    0.5,
    1,
    2,
    5,
    10
  ]

  try_times_list = [
    1,
    2,
    4,
    6,
    10
  ]

  constructor(private obd_service: ObdService) { }

  ngOnInit() {

    this.obd_service.configuration_subj.subscribe((data) => {
      this.config = JSON.parse(data);
      console.log(this.config);

    });

    this.obd_service.getConfiguration();

  }

  invia_configurazione(){
    this.obd_service.setConfiguration(this.config!);
  }

  //restart_obd
  restart_obd(){
    this.obd_service.restart_obd();
  }

  //stop_obd
  stop_obd(){
    this.obd_service.stop_obd();
  }

}

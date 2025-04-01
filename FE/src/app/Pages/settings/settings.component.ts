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

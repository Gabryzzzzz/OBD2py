import { importProvidersFrom, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './Pages/Home/home/home.component';

import { SocketIoModule, SocketIoConfig, Socket } from 'ngx-socket-io';
import { ObdService } from './Services/obd.service';

import { provideAnimations } from '@angular/platform-browser/animations';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeng/themes/aura';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { ConsumiCarburanteService } from './Services/OBD_Handler/consumi_carburante.service';
import { DiagnosiService } from './Services/OBD_Handler/diagnosi.service';
import { EmissioniService } from './Services/OBD_Handler/emissioni.service';
import { MotorePrestazioniService } from './Services/OBD_Handler/motore_prestazioni.service';
import { TemperatureSensoriService } from './Services/OBD_Handler/temperature_sensori.service';
import { DrawerModule } from 'primeng/drawer';
import { CruscottoComponent } from './Pages/cruscotto/cruscotto.component';
import { DiagnosticaComponent } from './Pages/diagnostica/diagnostica.component';
import { MediaComponent } from './Pages/media/media.component';
import { ProfileComponent } from './Pages/profile/profile.component';
import { SettingsComponent } from './Pages/settings/settings.component';
import { StatisticaComponent } from './Pages/statistica/statistica.component';
import { SocketConnectionService } from './Services/socket.service';
import { AlertService } from './Services/alert.service';
import { Toast } from 'primeng/toast';
import { MessageService } from 'primeng/api';

const primaryConfig: SocketIoConfig = {
  url: 'http://localhost:5000',
  options: { secure: true, transports: ['websocket'] },
};

const secondaryConfig: SocketIoConfig = {
  url: 'http://localhost:5001',
  options: { secure: true, transports: ['websocket'] },
};

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    CruscottoComponent,
    DiagnosticaComponent,
    MediaComponent,
    ProfileComponent,
    SettingsComponent,
    StatisticaComponent,
  ],
  imports: [
    CardModule,
    ButtonModule,
    DrawerModule,
    BrowserModule,
    AppRoutingModule,
    Toast,
    SocketIoModule.forRoot(primaryConfig),
  ],
  providers: [
    provideAnimations(),
    importProvidersFrom(SocketIoModule.forRoot(primaryConfig)),
    ObdService,
    SocketConnectionService,
    ConsumiCarburanteService,
    DiagnosiService,
    EmissioniService,
    MotorePrestazioniService,
    TemperatureSensoriService,
    AlertService,
    MessageService,
    providePrimeNG({
      theme: {
        preset: Aura,
      },
    }),
  ],
  bootstrap: [AppComponent],
})
export class AppModule {

  //on socket connect error print a log
  constructor(private socket: Socket) {
    this.socket.on('connect_error', () => {
      console.log('Connection error');
    });
  }

 }

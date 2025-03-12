import { importProvidersFrom, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './Pages/Home/home/home.component';

import { SocketIoModule, SocketIoConfig } from 'ngx-socket-io';
import { SocketService } from './Services/socket.service';
import { ObdService } from './Services/obd.service';

import { provideAnimations } from '@angular/platform-browser/animations';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeng/themes/aura';
import { CardModule } from 'primeng/card';
import { ConsumiCarburanteService } from './Services/OBD_Handler/consumi_carburante.service';
import { DiagnosiService } from './Services/OBD_Handler/diagnosi.service';
import { EmissioniService } from './Services/OBD_Handler/emissioni.service';
import { MotorePrestazioniService } from './Services/OBD_Handler/motore_prestazioni.service';
import { TemperatureSensoriService } from './Services/OBD_Handler/temperature_sensori.service';

const config: SocketIoConfig = {
  url: 'http://localhost:5000',
  options: { secure: true, transports: ['websocket'] },
};

@NgModule({
  declarations: [AppComponent, HomeComponent],
  imports: [
    CardModule,
    BrowserModule, AppRoutingModule, SocketIoModule.forRoot(config)],
  providers: [
    provideAnimations(),
    importProvidersFrom(SocketIoModule.forRoot(config)),
    SocketService,
    ObdService,
    ConsumiCarburanteService,
    DiagnosiService,
    EmissioniService,
    MotorePrestazioniService,
    TemperatureSensoriService,
    providePrimeNG({
      theme: {
        preset: Aura,
      },
    }),
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}

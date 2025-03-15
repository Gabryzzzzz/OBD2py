import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './Pages/Home/home/home.component';
import { CruscottoComponent } from './Pages/cruscotto/cruscotto.component';
import { DiagnosticaComponent } from './Pages/diagnostica/diagnostica.component';
import { MediaComponent } from './Pages/media/media.component';
import { ProfileComponent } from './Pages/profile/profile.component';
import { SettingsComponent } from './Pages/settings/settings.component';
import { StatisticaComponent } from './Pages/statistica/statistica.component';

const routes: Routes = [
  {
    component: HomeComponent,
    path: ''
  },
  {
    component: CruscottoComponent,
    path: 'cruscotto'
  },
  {
    component: DiagnosticaComponent,
    path: 'diagnostica'
  },
  {
    component: ProfileComponent,
    path: 'profile'
  },
  {
    component: SettingsComponent,
    path: 'impostazioni'
  },
  {
    component: StatisticaComponent,
    path: 'statistica'
  },
  {
    component: MediaComponent,
    path: 'media'
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

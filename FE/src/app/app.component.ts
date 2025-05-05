import { Component, HostListener } from '@angular/core';
import { ChildrenOutletContexts } from '@angular/router';
import { slideInAnimation } from './animations/slideInAnimation';
import { MessageService, ResponsiveOverlayOptions } from 'primeng/api';
import { AlertService, alert_interface } from './Services/alert.service';
import { ResponsiveService } from './Services/responsive.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: false,
  animations: [slideInAnimation],
})
export class AppComponent {
  title = 'OBD2pyFE';

  visible_drawer = false;

  constructor(
    private contexts: ChildrenOutletContexts,
    private messageService: MessageService,
    private alert_service: AlertService,
    private responsive_service: ResponsiveService
  ) {
    alert_service.getMessage().subscribe();
    alert_service.errors_subject.subscribe((data) => {
      this.show_error_alert(data);
      // responsive_service.onResize()
    });
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: { target: { innerWidth: any; }; }) {
    this.responsive_service.setup_platform();
  }

  show_error_alert(data: alert_interface) {
    this.messageService.add({
      severity: data.type,
      summary: data.title,
      detail: data.message,
    });
  }
  getRouteAnimationData() {
    return this.contexts.getContext('primary')?.route?.snapshot?.data?.[
      'animation'
    ];
  }
}

import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  ViewChild,
} from '@angular/core';
import { dati_movimento } from 'src/app/Models/Interfaces/gyroscope.interface';
import { SocketRequestsService } from 'src/app/Services/socketRequests.service';
import { UtilsService } from 'src/app/Services/utils.service';
import * as THREE from 'three';

@Component({
  selector: 'app-cruscotto-model',
  template: `<canvas
    #canvas
    style="width: 100%; height: 100%; display: block;"
  ></canvas>`,
  styleUrl: './cruscotto-model.component.css',
  standalone: false,
})
export class CruscottoModelComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvas', { static: true })
  canvasRef!: ElementRef<HTMLCanvasElement>;

  private renderer!: THREE.WebGLRenderer;
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private cube!: THREE.Mesh;

  accellerazione: { x: string; y: string; z: string } = { x: '', y: '', z: '' };
  giroscopio: { x: string; y: string; z: string } = { x: '', y: '', z: '' };
  dati_movimento: dati_movimento = new dati_movimento();

  private animationId: any;

  constructor(public socket_service: SocketRequestsService) {
    socket_service.get_position().subscribe((x) => {
      console.log('posizione', x);
      this.dati_movimento.set_data(x);
      console.log('dati convertiti', this.dati_movimento);
    });
  }

  ngAfterViewInit() {
    const canvas = this.canvasRef.nativeElement;

    // Setup Three.js
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setSize(canvas.clientWidth, canvas.clientHeight);

    this.scene = new THREE.Scene();

    const aspectRatio = canvas.clientWidth / canvas.clientHeight;
    this.camera = new THREE.PerspectiveCamera(75, aspectRatio, 0.1, 1000);
    this.camera.position.z = 5;

    const geometry = new THREE.BoxGeometry(2, 2, 2);
    const material = new THREE.MeshNormalMaterial();
    this.cube = new THREE.Mesh(geometry, material);
    this.scene.add(this.cube);

    // Inizia ciclo dati simulati
    // setInterval(() => {
    //   this.generateMockIMUData();
    // }, 300);

    // Inizia animazione
    this.animate();
  }

  private rotation = { x: 0, y: 0, z: 0 };

  private gyroscopeThreshold = 0.005; // soglia di sensibilità (tune this)
  private lastTimestamp = performance.now();

  private animate = () => {
    const now = performance.now();
    const deltaTime = (now - this.lastTimestamp) / 1000; // in secondi
    this.lastTimestamp = now;

    this.animationId = requestAnimationFrame(this.animate);

    // Applica soglia (deadzone) al giroscopio
    const gyroX = Math.abs(this.dati_movimento.giroscopio.x) > this.gyroscopeThreshold ? this.dati_movimento.giroscopio.x : 0;
    const gyroY = Math.abs(this.dati_movimento.giroscopio.y) > this.gyroscopeThreshold ? this.dati_movimento.giroscopio.y : 0;
    const gyroZ = Math.abs(this.dati_movimento.giroscopio.z) > this.gyroscopeThreshold ? this.dati_movimento.giroscopio.z : 0;

    // Integra la rotazione nel tempo
    this.rotation.x += -gyroX * deltaTime;
    this.rotation.y += -gyroY * deltaTime;
    this.rotation.z += gyroZ * deltaTime;

    this.cube.rotation.set(this.rotation.x, this.rotation.y, this.rotation.z);

    // Applica traslazioni basate sull'accelerazione (scalo per visibilità)
    // this.cube.position.x = this.dati_movimento.accelerometro.x * 0.5;
    // this.cube.position.y = this.dati_movimento.accelerometro.y * 0.1;
    // this.cube.position.z = this.dati_movimento.accelerometro.z * 0.2;

    this.renderer.render(this.scene, this.camera);
  }

  ngOnDestroy() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    this.renderer.dispose();
  }
}

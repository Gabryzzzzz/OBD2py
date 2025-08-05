import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild } from '@angular/core';
import { SocketRequestsService } from 'src/app/Services/socketRequests.service';
import { UtilsService } from 'src/app/Services/utils.service';
import * as THREE from 'three';

@Component({
  selector: 'app-cruscotto-model',
  template: `<canvas #canvas style="width: 100%; height: 100%; display: block;"></canvas>`,
  styleUrl: './cruscotto-model.component.css',
   standalone: false,
})
export class CruscottoModelComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvas', { static: true }) canvasRef!: ElementRef<HTMLCanvasElement>;

  private renderer!: THREE.WebGLRenderer;
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private cube!: THREE.Mesh;

  accellerazione: {x: string, y: string, z: string} = {x: "", y: "", z: ""}
  giroscopio: {x: string, y: string, z: string} = {x: "", y: "", z: ""}

  private animationId: any;

  constructor(public socket_service: SocketRequestsService){
    socket_service.get_position().subscribe(x => {
      console.log("posizione", x);

    })
  }

  // Variabili dati simulati (mock)
  private acceleration = { x: 0, y: 0, z: 0 };
  private gyroscope = { x: 0, y: 0, z: 0 };

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
    setInterval(() => {
      this.generateMockIMUData();
    }, 300);

    // Inizia animazione
    this.animate();
  }

  private animate = () => {
    this.animationId = requestAnimationFrame(this.animate);

    // Applica rotazioni basate sul giroscopio
    // Nota: i valori sono in radianti, moltiplico per fattore per visibilità
    this.cube.rotation.x = this.gyroscope.x * 5;
    this.cube.rotation.y = this.gyroscope.y * 5;
    this.cube.rotation.z = this.gyroscope.z * 5;

    // Applica traslazioni basate sull'accelerazione (scalo per visibilità)
    this.cube.position.x = this.acceleration.x * 0.5;
    this.cube.position.y = this.acceleration.y * 0.5;
    this.cube.position.z = this.acceleration.z * 0.2;

    this.renderer.render(this.scene, this.camera);
  };

  // Genera dati simulati random come prima
  private generateMockIMUData() {
    this.acceleration = {
      x: (Math.random() - 0.5) * 2,     // da -1 a 1
      y: (Math.random() - 0.5) * 2,     // da -1 a 1
      z: 9.8 + (Math.random() - 0.5)    // gravità +/- 0.5
    };
    this.gyroscope = {
      x: (Math.random() - 0.5) * 0.1,   // da -0.05 a 0.05 rad
      y: (Math.random() - 0.5) * 0.1,
      z: (Math.random() - 0.5) * 0.1
    };
  }

  ngOnDestroy() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    this.renderer.dispose();
  }
}

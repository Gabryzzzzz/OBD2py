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

  // Store the filtered orientation from the backend
  private orientation = { pitch: 0, roll: 0 };

  private animationId: any;

  constructor(public socket_service: SocketRequestsService) {
    // Subscribe to the new 'orientation' event
    this.socket_service.get_position().subscribe((data) => {
      // Directly store the stable pitch and roll values
      this.orientation.pitch = data.pitch;
      this.orientation.roll = data.roll;
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

    // Inizia animazione
    this.animate();
  }

  private animate = () => {
    this.animationId = requestAnimationFrame(this.animate);

    // Convert degrees from backend to radians for Three.js
    const pitchInRadians = THREE.MathUtils.degToRad(this.orientation.pitch);
    const rollInRadians = THREE.MathUtils.degToRad(this.orientation.roll);

    // Directly set the cube's rotation using the stable data from the backend.
    // The axes might need to be swapped or inverted depending on sensor orientation.
    // A common mapping is: pitch -> rotation.x, roll -> rotation.y
    this.cube.rotation.set(pitchInRadians, rollInRadians, 0);

    this.renderer.render(this.scene, this.camera);
  }

  ngOnDestroy() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    this.renderer.dispose();
  }
}

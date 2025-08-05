export class dati_movimento {
  accelerometro: accelerometro = {
    x: 0,
    y: 0,
    z: 0
  }

  giroscopio: giroscopio = {
    x: 0,
    y: 0,
    z: 0
  }

  temperatura: number = 0

  set_data(raw_data: any){
    this.accelerometro = {
      x: +raw_data[0][0],
      y: +raw_data[0][1],
      z: +raw_data[0][2]
    }
    this.giroscopio= {
      x: +raw_data[1][0],
      y: +raw_data[1][1],
      z: +raw_data[1][2]
    }
    this.temperatura = +raw_data[2]
  }

}

export interface accelerometro {
  x: number
  y: number
  z: number
}

export interface giroscopio {
  x: number
  y: number
  z: number
}

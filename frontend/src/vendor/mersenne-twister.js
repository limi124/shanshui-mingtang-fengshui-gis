// Browser ESM shim for Cesium's random-number dependency during Vite dev.
// The MVP only needs CesiumMath.nextRandomNumber(), so a compact seeded PRNG is enough.
export default class MersenneTwister {
  constructor(seed = Date.now()) {
    this.seed = Number(seed) >>> 0;
  }

  random() {
    this.seed = (1664525 * this.seed + 1013904223) >>> 0;
    return this.seed / 4294967296;
  }
}

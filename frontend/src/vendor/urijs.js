// Minimal URI shim for Cesium dependencies in Vite dev.
// It implements the subset used by Cesium Core during MVP initialization.
export default class Uri {
  constructor(value = "") {
    this.original = String(value);
    this.isRelative = !/^[a-z][a-z0-9+.-]*:/i.test(this.original);
    const base = typeof window !== "undefined" ? window.location.href : "http://localhost/";
    this.url = new URL(this.original || base, base);
  }

  query() {
    return this.url.search.replace(/^\?/, "");
  }

  search(value) {
    if (value === undefined) return this.url.search;
    this.url.search = value;
    return this;
  }

  fragment(value) {
    if (value === undefined) return this.url.hash.replace(/^#/, "");
    this.url.hash = value;
    return this;
  }

  scheme() {
    return this.isRelative ? "" : this.url.protocol.replace(/:$/, "");
  }

  authority(value) {
    if (value === undefined) return this.url.host;
    this.url.host = value;
    this.isRelative = false;
    return this;
  }

  path() {
    return this.url.pathname;
  }

  normalize() {
    return this;
  }

  absoluteTo(base) {
    return new Uri(new URL(this.toString(), String(base)).toString());
  }

  toString() {
    if (!this.isRelative) return this.url.toString();
    return `${this.url.pathname}${this.url.search}${this.url.hash}`;
  }
}

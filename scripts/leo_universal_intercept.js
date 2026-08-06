/**
 * LEO UNIVERSAL WEBGL OCCLUSION CULL v3.0 (The Photosynthesis Protocol)
 * Intercepts WebGL drawing buffer allocation and Prototype setters at engine level.
 * Force-locks drawing workload to 640x360 while stretching CSS to 100vw/100vh.
 * Bypasses iGPU memory & FP32 raymarching bottlenecks without altering shader source.
 */

(function () {
  console.log("🌌 [LEO] Initializing Universal WebGL Intercept Protocol...");

  const TARGET_W = 640;
  const TARGET_H = 360;

  // 1. Hijack HTMLCanvasElement Property Setters
  ["width", "height"].forEach((prop) => {
    const original = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, prop);
    if (original) {
      Object.defineProperty(HTMLCanvasElement.prototype, prop, {
        get: function () {
          return prop === "width" ? TARGET_W : TARGET_H;
        },
        set: function (val) {
          original.set.call(this, prop === "width" ? TARGET_W : TARGET_H);
        },
        configurable: true,
      });
    }
  });

  // 2. Hijack setAttribute (Defeats canvas.setAttribute('width', ...))
  const originalSetAttribute = HTMLCanvasElement.prototype.setAttribute;
  HTMLCanvasElement.prototype.setAttribute = function (name, value) {
    if (name && name.toLowerCase() === "width")
      return originalSetAttribute.call(this, name, TARGET_W);
    if (name && name.toLowerCase() === "height")
      return originalSetAttribute.call(this, name, TARGET_H);
    return originalSetAttribute.call(this, name, value);
  };

  // 3. Hijack getContext to spoof drawingBufferWidth/Height
  const originalGetContext = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (type, attributes) {
    const context = originalGetContext.call(this, type, attributes);
    if (context && (type.includes("webgl") || type.includes("experimental"))) {
      try {
        Object.defineProperty(context, "drawingBufferWidth", {
          get: () => TARGET_W,
          configurable: true,
        });
        Object.defineProperty(context, "drawingBufferHeight", {
          get: () => TARGET_H,
          configurable: true,
        });
      } catch (e) {}
    }
    return context;
  };

  // 4. Intercept WebGL Viewport
  const originalViewport = WebGLRenderingContext.prototype.viewport;
  WebGLRenderingContext.prototype.viewport = function (x, y, width, height) {
    return originalViewport.call(this, x, y, TARGET_W, TARGET_H);
  };

  if (window.WebGL2RenderingContext) {
    const originalViewport2 = WebGL2RenderingContext.prototype.viewport;
    WebGL2RenderingContext.prototype.viewport = function (x, y, width, height) {
      return originalViewport2.call(this, x, y, TARGET_W, TARGET_H);
    };
  }

  // 5. Force CSS to stretch micro-buffer to fullscreen smoothly
  const style = document.createElement("style");
  style.innerHTML =
    "canvas { width: 100vw !important; height: 100vh !important; image-rendering: auto !important; }";
  document.head.appendChild(style);

  console.log(
    "⚡ [LEO] UNIVERSAL INTERCEPT ACTIVE. Workload locked to 640x360 (89% workload reduction). Target: 60+ FPS.",
  );
})();

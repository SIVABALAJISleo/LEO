import { LazyExecutor } from "../optimization/LazyExecutor";

export class MediaProxy {
  private static instance: MediaProxy;
  private lazyExecutor: LazyExecutor;

  private constructor() {
    this.lazyExecutor = LazyExecutor.getInstance();
  }

  static getInstance(): MediaProxy {
    if (!MediaProxy.instance) {
      MediaProxy.instance = new MediaProxy();
    }
    return MediaProxy.instance;
  }

  // Get a low-res placeholder immediately while queuing high-res fetch
  getOptimizedMedia(
    url: string,
    type: "image" | "video",
  ): { placeholder: string; fullPromise: Promise<string> } {
    // Return a lightweight placeholder (mocked logic)
    const placeholder =
      type === "image"
        ? `${url}?w=64&q=10` // Simulated params
        : `${url}/preview.gif`;

    // Queue the heavy fetch
    const fullPromise = this.lazyExecutor.defer(async () => {
      // Mock heavy operation: fetching high-res
      await new Promise((r) => setTimeout(r, 500));
      return `${url}?hd=true`;
    }, 0); // Low priority

    return { placeholder, fullPromise };
  }

  async upscaleImage(url: string, scale: number = 2): Promise<string> {
    // Mock upscaling logic
    console.log(`[MediaProxy] Upscaling ${url} by ${scale}x...`);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(url.replace(".jpg", "_upscaled.png"));
      }, 1500);
    });
  }
}

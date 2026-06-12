// LEO AI V36 — Weather Adaptation Layer
// Adjusts optical sensor gain thresholds based on rain, fog, and dust.

export class WeatherAdaptationLayer {
  public computeGainMultiplier(weatherCondition: "clear" | "rain" | "fog" | "dust"): number {
    switch (weatherCondition) {
      case "clear": return 1.0;
      case "rain": return 1.45;
      case "fog": return 1.8;
      case "dust": return 1.6;
      default: return 1.0;
    }
  }
}

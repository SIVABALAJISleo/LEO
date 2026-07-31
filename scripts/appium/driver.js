const { remote } = require('webdriverio');
const config = require('./appium.config');
const fs = require('fs');
const path = require('path');

class DriverManager {
  constructor() {
    this.driver = null;
  }

  async initDriver() {
    if (!this.driver) {
      this.driver = await remote(config);
    }
    return this.driver;
  }

  async takeScreenshot(name) {
    if (!this.driver) return;
    const dir = path.resolve(config.screenshotsDir);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const filePath = path.join(dir, `${name}_${Date.now()}.png`);
    await this.driver.saveScreenshot(filePath);
    console.log(`[Appium] Screenshot saved: ${filePath}`);
  }

  async quitDriver() {
    if (this.driver) {
      await this.driver.deleteSession();
      this.driver = null;
    }
  }
}

module.exports = new DriverManager();

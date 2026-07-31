// Appium Automation Configuration
module.exports = {
  hostname: process.env.APPIUM_HOST || "localhost",
  port: parseInt(process.env.APPIUM_PORT || "4723", 10),
  path: "/",
  capabilities: {
    platformName: "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "Android Emulator",
    "appium:browserName": "Chrome",
    "appium:newCommandTimeout": 300,
    "appium:autoGrantPermissions": true,
  },
  testTimeout: 60000,
  screenshotsDir: "./reports/appium/screenshots",
  videosDir: "./reports/appium/videos",
};

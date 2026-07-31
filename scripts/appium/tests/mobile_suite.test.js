const driverManager = require('../driver');
const MobileAppPage = require('../pom/MobileAppPage');

describe('Appium Mobile E2E Suite', () => {
  let driver;
  let page;
  const baseUrl = process.env.BASE_URL || 'http://localhost:5173';

  beforeAll(async () => {
    driver = await driverManager.initDriver();
    page = new MobileAppPage(driver);
  });

  afterAll(async () => {
    await driverManager.quitDriver();
  });

  test('Mobile Registration & Login Flow', async () => {
    await page.navigateTo(`${baseUrl}/login`);
    await driverManager.takeScreenshot('mobile_login_page');
    await page.login('test@leo.ai', 'password123');
    await driverManager.takeScreenshot('mobile_after_login');
  });

  test('Mobile AI Chat Interaction', async () => {
    await page.navigateTo(`${baseUrl}/app/chat`);
    await page.sendChatMessage('Hello LEO Mobile Test');
    await driverManager.takeScreenshot('mobile_chat_sent');
  });

  test('Mobile Viewport Orientation & Offline Simulation', async () => {
    await driver.setOrientation('LANDSCAPE');
    await driverManager.takeScreenshot('mobile_landscape');
    await driver.setOrientation('PORTRAIT');
    await driverManager.takeScreenshot('mobile_portrait');
  });
});

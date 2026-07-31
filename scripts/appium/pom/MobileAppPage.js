class MobileAppPage {
  constructor(driver) {
    this.driver = driver;
  }

  // Selectors
  get emailInput() { return this.driver.$('input[name="email"], input[type="email"]'); }
  get passwordInput() { return this.driver.$('input[name="password"], input[type="password"]'); }
  get loginButton() { return this.driver.$('button[type="submit"], button:has-text("Sign in")'); }
  get chatInput() { return this.driver.$('textarea, input[placeholder*="Ask"]'); }
  get sendButton() { return this.driver.$('button[aria-label*="Send"], button:has-text("Send")'); }
  get drawerToggle() { return this.driver.$('button[aria-label*="menu"], button[aria-label*="Sidebar"]'); }

  async navigateTo(baseUrl) {
    await this.driver.url(baseUrl);
  }

  async login(email, password) {
    await this.emailInput.setValue(email);
    await this.passwordInput.setValue(password);
    await this.loginButton.click();
  }

  async sendChatMessage(message) {
    await this.chatInput.setValue(message);
    await this.sendButton.click();
  }

  async toggleDrawer() {
    if (await this.drawerToggle.isDisplayed()) {
      await this.drawerToggle.click();
    }
  }
}

module.exports = MobileAppPage;

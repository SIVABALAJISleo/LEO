import { Page, Locator, expect } from "@playwright/test";

export class ChatPage {
  readonly page: Page;
  readonly chatTextArea: Locator;
  readonly sendButton: Locator;
  readonly sidebarToggle: Locator;

  constructor(page: Page) {
    this.page = page;
    this.chatTextArea = page.locator('textarea, input[placeholder*="Ask"]');
    this.sendButton = page
      .getByRole("button", { name: /send/i })
      .or(page.locator('button[aria-label*="Send"]'));
    this.sidebarToggle = page.getByRole("button", { name: /toggle sidebar|menu/i });
  }

  async goto() {
    await this.page.goto("/app/chat");
  }

  async sendMessage(text: string) {
    await this.chatTextArea.fill(text);
    await this.sendButton.click();
  }
}

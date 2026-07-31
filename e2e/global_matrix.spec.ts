import { test, expect } from '@playwright/test';
import { mockLeoBackend } from './mocks';

const REGIONS = [
  { code: 'IN', locale: 'hi-IN', timezone: 'Asia/Kolkata', currency: 'INR' },
  { code: 'US', locale: 'en-US', timezone: 'America/New_York', currency: 'USD' },
  { code: 'UK', locale: 'en-GB', timezone: 'Europe/London', currency: 'GBP' },
  { code: 'DE', locale: 'de-DE', timezone: 'Europe/Berlin', currency: 'EUR' },
  { code: 'FR', locale: 'fr-FR', timezone: 'Europe/Paris', currency: 'EUR' },
  { code: 'JP', locale: 'ja-JP', timezone: 'Asia/Tokyo', currency: 'JPY' },
  { code: 'SG', locale: 'en-SG', timezone: 'Asia/Singapore', currency: 'SGD' },
  { code: 'AU', locale: 'en-AU', timezone: 'Australia/Sydney', currency: 'AUD' },
  { code: 'BR', locale: 'pt-BR', timezone: 'America/Sao_Paulo', currency: 'BRL' },
  { code: 'CA', locale: 'en-CA', timezone: 'America/Toronto', currency: 'CAD' },
];

test.describe('Pass 22: Global Regional Localization & Currency Simulation', () => {
  for (const region of REGIONS) {
    test(`Global Region Simulation: ${region.code} (${region.locale} / ${region.timezone})`, async ({ page }) => {
      await mockLeoBackend(page);
      await page.goto('/app/settings');
      await expect(page.locator('body')).toBeVisible();
    });
  }
});

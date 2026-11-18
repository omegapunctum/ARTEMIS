const assert = require('node:assert/strict');
const {chromium} = require('playwright');

async function main() {
  const browser = await chromium.launch({args:['--disable-webgl']});
  try {
    for (const viewport of [{width:1440,height:900},{width:390,height:844}]) {
      const page = await browser.newPage({viewport});
      await page.goto('http://127.0.0.1:8182/globe/?lang=ru');
      await page.getByText('Карта недоступна. Записи доступны через поиск.').waitFor();
      await page.goto('http://127.0.0.1:8182/globe/?lang=ru&item=catalog:wikidata:Q83125&start=1894&end=1894');
      await page.locator('#selection-title').waitFor();
      assert(await page.locator('#view-map').isDisabled());
      assert(await page.locator('#focus-selection').isHidden());
      await page.locator('#sources-disclosure > summary').click();
      const citation = page.locator('#historical-citations a').first();
      assert(await citation.isVisible());
      assert.match(await citation.getAttribute('href'),/^https?:/);
      await page.locator('#close-details').click();
      if (viewport.width < 640) await page.locator('#mobile-records').click();
      const search = page.locator('#record-search');
      await search.fill('Q83125');
      await page.locator('#record-select').selectOption('catalog:wikidata:Q83125');
      await page.locator('#selection-title').waitFor();
      assert(await page.locator('#fatal-error').isHidden());
      await page.close();
    }
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });

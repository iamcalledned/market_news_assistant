const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

puppeteer.use(StealthPlugin());

const url = process.argv[2];
if (!url) {
    console.error("Usage: node wsj_scraper.js <URL>");
    process.exit(1);
}

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    try {
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

        // Optionally screenshot/debug
        // await page.screenshot({ path: 'page.png' });

        const text = await page.evaluate(() => {
            const container = document.querySelector('article') || document.querySelector('main') || document.body;
            return container.innerText;
        });

        console.log(text.slice(0, 1500));  // Preview for now
    } catch (err) {
        console.error("❌ Error:", err.message);
    }

    await browser.close();
})();

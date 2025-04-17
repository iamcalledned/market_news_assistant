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
        console.log(`[WSJ Stealth] Navigating to: ${url}`);
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

        const html = await page.content();
        const result = await page.evaluate(() => {
            const selectors = [
                'article',
                'main',
                'div[class*="content"]',
                'body'
            ];
            for (let sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.innerText.length > 100) {
                    return el.innerText;
                }
            }
            return null;
        });

        if (result) {
            console.log("🧾 Preview:\n");
            console.log(result.slice(0, 1500));
        } else {
            console.error("❌ Could not extract any content from page.");
        }

    } catch (err) {
        console.error("💥 Error:", err.message);
    } finally {
        await browser.close();
    }
})();

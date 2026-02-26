const puppeteer = require('puppeteer');
(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto('http://localhost:8000', {waitUntil: 'networkidle2'});

    await page.screenshot({ path: '/Users/petersmith/.gemini/antigravity/brain/65e45563-4e77-43f2-8b6f-312087d621d7/dashboard_list_view.png' });

    await page.waitForSelector('#btn-map');
    await page.click('#btn-map');
    await new Promise(r => setTimeout(r, 2000)); // wait for leafy fade
    await page.screenshot({ path: '/Users/petersmith/.gemini/antigravity/brain/65e45563-4e77-43f2-8b6f-312087d621d7/dashboard_map_view.png' });
    
    await browser.close();
})();

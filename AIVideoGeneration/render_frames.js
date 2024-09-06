const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function renderFrames(htmlFile, outputDir, duration, fps, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    let browser;
    try {
      browser = await puppeteer.launch({
        headless: "new",
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
      });
      const page = await browser.newPage();
      
      await page.setViewport({ width: 1080, height: 1920 });
      await page.goto(`file:${path.resolve(htmlFile)}`, { waitUntil: 'networkidle0' });

      const totalFrames = Math.ceil(duration * fps);

      console.log('Rendering Frames');
      for (let i = 0; i < totalFrames; i++) {
        const time = i / fps;
        await page.evaluate((t) => update(t), time);
        
        const outputPath = path.join(outputDir, `frame_${i.toString().padStart(5, '0')}.png`);
        try {
          await page.screenshot({ path: outputPath, type: 'png' });
        } catch (screenshotError) {
          if (screenshotError.message.includes('Protocol error (Page.captureScreenshot): Unable to capture screenshot')) {
            console.error(`Error capturing screenshot for frame ${i}. Retrying...`);
            throw screenshotError; // Throw the error to trigger a retry
          } else {
            console.error(`Error capturing screenshot for frame ${i}:`, screenshotError);
            continue; // Skip this frame and continue with the next one
          }
        }
      }

      console.log('Rendering complete');
      return; // Successfully completed, exit the function
    } catch (error) {
      console.error(`Attempt ${attempt + 1} failed:`, error);
      if (attempt < maxRetries - 1) {
        console.log('Pausing for 30 seconds before retrying...');
        await delay(30000); // 30 seconds delay
      } else {
        console.error('Max retries reached. Rendering failed.');
        throw error; // Re-throw the error after all retries have failed
      }
    } finally {
      if (browser) {
        await browser.close();
      }
    }
  }
}

const [htmlFile, outputDir, duration, fps] = process.argv.slice(2);

renderFrames(htmlFile, outputDir, parseFloat(duration), parseInt(fps))
  .then(() => console.log('Rendering process finished'))
  .catch(console.error);
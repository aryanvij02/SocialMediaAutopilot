import { upload } from 'youtube-videos-uploader' //Typescript
import { createWebflowItem } from './webflow.mjs';
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

// Get the current file's path
const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// Get the video details from command line arguments
const videoDetailsJson = process.argv[2];

if (!videoDetailsJson) {
    console.error('Please provide video details as a JSON string argument');
    process.exit(1);
}

let videoDetails;
try {
    videoDetails = JSON.parse(videoDetailsJson);
} catch (error) {
    console.error('Failed to parse video details JSON:', error);
    process.exit(1);
}

const { path, title, description, email, pass, product } = videoDetails;

if (!path || !title || !description || !email || !pass || !product) {
    console.error('Missing required video details');
    process.exit(1);
}

const credentials = { email, pass, recoveryemail: '' }

const video1 = { path, title, description, product }

const onVideoUploadSuccess = async (videoUrl) => {
    // console.log("Video got uploaded:", videoUrl);
    console.log(JSON.stringify({ status: 'success', videoUrl: videoUrl[0] }));


    try {
        const cleanedDescription = description.replace(/^Link:\s*https?:\/\/\S+\s*/, '');
        // Create a new item in Webflow
        const itemId = await createWebflowItem(path.split('/').pop(), title, cleanedDescription, videoUrl[0]);
        if (itemId) {
            // console.log(`Successfully created Webflow item with ID: ${itemId}`);
            console.log(JSON.stringify({ status: 'webflow_success', itemId: itemId }));
        } else {
            console.error(JSON.stringify({ status: 'webflow_error', message: 'Failed to create Webflow item' }));
        }
    } catch (error) {
        console.error(JSON.stringify({ status: 'webflow_error', message: error.toString() }));
    }
};

const puppeteerLaunchOptions = {
    headless: " new",
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    ignoreHTTPSErrors: true,
    defaultViewport: null,
    timeout: 120000  // Increase timeout to 60 seconds
};

// const attemptUpload = async (retryCount = 0) => {
//     try {
//         console.log("trying upload on ", credentials['email'])
//         const result = await upload(credentials, [video1], puppeteerLaunchOptions);
//         await onVideoUploadSuccess(result);
//         process.exit(0)
//     } catch (error) {
//         console.error(`Upload attempt ${retryCount + 1} failed:`, error);
//         if (retryCount < 3) {  // Retry once
//             console.log("Retrying upload...");
//             await attemptUpload(retryCount + 1);
//         } 
//         else {
//             try {
//                 const credentials1 = { email: "myaifrontdesk4@gmail.com", pass: "myaifrontdesk101$", recoveryemail: '', "urn": "C4NTCvIScX" , "access_token": "AQQZ1SzuI5E7IP8zsWe2jGQHXwbirqTRWXuJCPKgLnGxSsPBMgBZEPXTbHft_u8g3BBXg5TK4zRkFOVYiugfPT3seOPMP0TNKCMpLthlByfhkxvLne8PveV76vhkJaPCnICSoXD0KTUEHJbQjY_W58-ws_Oapu24ev27xvRVRiijUKiJRzRuN8QzU65LpCBw3_j1l8p8_zCPpLv-o80" }
//                 console.log("trying upload on ", credentials1['email'])
//                 const result = await upload(credentials1, [video1], puppeteerLaunchOptions);
//                 await onVideoUploadSuccess(result);
//                 console.log("Upload successful on retry");
//                 process.exit(0)
//             } 
//             catch {
//                 console.error("Upload failed after retry:");
//                 process.exit(1)
//             }
//         }
//     }
// };

const attemptUpload = async (retryCount = 0) => {
    try {
        console.log(JSON.stringify({ status: 'uploading', account: credentials['email'] }));
        const result = await upload(credentials, [video1], puppeteerLaunchOptions);
        await onVideoUploadSuccess(result);
        process.exit(0);
    } catch (error) {
        console.error(JSON.stringify({ status: 'upload_error', message: error.toString(), retryCount: retryCount }));
        if (retryCount < 3) {
            console.log(JSON.stringify({ status: 'retrying', retryCount: retryCount + 1 }));
            await attemptUpload(retryCount + 1);
        } else {
            try {
                const credentials1 = { email: "myaifrontdesk4@gmail.com", pass: "myaifrontdesk101$", recoveryemail: '', "urn": "C4NTCvIScX" , "access_token": "AQQZ1SzuI5E7IP8zsWe2jGQHXwbirqTRWXuJCPKgLnGxSsPBMgBZEPXTbHft_u8g3BBXg5TK4zRkFOVYiugfPT3seOPMP0TNKCMpLthlByfhkxvLne8PveV76vhkJaPCnICSoXD0KTUEHJbQjY_W58-ws_Oapu24ev27xvRVRiijUKiJRzRuN8QzU65LpCBw3_j1l8p8_zCPpLv-o80" }
                console.log(JSON.stringify({ status: 'uploading', account: credentials1['email'] }));
                const result = await upload(credentials1, [video1], puppeteerLaunchOptions);
                await onVideoUploadSuccess(result);
                process.exit(0);
            } catch (error) {
                console.error(JSON.stringify({ status: 'final_error', message: error.toString() }));
                process.exit(1);
            }
        }
    }
};

attemptUpload()




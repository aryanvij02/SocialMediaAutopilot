const axios = require('axios');

const ACCESS_TOKEN = 'EAAOf4EWdgTsBO9Q2fNZAWdgZA3HBZAc8ZAZAuiukbPdw2Fic6eZCYnPZCbyi5V5Rc59tGijlsWZBgg1GDZBYPj4eKELvN4vUWPYd0wNC2Dtqjn3st8H427yzjr6ZBtDVuHlEZCgWEbbtuJhTrPiJcrSJLSu1VlXJBHQlru2xDW5sziLghah2SsnJkfZAWcK7gZCzAHdPJvLTn2eZAF34JnSurr1s4BlJUxp8PERZBtq';
const GRAPH_API_BASE_URL = 'https://graph.facebook.com/v18.0/';

function buildGraphAPIURL(path, params) {
    const url = new URL(path, GRAPH_API_BASE_URL);
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
            url.searchParams.append(key, value);
        }
    });
    url.searchParams.append('access_token', ACCESS_TOKEN);
    return url.toString();
}

async function uploadReel(accountId, videoUrl, caption, coverUrl, thumbOffset, locationId) {
    const uploadVideoUri = buildGraphAPIURL(`${accountId}/media`, {
        media_type: 'REELS',
        video_url: videoUrl,
        caption,
        cover_url: coverUrl,
        thumb_offset: thumbOffset,
        location_id: locationId,
    });

    try {
        const response = await axios.post(uploadVideoUri);
        return response.data.id; // This is the container ID
    } catch (error) {
        console.error('Error uploading reel:', error.response ? error.response.data : error.message);
        throw error;
    }
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function publishReel(accountId, containerId, maxRetries = 10, retryDelay = 5000) {
    const publishVideoUri = buildGraphAPIURL(`${accountId}/media_publish`, {
        creation_id: containerId,
    });

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const response = await axios.post(publishVideoUri);
            return response.data.id; // This is the published media ID
        } catch (error) {
            if (error.response && error.response.data.error.code === 9007) {
                console.log(`Attempt ${attempt + 1}: Media not ready. Retrying in ${retryDelay / 1000} seconds...`);
                await delay(retryDelay);
            } else {
                console.error('Error publishing reel:', error.response ? error.response.data : error.message);
                throw error;
            }
        }
    }
    throw new Error('Failed to publish reel after maximum retries');
}

async function checkUploadStatus(containerId, maxRetries = 30, retryDelay = 3000) {
    const checkStatusUri = buildGraphAPIURL(`${containerId}`, { fields: 'status_code' });

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const response = await axios.get(checkStatusUri);
            if (response.data.status_code === "FINISHED") {
                return true;
            }
            console.log(`Upload not ready. Checking again in ${retryDelay / 1000} seconds...`);
            await delay(retryDelay);
        } catch (error) {
            console.error('Error checking upload status:', error.response ? error.response.data : error.message);
            await delay(retryDelay);
        }
    }
    return false;
}

async function main() {
    const accountId = '17841468378531043'; // Replace with your Instagram account ID
    const videoUrl = 'https://static.videezy.com/system/resources/previews/000/032/359/original/MM008645___BOUNCING_FRUIT_009___1080p___phantom.mp4';
    const caption = 'New account?!!';
    const coverUrl = '';
    const thumbOffset = 0; // 5 seconds

    try {
        console.log('Uploading reel...');
        const containerId = await uploadReel(accountId, videoUrl, caption, coverUrl, thumbOffset);
        console.log('Reel uploaded successfully. Container ID:', containerId);

        console.log('Checking upload status...');
        const isUploaded = await checkUploadStatus(containerId);
        if (!isUploaded) {
            throw new Error('Upload did not complete successfully');
        }

        console.log('Publishing reel...');
        const publishedMediaId = await publishReel(accountId, containerId);
        console.log('Reel published successfully. Media ID:', publishedMediaId);
    } catch (error) {
        console.error('Failed to upload or publish reel:', error);
    }
}

main();
import fetch from 'node-fetch';
import slugify from 'slugify';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { URL } from 'url';



const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config({ path: `${__dirname}/.env` });

// API Configuration
const WEBFLOW_SITE_ID = process.env.WEBFLOW_SITE_ID
const WEBFLOW_API_KEY = process.env.WEBFLOW_API_KEY
const WEBFLOW_COLLECTION_ID = process.env.WEBFLOW_COLLECTION_ID
const WEBFLOW_BASE_URL = 'https://api.webflow.com/v2';


function convertYoutubeLink(url) {
  try {
    const parsedUrl = new URL(url);
    
    // Check if it's a YouTube URL
    if (parsedUrl.hostname === 'youtube.com' || parsedUrl.hostname === 'www.youtube.com') {
      // Check if it's a Shorts link
      if (parsedUrl.pathname.startsWith('/shorts/')) {
        const videoId = parsedUrl.pathname.split('/')[2];
        return `https://www.youtube.com/watch?v=${videoId}`;
      }
    }
    
    // If it's not a YouTube Shorts link, return the original URL
    return url;
  } catch (error) {
    console.error('Error parsing URL:', error);
    return url;
  }
}

function getWebflowHeaders() {
  return {
    'accept': 'applicataion/json',
    'content-type': 'application/json',
    'authorization': `Bearer ${WEBFLOW_API_KEY}`
  };
}

async function makeApiRequest(url, method = 'GET', headers = {}, body = null) {
  try {
    console.log(`Making ${method} request to ${url}`);
    console.log('Headers:', JSON.stringify(headers, null, 2));
    if (body) {
      console.log('Request body:', JSON.stringify(body, null, 2));
    }

    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null
    });

    const responseText = await response.text();
    console.log('Response status:', response.status);
    console.log('Response headers:', JSON.stringify(response.headers.raw(), null, 2));
    console.log('Response body:', responseText);

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}\nResponse: ${responseText}`);
    }

    return JSON.parse(responseText);
  } catch (error) {
    console.error(`API request failed: ${error.message}`);
    throw error;
  }
}

async function testWebflowConnection() {
  const url = `${WEBFLOW_BASE_URL}/collections/${WEBFLOW_COLLECTION_ID}`;
  console.log("Testing Webflow API connection...");
  try {
    const result = await makeApiRequest(url, 'GET', getWebflowHeaders());
    console.log("Successfully connected to Webflow API and fetched collection details.");
    console.log(`Collection Name: ${result.name || 'N/A'}`);
    console.log('Collection details:', JSON.stringify(result, null, 2));
  } catch (error) {
    console.error("Failed to connect to Webflow API or fetch collection details.");
    console.error(error);
  }
}

export async function createWebflowItem(name, title, description, vidLink) {
  await testWebflowConnection();
  const headers = getWebflowHeaders();
  const videoLink = convertYoutubeLink(vidLink)

  // Convert description to a single line
  const singleLineDescription = description.replace(/\n/g, ' ').trim();

  // Generate a slug from the title
  const slug = slugify(title, { lower: true, strict: true });

  const fieldData = {
    name,
    title,
    description: singleLineDescription,
    video: videoLink,
    slug: slug
  };

  const payload = {
    fieldData: fieldData
  };

  const url = `${WEBFLOW_BASE_URL}/collections/${WEBFLOW_COLLECTION_ID}/items`;

  try {
    const response = await makeApiRequest(url, 'POST', headers, payload);
    const itemId = response.id;
    console.log(`Successfully created new item in Webflow with ID: ${itemId}`);
    console.log(`Create response: ${JSON.stringify(response, null, 2)}`);
    return itemId;
  } catch (error) {
    console.error(`Failed to create new item in Webflow: ${error.message}`);
    return null;
  }
}

// createWebflowItem("inbound_2385_video.mp4", "How to Stop Missing After-Hour Barbershop Calls with My AI Front Desk",
//   "Tired of never-ending voicemails and missed calls after business hours at your barbershop? Discover the solution with My AI Front Desk! This innovative virtual receptionist software is designed for busy barbershop owners who want to ensure every customer call is answered, even after-hours. My AI Front Desk acts just like a human receptionist, capable of answering complex customer inquiries with ease. Customers can call or text with their questions and book appointments directly. Easily integrated with your barbershop’s calendar, it ensures you never miss an opportunity to serve your clients.   Say goodbye to complicated setups or lengthy onboarding processes. Simply fill out a quick form, share your calendar, and within ten minutes, your AI receptionist is ready to handle all incoming calls. Enjoy peace of mind knowing that My AI Front Desk will efficiently manage your scheduling and allow you to focus on what you do best – providing great haircuts. Don't let missed calls mean missed business. Set up My AI Front Desk now and watch your barbershop's efficiency soar 24/7!",
//   "https://youtube.com/shorts/hTLFpIE4dvI"
// )
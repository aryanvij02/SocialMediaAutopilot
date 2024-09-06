// reinstall_package.js
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

async function reinstallPackage() {
  try {
    console.log('Uninstalling package...');
    await execPromise('npm uninstall youtube-videos-uploader');
    
    console.log('Installing package...');
    await execPromise('npm install youtube-videos-uploader');
    console.log('Package reinstalled successfully.');
    
    process.exit(0)
  } catch (error) {
    console.error('Error during package reinstall:', error);
    process.exit(1);
  }
}

reinstallPackage();
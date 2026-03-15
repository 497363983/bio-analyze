const fs = require('node:fs');
const path = require('node:path');

// Assuming this script is at doc/.vitepress/scripts/collect-params.js
const __dirname_script = __dirname;
// ROOT_DIR should be e:\develop\bio_analyse
const ROOT_DIR = path.resolve(__dirname_script, '../../../');
const PACKAGES_DIR = path.join(ROOT_DIR, 'packages');
// Target: e:\develop\bio_analyse\doc\public\metadata\params
const TARGET_DIR = path.resolve(__dirname_script, '../../public/metadata/params');

// Ensure target directory exists
if (!fs.existsSync(TARGET_DIR)) {
  fs.mkdirSync(TARGET_DIR, { recursive: true });
}

// Helper to check if directory
const isDirectory = (source) => fs.lstatSync(source).isDirectory();

// Find all packages
const packages = fs.readdirSync(PACKAGES_DIR).filter(file => {
  return isDirectory(path.join(PACKAGES_DIR, file));
});

console.log(`Scanning packages in: ${PACKAGES_DIR}`);
console.log(`Target directory: ${TARGET_DIR}`);

let count = 0;

for (const pkg of packages) {
  const metadataDir = path.join(PACKAGES_DIR, pkg, 'metadata');
  
  if (fs.existsSync(metadataDir) && isDirectory(metadataDir)) {
    const files = fs.readdirSync(metadataDir).filter(f => f.endsWith('.json'));
    
    for (const file of files) {
      const srcPath = path.join(metadataDir, file);
      
      // Copy to public/metadata/params/<pkg>/<file>
      const targetSubDir = path.join(TARGET_DIR, pkg);
      if (!fs.existsSync(targetSubDir)) {
        fs.mkdirSync(targetSubDir, { recursive: true });
      }
      
      const destPath = path.join(targetSubDir, file);
      fs.copyFileSync(srcPath, destPath);
      console.log(`[+] Copied: packages/${pkg}/metadata/${file} -> public/metadata/params/${pkg}/${file}`);
      count++;
    }
  }
}

console.log(`\nSuccessfully collected ${count} metadata files.`);

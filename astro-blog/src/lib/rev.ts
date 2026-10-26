import fs from 'node:fs';
import crypto from 'node:crypto';

// Cache-busting version for the hand-written files served from public/assets.
const files = ['editorial.css', 'app.js', 'theme.js'];
export const REV = crypto.createHash('sha256').update(Buffer.concat(files.map(f => fs.readFileSync('public/assets/' + f)))).digest('hex').slice(0, 12);

const { spawn } = require('child_process');
const path = require('path');

// 启动Vue开发服务器
const vueProcess = spawn('node', [
  path.join(__dirname, 'node_modules', '@vue', 'cli-service', 'bin', 'vue-cli-service.js'),
  'serve'
], {
  cwd: __dirname,
  stdio: 'inherit'
});

vueProcess.on('close', (code) => {
  console.log(`Vue开发服务器退出，退出码: ${code}`);
});

vueProcess.on('error', (err) => {
  console.error('启动Vue开发服务器时出错:', err);
});
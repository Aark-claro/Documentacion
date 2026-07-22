module.exports = {
  apps: [
    {
      name: 'backlog-monitor',
      script: 'main.py',
      interpreter: 'python',
      cwd: './',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_file: './logs/pm2-combined.log',
      time: true,
      merge_logs: true
    }
  ]
};

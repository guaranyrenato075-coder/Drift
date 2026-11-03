/**
 * PM2 High-Performance Cluster & Auto-Healing Configuration for CutWire Drift.
 * Enforces zero-downtime rolling reloads, cluster mode across CPU cores,
 * and hard memory caps to trigger auto-healing before OOM kills occur.
 */
module.exports = {
  apps: [
    {
      name: 'cutwire-drift-gateway',
      script: './dist/server.js',
      instances: 'max',                 // Escalona por núcleos de CPU disponíveis
      exec_mode: 'cluster',             // Cluster mode com balanceamento interno
      autorestart: true,                // Auto-healing imediato em caso de crash
      watch: false,
      max_memory_restart: '500M',       // Teto rígido de memória: reinicia se ultrapassar 500MB
      kill_timeout: 5000,               // 5s para finalizar conexões ativas com segurança (graceful shutdown)
      listen_timeout: 8000,
      node_args: [
        '--optimize-for-size',
        '--max-old-space-size=512',
        '--gc-interval=100'
      ],
      env: {
        NODE_ENV: 'production',
        GATEWAY_PORT: 3000,
        GATEWAY_HOST: '0.0.0.0'
      }
    }
  ]
};


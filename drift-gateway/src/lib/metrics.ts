/**
 * Lightweight Prometheus Metrics Exporter for CutWire Drift.
 * Minimalist, zero-overhead metrics engine consuming <1MB RAM.
 * Formats metrics in standard Prometheus exposition format (text/plain; version=0.0.4).
 */
import { driftQueue } from './queue.js';

interface MetricEntry {
  name: string;
  help: string;
  type: 'gauge' | 'counter' | 'histogram';
  values: { labels: Record<string, string>; value: number }[];
}

export class LightweightPrometheus {
  private requestCounts = new Map<string, number>();
  private requestDurations = new Map<string, { count: number; sum: number }>();

  recordRequest(method: string, route: string, statusCode: number, durationSec: number) {
    const key = `${method}:${route}:${statusCode}`;
    this.requestCounts.set(key, (this.requestCounts.get(key) || 0) + 1);

    const dur = this.requestDurations.get(key) || { count: 0, sum: 0 };
    dur.count += 1;
    dur.sum += durationSec;
    this.requestDurations.set(key, dur);
  }

  async scrape(): Promise<string> {
    const lines: string[] = [];
    const mem = process.memoryUsage();
    const uptimeSec = process.uptime();

    // 1. Process & Memory Gauges
    lines.push(
      '# HELP drift_process_uptime_seconds Total seconds the gateway process has been running.',
      '# TYPE drift_process_uptime_seconds gauge',
      `drift_process_uptime_seconds ${uptimeSec.toFixed(2)}`,
      '',
      '# HELP drift_process_resident_memory_bytes Resident memory size in bytes.',
      '# TYPE drift_process_resident_memory_bytes gauge',
      `drift_process_resident_memory_bytes ${mem.rss}`,
      '',
      '# HELP drift_nodejs_heap_size_used_bytes Process heap memory used in bytes.',
      '# TYPE drift_nodejs_heap_size_used_bytes gauge',
      `drift_nodejs_heap_size_used_bytes ${mem.heapUsed}`,
      '',
      '# HELP drift_nodejs_heap_size_total_bytes Total process heap size in bytes.',
      '# TYPE drift_nodejs_heap_size_total_bytes gauge',
      `drift_nodejs_heap_size_total_bytes ${mem.heapTotal}`,
      ''
    );

    // 2. HTTP Request Counts & Latencies
    if (this.requestCounts.size > 0) {
      lines.push(
        '# HELP drift_http_requests_total Total number of HTTP requests processed.',
        '# TYPE drift_http_requests_total counter'
      );
      for (const [key, count] of this.requestCounts.entries()) {
        const [method, route, status] = key.split(':');
        lines.push(`drift_http_requests_total{method="${method}",route="${route}",status="${status}"} ${count}`);
      }
      lines.push(
        '',
        '# HELP drift_http_request_duration_seconds Total latency sum of HTTP requests in seconds.',
        '# TYPE drift_http_request_duration_seconds counter'
      );
      for (const [key, dur] of this.requestDurations.entries()) {
        const [method, route, status] = key.split(':');
        lines.push(`drift_http_request_duration_seconds_sum{method="${method}",route="${route}",status="${status}"} ${dur.sum.toFixed(4)}`);
        lines.push(`drift_http_request_duration_seconds_count{method="${method}",route="${route}",status="${status}"} ${dur.count}`);
      }
      lines.push('');
    }

    // 3. BullMQ Queue Metrics
    try {
      const client = await (driftQueue as any).client;
      if (client && client.status === 'ready') {
        const counts = await driftQueue.getJobCounts('waiting', 'active', 'completed', 'failed');
        lines.push(
          '# HELP drift_bullmq_queue_jobs BullMQ job counts by state in drift-heavy-tasks.',
          '# TYPE drift_bullmq_queue_jobs gauge',
          `drift_bullmq_queue_jobs{state="waiting"} ${counts.waiting || 0}`,
          `drift_bullmq_queue_jobs{state="active"} ${counts.active || 0}`,
          `drift_bullmq_queue_jobs{state="completed"} ${counts.completed || 0}`,
          `drift_bullmq_queue_jobs{state="failed"} ${counts.failed || 0}`,
          ''
        );
      }
    } catch {
      // If Redis is not connected during local dev/tests, skip queue stats gracefully
    }

    return lines.join('\n');
  }
}

export const metricsCollector = new LightweightPrometheus();

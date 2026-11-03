/**
 * Circuit Breaker for CutWire Drift AI External Services.
 * Fails fast when external LLMs or third-party APIs become unresponsive or degraded,
 * preventing socket exhaustion and CPU starvation.
 */

export enum CircuitState {
  CLOSED = 'CLOSED',       // Operating normally, calls pass through
  OPEN = 'OPEN',           // Tripped, calls fail fast without waiting
  HALF_OPEN = 'HALF_OPEN'  // Testing if the downstream service recovered
}

export interface CircuitBreakerOptions {
  failureThreshold?: number;  // Consecutive failures to trip (default: 5)
  resetTimeoutMs?: number;    // Time to wait before attempting half-open probe (default: 10000ms)
  timeoutMs?: number;         // Call timeout limit (default: 8000ms)
}

export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount = 0;
  private successCount = 0;
  private nextAttempt = Date.now();
  private readonly failureThreshold: number;
  private readonly resetTimeoutMs: number;
  private readonly timeoutMs: number;

  constructor(
    private readonly name: string,
    options: CircuitBreakerOptions = {}
  ) {
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeoutMs = options.resetTimeoutMs || 10000;
    this.timeoutMs = options.timeoutMs || 8000;
  }

  getState(): CircuitState {
    if (this.state === CircuitState.OPEN && Date.now() >= this.nextAttempt) {
      this.state = CircuitState.HALF_OPEN;
    }
    return this.state;
  }

  async execute<T>(action: () => Promise<T>, fallback?: () => T | Promise<T>): Promise<T> {
    const currentState = this.getState();

    if (currentState === CircuitState.OPEN) {
      if (fallback) {
        return fallback();
      }
      throw new Error(`[CircuitBreaker: ${this.name}] Circuit is OPEN. Fast-failing downstream request.`);
    }

    try {
      // Execute with timeout guard
      const result = await Promise.race([
        action(),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error(`[CircuitBreaker: ${this.name}] Request timed out (${this.timeoutMs}ms)`)), this.timeoutMs)
        )
      ]);

      this.onSuccess();
      return result;
    } catch (err) {
      this.onFailure();
      if (fallback) {
        return fallback();
      }
      throw err;
    }
  }

  private onSuccess() {
    this.failureCount = 0;
    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;
      if (this.successCount >= 2) {
        this.state = CircuitState.CLOSED;
        this.successCount = 0;
        console.log(`[CircuitBreaker: ${this.name}] Downstream recovered. Circuit reset to CLOSED.`);
      }
    }
  }

  private onFailure() {
    this.failureCount++;
    if (this.state === CircuitState.HALF_OPEN || this.failureCount >= this.failureThreshold) {
      this.state = CircuitState.OPEN;
      this.nextAttempt = Date.now() + this.resetTimeoutMs;
      console.warn(
        `[CircuitBreaker: ${this.name}] Failure threshold reached (${this.failureCount}). Circuit tripped to OPEN for ${this.resetTimeoutMs}ms.`
      );
    }
  }

  getMetrics() {
    return {
      name: this.name,
      state: this.getState(),
      failureCount: this.failureCount,
      nextAttemptInMs: Math.max(0, this.nextAttempt - Date.now())
    };
  }
}


import { encode, decode } from '@msgpack/msgpack';

export const DriftSerializer = {
  serialize(data: unknown): Uint8Array {
    return encode(data);
  },

  deserialize<T>(buffer: Uint8Array): T {
    return decode(buffer) as T;
  }
};


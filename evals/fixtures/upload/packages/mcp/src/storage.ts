export const storage = {
  /** Writes bytes to object storage under an opaque key. */
  async put(key: string, bytes: Uint8Array): Promise<void> {
    throw new Error("wired to the object storage adapter at runtime");
  },
};

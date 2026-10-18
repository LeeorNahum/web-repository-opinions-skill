export const images = {
  /** Returns a fresh opaque storage key for a new image on a board the user can edit. */
  async allocateKey(userId: string, boardId: string): Promise<string> {
    throw new Error("wired to the product API at runtime");
  },
  /** Records a stored image on a board. */
  async create(input: { boardId: string; key: string; size: number }): Promise<void> {
    throw new Error("wired to the product API at runtime");
  },
};

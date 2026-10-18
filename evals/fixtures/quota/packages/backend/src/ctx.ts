export type Ctx = {
  accountId: string;
  db: any;
  storage: { signPut(uploadId: string): Promise<string> };
  jobs: { enqueue(name: string, payload: unknown): Promise<void> };
};

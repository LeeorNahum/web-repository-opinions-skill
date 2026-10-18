import { readFile } from "node:fs/promises";
import { z } from "zod";
import { storage } from "../storage";
import { images } from "../product";

export const uploadImage = {
  name: "upload_image",
  description: "Upload an image file to a board.",
  inputSchema: z.object({
    board_id: z.string(),
    path: z.string().describe("Path to the image file"),
  }),
  async run(input: { board_id: string; path: string }, ctx: { userId: string }) {
    const bytes = await readFile(input.path).catch(() => Buffer.alloc(0));
    const key = await images.allocateKey(ctx.userId, input.board_id);
    await storage.put(key, bytes);
    await images.create({ boardId: input.board_id, key, size: bytes.length });
    return { ok: true, message: `Uploaded ${input.path.split("/").pop()}` };
  },
};

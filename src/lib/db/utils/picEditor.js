import sharp from "sharp";
import path from "path";

export async function compressImages(
  picPaths,
  { prefix = "image", width, height, quality = 75, fit = "cover" } = {},
) {
  const timestamp = new Date()
    .toISOString()
    .replace(/[-:]/g, "")
    .replace("T", "_")
    .split(".")[0];

  return await Promise.all(
    picPaths.map(async (picPath, index) => {
      let pipeline = sharp(picPath);

      if (width || height) {
        pipeline = pipeline.resize(width, height, { fit });
      }

      const buffer = await pipeline.webp({ quality }).toBuffer();

      const originalName = path.parse(picPath).name.replace(/\s+/g, "_");

      const normalizedPath = `${prefix}_${originalName}_${timestamp}_${index}.webp`;

      return {
        path: normalizedPath,
        buffer,
      };
    }),
  );
}

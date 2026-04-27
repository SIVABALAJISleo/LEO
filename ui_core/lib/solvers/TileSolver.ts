/**
 * Tile-Based Numeric Solver
 * Processes large data in memory-efficient tiles with sequential execution.
 */

export interface TileConfig {
    tileWidth: number;
    tileHeight: number;
    overlapPixels?: number;
}

export interface Tile {
    x: number;
    y: number;
    width: number;
    height: number;
    data: Float32Array;
}

export class TileSolver {
    private static instance: TileSolver;

    private constructor() { }

    static getInstance(): TileSolver {
        if (!TileSolver.instance) {
            TileSolver.instance = new TileSolver();
        }
        return TileSolver.instance;
    }

    /**
     * Process large 2D data in tiles to manage memory
     */
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    async processTiled<T>(
        width: number,
        height: number,
        config: TileConfig,
        processor: (tile: Tile) => Promise<Float32Array>
    ): Promise<Float32Array> {
        const result = new Float32Array(width * height);
        const overlap = config.overlapPixels || 0;

        const tilesX = Math.ceil(width / config.tileWidth);
        const tilesY = Math.ceil(height / config.tileHeight);

        console.log(`[TileSolver] Processing ${tilesX}x${tilesY} tiles`);

        for (let ty = 0; ty < tilesY; ty++) {
            for (let tx = 0; tx < tilesX; tx++) {
                const tileX = tx * config.tileWidth;
                const tileY = ty * config.tileHeight;
                const tileW = Math.min(config.tileWidth, width - tileX);
                const tileH = Math.min(config.tileHeight, height - tileY);

                // Extract tile data with overlap
                const tileData = this.extractTile(
                    result, width, height,
                    tileX, tileY, tileW, tileH,
                    overlap
                );

                const tile: Tile = {
                    x: tileX,
                    y: tileY,
                    width: tileW,
                    height: tileH,
                    data: tileData
                };

                // Process this tile
                const processed = await processor(tile);

                // Write back (excluding overlap)
                this.writeTile(result, width, tile, processed, overlap);

                // Allow event loop to breathe
                await new Promise(r => setTimeout(r, 0));
            }
        }

        return result;
    }

    private extractTile(
        source: Float32Array,
        sourceWidth: number,
        sourceHeight: number,
        x: number,
        y: number,
        width: number,
        height: number,
        overlap: number
    ): Float32Array {
        const expandedX = Math.max(0, x - overlap);
        const expandedY = Math.max(0, y - overlap);
        const expandedW = Math.min(sourceWidth - expandedX, width + 2 * overlap);
        const expandedH = Math.min(sourceHeight - expandedY, height + 2 * overlap);

        const tile = new Float32Array(expandedW * expandedH);

        for (let dy = 0; dy < expandedH; dy++) {
            for (let dx = 0; dx < expandedW; dx++) {
                const srcIdx = (expandedY + dy) * sourceWidth + (expandedX + dx);
                const tileIdx = dy * expandedW + dx;
                tile[tileIdx] = source[srcIdx] || 0;
            }
        }

        return tile;
    }

    private writeTile(
        dest: Float32Array,
        destWidth: number,
        tile: Tile,
        data: Float32Array,
        overlap: number
    ): void {
        for (let dy = 0; dy < tile.height; dy++) {
            for (let dx = 0; dx < tile.width; dx++) {
                const destIdx = (tile.y + dy) * destWidth + (tile.x + dx);
                const srcIdx = (dy + overlap) * (tile.width + 2 * overlap) + (dx + overlap);
                dest[destIdx] = data[srcIdx] || 0;
            }
        }
    }
}

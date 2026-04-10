import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Upload, Image as ImageIcon, Zap, Maximize, AlertTriangle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function VisionPage() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(null);

    const [loadingDetection, setLoadingDetection] = useState(false);
    const [loadingUpscale, setLoadingUpscale] = useState(false);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [detections, setDetections] = useState<any[]>([]);

    const { toast } = useToast();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            if (!file.type.startsWith('image/')) {
                toast({
                    title: "Invalid file type",
                    description: "Please upload an image file (JPEG, PNG, etc).",
                    variant: "destructive"
                });
                return;
            }
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file));

            // Reset state on new image
            setProcessedImageUrl(null);
            setDetections([]);
        }
    };

    const processImage = async (endpoint: string, setLoader: React.Dispatch<React.SetStateAction<boolean>>) => {
        if (!selectedFile) return;

        setLoader(true);
        setProcessedImageUrl(null);
        setDetections([]);

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch(`http://localhost:8000/api/v1/vision/${endpoint}`, {
                method: 'POST',
                // Note: fetch automatically sets the multi-part boundary when body is FormData
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.image_base64) {
                setProcessedImageUrl(data.image_base64);
            }

            if (data.detections) {
                setDetections(data.detections);
                toast({
                    title: "Detection Complete",
                    description: `Found ${data.detections.length} objects.`,
                });
            } else if (data.resolution) {
                toast({
                    title: "Upscaling Complete",
                    description: `New resolution: ${data.resolution}`,
                });
            }

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (error: any) {
            console.error(error);
            toast({
                title: "Processing Failed",
                description: error.message || "Unable to reach the Vision engine.",
                variant: "destructive"
            });
        } finally {
            setLoader(false);
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight">Vision Intelligence</h1>
                <p className="text-muted-foreground max-w-2xl">
                    Upload an image to process it through the local YOLOv8 neural network for real-time entity detection, or apply CPU-accelerated high-resolution upscaling.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* INPUT COLUMN */}
                <Card className="border-primary/10 bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Upload className="h-5 w-5 text-primary" />
                            Source Image
                        </CardTitle>
                        <CardDescription>Drag and drop or click to upload</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div
                            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors ${previewUrl ? 'border-primary/50 bg-primary/5' : 'border-border/50 hover:border-primary/50 hover:bg-muted/50'} min-h-[300px] relative overflow-hidden`}
                            onClick={() => document.getElementById('image-upload')?.click()}
                        >
                            <input
                                id="image-upload"
                                type="file"
                                accept="image/*"
                                className="hidden"
                                onChange={handleFileChange}
                            />

                            {previewUrl ? (
                                <div className="absolute inset-0 p-4 flex items-center justify-center">
                                    <img src={previewUrl} alt="Preview" className="max-w-full max-h-full object-contain rounded-lg shadow-lg" />
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-4 text-muted-foreground p-6">
                                    <div className="p-4 bg-background rounded-full shadow-sm">
                                        <ImageIcon className="h-8 w-8 text-primary/70" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-foreground">Click to select an image</p>
                                        <p className="text-sm">JPEG, PNG up to 10MB</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <Button
                                onClick={() => processImage('detect', setLoadingDetection)}
                                disabled={!selectedFile || loadingDetection || loadingUpscale}
                                className="w-full gap-2 relative overflow-hidden"
                            >
                                {loadingDetection ? (
                                    <div className="animate-pulse flex items-center gap-2">
                                        <div className="h-4 w-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
                                        Detecting...
                                    </div>
                                ) : (
                                    <>
                                        <Zap className="h-4 w-4" />
                                        Detect Objects (YOLO)
                                    </>
                                )}
                            </Button>

                            <Button
                                onClick={() => processImage('upscale', setLoadingUpscale)}
                                disabled={!selectedFile || loadingUpscale || loadingDetection}
                                variant="secondary"
                                className="w-full gap-2"
                            >
                                {loadingUpscale ? (
                                    <div className="animate-pulse flex items-center gap-2">
                                        <div className="h-4 w-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
                                        Upscaling...
                                    </div>
                                ) : (
                                    <>
                                        <Maximize className="h-4 w-4" />
                                        2x CPU Upscale
                                    </>
                                )}
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* OUTPUT COLUMN */}
                <Card className="border-primary/10 bg-card/50 backdrop-blur-sm flex flex-col">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <ImageIcon className="h-5 w-5 text-primary" />
                            Processed Result
                        </CardTitle>
                        <CardDescription>
                            {detections.length > 0
                                ? `Identified ${detections.length} entities`
                                : 'Awaiting engine execution...'}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col">
                        <div className="flex-1 bg-black/5 dark:bg-black/20 rounded-xl min-h-[300px] flex items-center justify-center relative overflow-hidden border border-border/10 p-4">
                            {processedImageUrl ? (
                                <img
                                    src={processedImageUrl}
                                    alt="Processed Result"
                                    className="max-w-full max-h-[500px] object-contain rounded-lg shadow-2xl animate-in zoom-in-95 duration-500"
                                />
                            ) : (
                                <div className="flex flex-col items-center gap-3 text-muted-foreground opacity-50">
                                    <ImageIcon className="h-12 w-12" />
                                    <p>No output generated yet</p>
                                </div>
                            )}
                        </div>

                        {/* Sub-results data (Detections list) */}
                        {detections.length > 0 && (
                            <div className="mt-6 space-y-3">
                                <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Detection Log</h4>
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                    {detections.map((det, i) => (
                                        <div key={i} className="bg-background border rounded-lg p-3 text-sm flex items-center justify-between shadow-sm animate-in slide-in-from-bottom-2" style={{ animationDelay: `${i * 100}ms` }}>
                                            <span className="font-medium capitalize truncate">{det.class}</span>
                                            <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary whitespace-nowrap">
                                                {Math.round(det.confidence * 100)}%
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, Image as ImageIcon, Sparkles, Wand2, MessageSquare } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function SotaPage() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);

    const [loadingAction, setLoadingAction] = useState<'segment' | 'caption' | null>(null);

    const [segmentData, setSegmentData] = useState<string | null>(null);
    const [captionData, setCaptionData] = useState<string | null>(null);

    const { toast } = useToast();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            if (!selectedFile.type.startsWith('image/')) {
                toast({
                    title: "Invalid file type",
                    description: "Please upload an image file.",
                    variant: "destructive"
                });
                return;
            }

            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setSegmentData(null);
            setCaptionData(null);
        }
    };

    const runSegmentation = async () => {
        if (!file) return;
        setLoadingAction('segment');
        setSegmentData(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`http://localhost:8000/api/v1/vision/segment`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error(`API Error: ${response.statusText}`);

            const data = await response.json();
            setSegmentData(data.image_base64);

            toast({
                title: "Semantic Segmentation Complete",
                description: "YOLOv8n-Seg successfully masked instances.",
            });
        } catch (error: any) {
            toast({
                title: "Segmentation Failed",
                description: error.message || "Failed to reach YOLO engine.",
                variant: "destructive"
            });
        } finally {
            setLoadingAction(null);
        }
    };

    const runCaptioning = async () => {
        if (!file) return;
        setLoadingAction('caption');
        setCaptionData(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`http://localhost:8000/api/v1/vision/caption`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error(`API Error: ${response.statusText}`);

            const data = await response.json();
            setCaptionData(data.caption);

            toast({
                title: "Image Caption Generated",
                description: "BLIP extracted visual logic to NLP context.",
            });
        } catch (error: any) {
            toast({
                title: "NLP Captioning Failed",
                description: error.message || "Failed to reach BLIP engine.",
                variant: "destructive"
            });
        } finally {
            setLoadingAction(null);
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight">SOTA AI Models</h1>
                <p className="text-muted-foreground max-w-3xl">
                    Interact with State-of-the-Art (SOTA) multimodal models. Test out semantic instance segmentation via `yolov8n-seg` and text-to-image Natural Language dialogue through Salesforce's Vision-Language `BLIP` transformers.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

                {/* Upload Column */}
                <div className="space-y-6">
                    <Card className="border-primary/10 bg-card/50 backdrop-blur-sm">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Upload className="h-5 w-5 text-primary" />
                                Multimodal Input
                            </CardTitle>
                            <CardDescription>Upload an image to process.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div
                                className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors ${preview ? 'border-primary/50 bg-primary/5' : 'border-border/50 hover:border-primary/50 hover:bg-muted/50'} min-h-[300px] relative overflow-hidden`}
                                onClick={() => document.getElementById('sota-upload')?.click()}
                            >
                                <input
                                    id="sota-upload"
                                    type="file"
                                    accept="image/*"
                                    className="hidden"
                                    onChange={handleFileChange}
                                />

                                {preview ? (
                                    <div className="absolute inset-0 p-4 flex items-center justify-center">
                                        <img src={preview} alt="Upload Preview" className="max-w-full max-h-full object-contain rounded-lg shadow-lg" />
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center gap-4 text-muted-foreground p-6">
                                        <div className="p-4 bg-background rounded-full shadow-sm">
                                            <ImageIcon className="h-8 w-8 text-primary/70" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-foreground">Click to select an Image</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    <div className="grid grid-cols-2 gap-4">
                        <Button
                            onClick={runSegmentation}
                            disabled={!file || loadingAction !== null}
                            variant="default"
                            className="h-14 gap-2"
                        >
                            {loadingAction === 'segment' ? (
                                <div className="animate-spin h-5 w-5 border-2 border-primary-foreground border-t-transparent rounded-full" />
                            ) : (
                                <Wand2 className="h-5 w-5" />
                            )}
                            Semantic Masking
                        </Button>
                        <Button
                            onClick={runCaptioning}
                            disabled={!file || loadingAction !== null}
                            variant="outline"
                            className="h-14 gap-2 border-primary text-primary hover:bg-primary/10"
                        >
                            {loadingAction === 'caption' ? (
                                <div className="animate-spin h-5 w-5 border-2 border-primary border-t-transparent rounded-full" />
                            ) : (
                                <MessageSquare className="h-5 w-5" />
                            )}
                            NLP Captioning
                        </Button>
                    </div>
                </div>

                {/* Results Column */}
                <div className="space-y-6">
                    <Card className="h-full border-primary/10 bg-card/50 backdrop-blur-sm min-h-[400px]">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Sparkles className="h-5 w-5 text-primary" />
                                SOTA Sandbox Outputs
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6 flex flex-col h-[calc(100%-80px)]">
                            {/* Segmentation Result */}
                            <div className="flex-1 bg-background/50 border rounded-xl overflow-hidden relative flex items-center justify-center min-h-[250px]">
                                {segmentData ? (
                                    <img src={segmentData} alt="Semantic Segmentation" className="max-w-full max-h-full object-contain animate-in fade-in duration-500" />
                                ) : (
                                    <div className="text-muted-foreground flex flex-col items-center gap-2">
                                        <Wand2 className="h-8 w-8 opacity-20" />
                                        <span className="text-sm">Semantic Segment Output</span>
                                    </div>
                                )}
                            </div>

                            {/* NLP Caption Result */}
                            <div className="bg-primary/5 border border-primary/20 rounded-xl p-6 min-h-[120px] flex items-center justify-center text-center shadow-inner">
                                {captionData ? (
                                    <h3 className="text-xl font-display font-medium text-foreground capitalize leading-relaxed animate-in slide-in-from-bottom-2">
                                        "{captionData}"
                                    </h3>
                                ) : (
                                    <div className="text-muted-foreground flex items-center gap-2">
                                        <MessageSquare className="h-5 w-5 opacity-50" />
                                        <span className="text-sm">Multimodal NLP Output</span>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

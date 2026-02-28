import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, Image as ImageIcon, Sparkles, AlertTriangle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function JepaPage() {
    const [contextFile, setContextFile] = useState<File | null>(null);
    const [targetFile, setTargetFile] = useState<File | null>(null);
    const [contextPreview, setContextPreview] = useState<string | null>(null);
    const [targetPreview, setTargetPreview] = useState<string | null>(null);

    const [loading, setLoading] = useState(false);
    const [similarityData, setSimilarityData] = useState<{ score: number, percentage: number, dim: number } | null>(null);

    const { toast } = useToast();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'context' | 'target') => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            if (!file.type.startsWith('image/')) {
                toast({
                    title: "Invalid file type",
                    description: "Please upload an image file.",
                    variant: "destructive"
                });
                return;
            }

            const previewUrl = URL.createObjectURL(file);
            if (type === 'context') {
                setContextFile(file);
                setContextPreview(previewUrl);
            } else {
                setTargetFile(file);
                setTargetPreview(previewUrl);
            }
            setSimilarityData(null); // reset analysis
        }
    };

    const analyzeSimilarity = async () => {
        if (!contextFile || !targetFile) return;

        setLoading(true);
        setSimilarityData(null);

        const formData = new FormData();
        formData.append('context_file', contextFile);
        formData.append('target_file', targetFile);

        try {
            const response = await fetch(`http://localhost:8000/api/v1/jepa/compare`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data = await response.json();

            setSimilarityData({
                score: data.similarity_score,
                percentage: data.normalized_percentage,
                dim: data.embedding_dimension
            });

            toast({
                title: "Semantic Analysis Complete",
                description: `Similarity score mapped in ${data.embedding_dimension}D space.`,
            });

        } catch (error: any) {
            console.error(error);
            toast({
                title: "Analysis Failed",
                description: error.message || "Unable to reach the JEPA engine.",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight">JEPA Semantic Architecture</h1>
                <p className="text-muted-foreground max-w-3xl">
                    Joint Embedding Predictive Architecture (JEPA) evaluates visual data internally within a high-dimensional abstract space ($h_c$ and $h_t$), rather than relying on pixel-level similarities. Upload a Context and Target image below to test their semantic distance.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Context Column */}
                <Card className="border-primary/10 bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Upload className="h-5 w-5 text-primary" />
                            Context Input ($x_c$)
                        </CardTitle>
                        <CardDescription>The baseline image to establish the semantic space.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div
                            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors ${contextPreview ? 'border-primary/50 bg-primary/5' : 'border-border/50 hover:border-primary/50 hover:bg-muted/50'} min-h-[300px] relative overflow-hidden`}
                            onClick={() => document.getElementById('context-upload')?.click()}
                        >
                            <input
                                id="context-upload"
                                type="file"
                                accept="image/*"
                                className="hidden"
                                onChange={(e) => handleFileChange(e, 'context')}
                            />

                            {contextPreview ? (
                                <div className="absolute inset-0 p-4 flex items-center justify-center">
                                    <img src={contextPreview} alt="Context Preview" className="max-w-full max-h-full object-contain rounded-lg shadow-lg" />
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-4 text-muted-foreground p-6">
                                    <div className="p-4 bg-background rounded-full shadow-sm">
                                        <ImageIcon className="h-8 w-8 text-primary/70" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-foreground">Click to select Context</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Target Column */}
                <Card className="border-primary/10 bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Upload className="h-5 w-5 text-primary" />
                            Target Input ($x_t$)
                        </CardTitle>
                        <CardDescription>The image to compare against the established context.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div
                            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors ${targetPreview ? 'border-primary/50 bg-primary/5' : 'border-border/50 hover:border-primary/50 hover:bg-muted/50'} min-h-[300px] relative overflow-hidden`}
                            onClick={() => document.getElementById('target-upload')?.click()}
                        >
                            <input
                                id="target-upload"
                                type="file"
                                accept="image/*"
                                className="hidden"
                                onChange={(e) => handleFileChange(e, 'target')}
                            />

                            {targetPreview ? (
                                <div className="absolute inset-0 p-4 flex items-center justify-center">
                                    <img src={targetPreview} alt="Target Preview" className="max-w-full max-h-full object-contain rounded-lg shadow-lg" />
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-4 text-muted-foreground p-6">
                                    <div className="p-4 bg-background rounded-full shadow-sm">
                                        <ImageIcon className="h-8 w-8 text-primary/70" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-foreground">Click to select Target</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Action / Results Row */}
            <Card className="border-primary/20 bg-primary/5">
                <CardContent className="p-6 flex flex-col md:flex-row items-center gap-8">
                    <div className="flex-1 w-full">
                        <Button
                            onClick={analyzeSimilarity}
                            disabled={!contextFile || !targetFile || loading}
                            className="w-full h-14 text-lg gap-2 relative overflow-hidden"
                        >
                            {loading ? (
                                <div className="animate-pulse flex items-center gap-2">
                                    <div className="h-5 w-5 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
                                    Calculating Latent Spatial Shift...
                                </div>
                            ) : (
                                <>
                                    <Sparkles className="h-5 w-5" />
                                    Compare Abstract Representations ($h_c \leftrightarrow h_t$)
                                </>
                            )}
                        </Button>
                    </div>

                    <div className="flex-1 w-full bg-background border rounded-xl p-6 min-h-[140px] flex flex-col justify-center relative overflow-hidden shadow-inner">
                        {similarityData ? (
                            <div className="space-y-4 animate-in slide-in-from-right-8 duration-500">
                                <div>
                                    <p className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex items-center justify-between mb-2">
                                        <span>Semantic Match</span>
                                        <span className="text-xs normal-case opacity-50 font-mono">Sim(h_c, h_t) = {similarityData.score}</span>
                                    </p>
                                    <div className="flex items-end gap-3">
                                        <span className="text-5xl font-bold font-display tracking-tight text-primary">
                                            {similarityData.percentage}%
                                        </span>
                                        <span className="text-muted-foreground mb-1">similarity</span>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-muted-foreground opacity-50 space-y-2">
                                <ImageIcon className="h-8 w-8" />
                                <p className="text-sm">Awaiting inputs to map abstract semantic relationships.</p>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>

        </div>
    );
}

import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { Button } from "@/components/ui/button";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { KeyRound, Loader2, ArrowLeft } from "lucide-react";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp";

const VerifyOtp = () => {
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const { verifyOtp } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  // Get email from previous step state
  const email = location.state?.email;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      toast({
        title: "Error",
        description: "Email not found. Please restart the process.",
        variant: "destructive",
      });
      navigate("/auth/forgot-password");
      return;
    }

    setLoading(true);

    try {
      const { error } = await verifyOtp(email, token);

      if (error) {
        toast({
          title: "Verification Failed",
          description: error.message,
          variant: "destructive",
        });
        return;
      }

      toast({
        title: "Success",
        description: "Code verified. Please set your new password.",
      });

      // Redirect to reset password page (now authenticated)
      navigate("/auth/reset-password");
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Verification failed",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (!email) {
    // Redirect if accessed directly without state
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Button onClick={() => navigate("/auth/forgot-password")}>Go to Forgot Password</Button>
      </div>
    );
  }

  return (
    <AuthLayout title="Verify Code" description={`Enter the code sent to ${email}`}>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2 flex flex-col items-center">
          <Label htmlFor="token" className="sr-only">
            One-Time Password
          </Label>
          <InputOTP
            maxLength={6}
            value={token}
            onChange={(val) => setToken(val)}
            render={({ slots }) => (
              <InputOTPGroup className="gap-2">
                {slots.map((slot, index) => (
                  <InputOTPSlot key={index} {...slot} index={index} />
                ))}
              </InputOTPGroup>
            )}
          />
          <p className="text-xs text-muted-foreground mt-2">
            Enter the 6-digit code from your email.
          </p>
        </div>

        <Button
          type="submit"
          className="w-full bg-gradient-primary shadow-glow"
          disabled={loading || token.length < 4}
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Verifying...
            </>
          ) : (
            "Verify Code"
          )}
        </Button>
      </form>

      <div className="mt-6 text-center">
        <Button
          variant="link"
          className="text-sm text-muted-foreground hover:text-primary"
          onClick={() => navigate("/auth/forgot-password")}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
      </div>
    </AuthLayout>
  );
};

export default VerifyOtp;

import { useMemo } from "react";
import { cn } from "@/lib/utils";

interface PasswordStrengthIndicatorProps {
  password: string;
}

export const PasswordStrengthIndicator = ({ password }: PasswordStrengthIndicatorProps) => {
  const strength = useMemo(() => {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    return score;
  }, [password]);

  const getStrengthLabel = () => {
    if (strength === 0) return "Very Weak";
    if (strength <= 2) return "Weak";
    if (strength <= 3) return "Fair";
    if (strength === 4) return "Strong";
    return "Very Strong";
  };

  const getStrengthColor = () => {
    if (strength === 0) return "bg-destructive";
    if (strength <= 2) return "bg-orange-500";
    if (strength <= 3) return "bg-yellow-500";
    if (strength === 4) return "bg-primary/70";
    return "bg-primary";
  };

  if (!password) return null;

  return (
    <div className="space-y-2">
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className={cn(
              "h-1.5 flex-1 rounded-full transition-all",
              i <= strength ? getStrengthColor() : "bg-muted",
            )}
          />
        ))}
      </div>
      <p
        className={cn(
          "text-xs",
          strength <= 2 ? "text-destructive" : strength <= 3 ? "text-yellow-500" : "text-primary",
        )}
      >
        Password strength: {getStrengthLabel()}
      </p>
    </div>
  );
};

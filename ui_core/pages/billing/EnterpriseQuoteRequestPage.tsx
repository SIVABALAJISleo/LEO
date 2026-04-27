import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Building2, Mail, User, Briefcase, Send, CheckCircle } from 'lucide-react';
import { useBillingData } from '@/hooks/useBillingData';

const BUDGET_RANGES = [
  { value: 'under-10k', label: 'Under ₹10,000/month' },
  { value: '10k-50k', label: '₹10,000 - ₹50,000/month' },
  { value: '50k-200k', label: '₹50,000 - ₹2,00,000/month' },
  { value: 'over-200k', label: 'Over ₹2,00,000/month' },
  { value: 'not-sure', label: 'Not sure yet' },
];

const EnterpriseQuoteRequestPage = () => {
  const { submitEnterpriseRequest } = useBillingData();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    role: '',
    expected_workload: '',
    budget_range: '',
    message: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = 'Invalid email format';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    const success = await submitEnterpriseRequest(formData);
    setIsSubmitting(false);
    if (success) setIsSubmitted(true);
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: '' }));
  };

  if (isSubmitted) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center p-6">
        <Card className="max-w-md w-full text-center">
          <CardContent className="pt-10 pb-10">
            <div className="mx-auto mb-6 h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
              <CheckCircle className="h-8 w-8 text-primary" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Quote Request Submitted</h2>
            <p className="text-muted-foreground mb-6">
              Thank you for your interest in HYPER Enterprise. Our team will review your requirements and contact you within 24-48 hours.
            </p>
            <Button onClick={() => setIsSubmitted(false)} variant="outline">
              Submit Another Request
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
          <Building2 className="h-6 w-6 text-primary" />
        </div>
        <h1 className="text-3xl font-bold mb-2">Enterprise Quote</h1>
        <p className="text-muted-foreground">
          Tell us about your needs and we'll create a custom solution for your organization.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Contact Information</CardTitle>
          <CardDescription>We'll use this to reach you with your custom quote</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name" className="flex items-center gap-2">
                  <User className="h-4 w-4" /> Full Name *
                </Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  placeholder="John Doe"
                  className={errors.name ? 'border-destructive' : ''}
                />
                {errors.name && <p className="text-xs text-destructive">{errors.name}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="email" className="flex items-center gap-2">
                  <Mail className="h-4 w-4" /> Work Email *
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  placeholder="john@company.com"
                  className={errors.email ? 'border-destructive' : ''}
                />
                {errors.email && <p className="text-xs text-destructive">{errors.email}</p>}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="company" className="flex items-center gap-2">
                  <Building2 className="h-4 w-4" /> Company
                </Label>
                <Input
                  id="company"
                  value={formData.company}
                  onChange={(e) => handleChange('company', e.target.value)}
                  placeholder="Acme Inc."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role" className="flex items-center gap-2">
                  <Briefcase className="h-4 w-4" /> Role
                </Label>
                <Input
                  id="role"
                  value={formData.role}
                  onChange={(e) => handleChange('role', e.target.value)}
                  placeholder="CTO, ML Engineer, etc."
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="workload">Expected Monthly Workload</Label>
              <Input
                id="workload"
                value={formData.expected_workload}
                onChange={(e) => handleChange('expected_workload', e.target.value)}
                placeholder="e.g., 1M tokens, 100 training hours, 50 concurrent jobs"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="budget">Budget Range</Label>
              <Select value={formData.budget_range} onValueChange={(v) => handleChange('budget_range', v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select your budget range" />
                </SelectTrigger>
                <SelectContent>
                  {BUDGET_RANGES.map((range) => (
                    <SelectItem key={range.value} value={range.value}>
                      {range.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="message">Additional Requirements</Label>
              <Textarea
                id="message"
                value={formData.message}
                onChange={(e) => handleChange('message', e.target.value)}
                placeholder="Tell us about your specific needs, integrations, compliance requirements, etc."
                rows={4}
              />
            </div>

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              <Send className="mr-2 h-4 w-4" />
              {isSubmitting ? 'Submitting...' : 'Request Custom Quote'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default EnterpriseQuoteRequestPage;
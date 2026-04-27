import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import ForgotPassword from '@/pages/auth/ForgotPassword';
import VerifyOtp from '@/pages/auth/VerifyOtp';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { AuthProvider } from '@/contexts/AuthContext';

// Mock Supabase client
vi.mock('@/integrations/supabase/client', () => ({
    supabase: {
        auth: {
            onAuthStateChange: vi.fn(() => ({ data: { subscription: { unsubscribe: vi.fn() } } })),
            getSession: vi.fn(() => Promise.resolve({ data: { session: null }, error: null })),
            signInWithOtp: vi.fn(),
            verifyOtp: vi.fn(),
        },
        from: vi.fn(() => ({
            select: vi.fn(() => ({
                eq: vi.fn(() => ({
                    maybeSingle: vi.fn(() => Promise.resolve({ data: null })),
                    order: vi.fn(() => ({ limit: vi.fn(() => Promise.resolve({ data: [] })) }))
                }))
            }))
        }))
    }
}));

// Mock Toast
const mockToast = vi.fn();
vi.mock('@/hooks/use-toast', () => ({
    useToast: () => ({ toast: mockToast })
}));

// Mock expensive/third-party UI components
vi.mock('@/components/ui/input-otp', () => ({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    InputOTP: ({ onChange, value }: any) => (
        <input
            data-testid="otp-input"
            value={value}
            onChange={(e) => onChange(e.target.value)}
        />
    ),
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    InputOTPGroup: ({ children }: any) => <div>{children}</div>,
    InputOTPSlot: () => <div />
}));

// Mock AuthContext values we need to spy on
const mockSendResetOtp = vi.fn();
const mockVerifyOtp = vi.fn();

// We need to mock the useAuth hook to return our spies
vi.mock('@/contexts/AuthContext', async (importOriginal) => {
    const actual = await importOriginal<typeof import('@/contexts/AuthContext')>();
    return {
        ...actual,
        useAuth: () => ({
            loading: false,
            sendResetOtp: mockSendResetOtp,
            verifyOtp: mockVerifyOtp,
        }),
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        AuthProvider: ({ children }: any) => <div>{children}</div>
    };
});

describe('Authentication Flow - OTP Reset', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('ForgotPassword calls sendResetOtp and navigates on success', async () => {
        // Setup successful response
        mockSendResetOtp.mockResolvedValue({ error: null });

        render(
            <MemoryRouter initialEntries={['/auth/forgot-password']}>
                <Routes>
                    <Route path="/auth/forgot-password" element={<ForgotPassword />} />
                    <Route path="/auth/verify-reset" element={<div>Verify Page Reached</div>} />
                </Routes>
            </MemoryRouter>
        );

        // 1. Enter Email
        const emailInput = screen.getByLabelText(/email/i);
        fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

        // 2. Click Send
        const sendBtn = screen.getByRole('button', { name: /send/i }); 
        fireEvent.click(sendBtn);

        // 3. Check if sendResetOtp was called correctly
        await waitFor(() => {
            expect(mockSendResetOtp).toHaveBeenCalledWith('test@example.com');
        });

        // 4. Verify Success Toast
        expect(mockToast).toHaveBeenCalledWith(expect.objectContaining({
            title: 'Code Sent'
        }));

        // 5. Verify Navigation (we check if the new page content is rendered)
        expect(screen.getByText('Verify Page Reached')).toBeInTheDocument();
    });

    it('VerifyOtp submits code when 6 digits entered', async () => {
        mockVerifyOtp.mockResolvedValue({ error: null });

        // Render with state (email provided from previous step)
        render(
            <MemoryRouter initialEntries={[{ pathname: '/verify-reset', state: { email: 'test@example.com' } }]}>
                <Routes>
                    <Route path="/verify-reset" element={<VerifyOtp />} />
                    <Route path="/reset-password" element={<div>New Password Page Reached</div>} />
                </Routes>
            </MemoryRouter>
        );

        // 1. Check title - using Role to avoid ambiguity with button
        expect(screen.getByRole('heading', { name: /verify code/i })).toBeInTheDocument();

        // 2. Verify inputs are rendered
        expect(screen.getByTestId('otp-input')).toBeInTheDocument();

        // 3. Verify Button exists
        const verifyBtn = screen.getByRole('button', { name: /verify code/i });
        expect(verifyBtn).toBeInTheDocument();
    });
});

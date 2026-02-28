import { createClient } from '@supabase/supabase-js';
import { Database } from './types';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    console.error("Missing Supabase environment variables. Please check your .env file.");
}

// Ensure the URL is valid, otherwise Supabase's internal "new URL()" parses will throw 
// a fatal TypeError and crash the entire React application bundle (white screen).
const validUrl = supabaseUrl?.startsWith('http')
    ? supabaseUrl
    : 'https://placeholder-url.supabase.co';

export const supabase = createClient<Database>(
    validUrl,
    supabaseAnonKey || "placeholder-key"
);

/**
 * SUPABASE COMPATIBILITY LAYER (MOCK)
 * Used to resolve legacy imports while the system transitions to local-first SaaS.
 * This mock supports infinite chaining to prevent "is not a function" errors.
 */

const mockPromise = () => {
    const p = Promise.resolve({ data: null, error: null }) as any;
    const chain = () => {
        const proxy: any = new Proxy(() => { }, {
            get: (_, prop) => {
                if (prop === 'then') return p.then.bind(p);
                if (prop === 'catch') return p.catch.bind(p);
                if (prop === 'finally') return p.finally.bind(p);
                return proxy;
            },
            apply: () => proxy
        });
        return proxy;
    };
    return chain();
};

export const supabase = {
    auth: {
        getSession: async () => ({ data: { session: null }, error: null }),
        getUser: async () => ({ data: { user: null }, error: null }),
        onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => { } } } }),
        signInWithPassword: async () => ({ data: { user: null, session: null }, error: null }),
        signUp: async () => ({ data: { user: null, session: null }, error: null }),
        signOut: async () => ({ error: null }),
        updateUser: async () => ({ data: { user: null }, error: null }),
        resetPasswordForEmail: async () => ({ data: null, error: null }),
    },
    from: () => {
        const chain = {
            select: () => chain,
            insert: () => chain,
            update: () => chain,
            delete: () => chain,
            upsert: () => chain,
            eq: () => chain,
            neq: () => chain,
            gt: () => chain,
            gte: () => chain,
            lt: () => chain,
            lte: () => chain,
            like: () => chain,
            ilike: () => chain,
            is: () => chain,
            in: () => chain,
            contains: () => chain,
            containedBy: () => chain,
            rangeGt: () => chain,
            rangeGte: () => chain,
            rangeLt: () => chain,
            rangeLte: () => chain,
            rangeAdjacent: () => chain,
            overlaps: () => chain,
            match: () => chain,
            not: () => chain,
            or: () => chain,
            filter: () => chain,
            order: () => chain,
            limit: () => chain,
            range: () => chain,
            abortSignal: () => chain,
            single: async () => ({ data: null, error: null }),
            maybeSingle: async () => ({ data: null, error: null }),
            csv: () => chain,
            then: (cb: any) => Promise.resolve({ data: [], error: null }).then(cb),
        };
        return chain;
    },
    functions: {
        invoke: async () => ({ data: { success: true }, error: null }),
    },
    channel: (name: string) => {
        const mockChannel = {
            on: (type: string, filter: any, callback: any) => mockChannel,
            subscribe: () => ({ unsubscribe: () => { } }),
        };
        return mockChannel;
    },
    removeChannel: async () => ({ error: null }),
    removeAllChannels: async () => ({ error: null }),
    getChannels: () => [],
    storage: {
        from: () => ({
            upload: async () => ({ data: null, error: null }),
            download: async () => ({ data: null, error: null }),
            getPublicUrl: () => ({ data: { publicUrl: '' } }),
            list: async () => ({ data: [], error: null }),
            remove: async () => ({ data: [], error: null }),
        }),
    },
    rpc: async () => ({ data: null, error: null }),
};

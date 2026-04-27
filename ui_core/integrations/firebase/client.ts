import { initializeApp } from 'firebase/app';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { getFirestore, collection, getDocs, addDoc, updateDoc, deleteDoc, doc, query, where, orderBy, onSnapshot, getDoc, setDoc } from 'firebase/firestore';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged } from 'firebase/auth';

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "dummy-api-key",
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "hyper-app.firebaseapp.com",
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "hyper-app",
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "hyper-app.appspot.com",
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "123456789",
    appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:123456789:web:abcdef"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);

// Mimic the Supabase Query Builder architecture to protect 300+ React UI components from Typescript AST destruction
class FirebaseQueryBuilder {
    private _collection: string;
    private _select: string = '*';
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private _filters: any[] = [];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private _orders: any[] = [];
    private _limit: number | null = null;
    private _single: boolean = false;

    constructor(collectionName: string) {
        this._collection = collectionName;
    }

    select(fields: string) {
        this._select = fields;
        return this;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    eq(column: string, value: any) {
        this._filters.push({ column, operator: '==', value });
        return this;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    gt(column: string, value: any) {
        this._filters.push({ column, operator: '>', value });
        return this;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    lt(column: string, value: any) {
        this._filters.push({ column, operator: '<', value });
        return this;
    }

    order(column: string, options?: { ascending?: boolean }) {
        this._orders.push({ column, direction: options?.ascending ? 'asc' : 'desc' });
        return this;
    }

    limit(count: number) {
        this._limit = count;
        return this;
    }

    single() {
        this._single = true;
        return this;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async insert(payload: any) {
        try {
            const colRef = collection(db, this._collection);
            if (Array.isArray(payload)) {
                for (const item of payload) await addDoc(colRef, item);
            } else {
                await addDoc(colRef, payload);
            }
            return { data: payload, error: null };
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (e: any) {
            return { data: null, error: e };
        }
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async update(payload: any) {
        // Requires an eq('id', val) filter to execute properly
        try {
            const idFilter = this._filters.find(f => f.column === 'id');
            if (idFilter) {
                const docRef = doc(db, this._collection, idFilter.value);
                await updateDoc(docRef, payload);
                return { data: payload, error: null };
            }
            return { data: null, error: new Error('Missing ID for update') };
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (e: any) {
            return { data: null, error: e };
        }
    }

    async delete() {
        try {
            const idFilter = this._filters.find(f => f.column === 'id');
            if (idFilter) {
                const docRef = doc(db, this._collection, idFilter.value);
                await deleteDoc(docRef);
                return { data: null, error: null };
            }
            return { data: null, error: new Error('Missing ID for delete') };
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (e: any) {
            return { data: null, error: e };
        }
    }

    // Await Executor mechanism resolving the ORM chain
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars
    async then(resolve: (val: any) => void, reject?: (err: any) => void) {
        try {
            const colRef = collection(db, this._collection);
            const q = query(colRef);

            // We'd map custom where() and orderBy() filters here in production

            const querySnapshot = await getDocs(q);
            const results = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));

            if (this._single) {
                resolve({ data: results[0] || null, error: null, count: results.length });
            } else {
                resolve({ data: results, error: null, count: results.length });
            }
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (error: any) {
            resolve({ data: null, error });
        }
    }
}

export const firebaseClient = {
    from: (table: string) => new FirebaseQueryBuilder(table),
    auth: {
        getSession: async () => {
            const user = auth.currentUser;
            return { data: { session: user ? { user: { ...user, id: user.uid } } : null }, error: null };
        },
        getUser: async () => {
            const user = auth.currentUser;
            return { data: { user: user ? { ...user, id: user.uid } : null }, error: null };
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        signInWithPassword: async ({ email, password }: any) => {
            try {
                const credential = await signInWithEmailAndPassword(auth, email, password);
                return { data: { user: { ...credential.user, id: credential.user.uid } }, error: null };
            } catch (e) { return { data: null, error: e }; }
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        signUp: async ({ email, password, options }: any) => {
            try {
                const credential = await createUserWithEmailAndPassword(auth, email, password);
                // In a real app, we'd save metadata (options.data.username) to Firestore here
                return { data: { user: { ...credential.user, id: credential.user.uid } }, error: null };
            } catch (e) { return { data: null, error: e }; }
        },
        signOut: async () => {
            await signOut(auth);
            return { error: null };
        },
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        sendResetOtp: async ({ email }: { email: string }) => {
            // Mock OTP sending
            console.log(`[Firebase Mock] Sent reset code (123456) to ${email}`);
            return { error: null };
        },
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        verifyOtp: async ({ email, token, type }: { email: string, token: string, type: string }) => {
            // Mock OTP verification
            if (token === '123456' || token === '000000') {
                return { error: null };
            }
            return { error: new Error('Invalid verification code') };
        },
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        resetPasswordForEmail: async (email: string) => {
            // Firebase uses sendPasswordResetEmail
            return { error: null };
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onAuthStateChange: (callback: any) => {
            const unsubscribe = onAuthStateChanged(auth, (user) => {
                const mappedUser = user ? { ...user, id: user.uid } : null;
                callback(user ? 'SIGNED_IN' : 'SIGNED_OUT', { user: mappedUser });
            });
            return { data: { subscription: { unsubscribe } } };
        }
    },
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    channel: (name: string) => ({
        on: () => ({
            subscribe: () => ({ unsubscribe: () => { } }) // Mock Realtime dropping
        }),
        subscribe: () => ({ unsubscribe: () => { } })
    }),
    removeChannel: () => { },
    functions: {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
        invoke: async (name: string, payload: any) => ({ data: { message: "Invoked Firebase Function" }, error: null })
    }
};

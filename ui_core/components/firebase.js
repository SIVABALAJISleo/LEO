import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
    getAuth,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyD8w4toy_YmswN_LRHnWobesKQZdjib7bo",
    authDomain: "hyper-1618e.firebaseapp.com",
    projectId: "hyper-1618e",
    storageBucket: "hyper-1618e.firebasestorage.app",
    messagingSenderId: "940534680027",
    appId: "1:940534680027:web:2ec8627b8dc51f2fe0fffe",
    measurementId: "G-8MGSTSQ45K"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export {
    auth,
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    onAuthStateChanged
};

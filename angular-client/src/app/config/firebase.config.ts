// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyD5u3QaEWZXboUOeU1w-ETRf0EMyGESAYs",
  authDomain: "coursewagon.firebaseapp.com",
  projectId: "coursewagon",
  storageBucket: "coursewagon.firebasestorage.app",
  messagingSenderId: "623320490056",
  appId: "1:623320490056:web:e66cd9f8b82dd885d2f87d"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Google Auth Provider
export const googleProvider = new GoogleAuthProvider();

// Configure Google provider
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

export default app;

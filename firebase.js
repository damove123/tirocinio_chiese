// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyDnLeO1sx8-s8ieJfM0OtZWLy8ayFgE_j0",
    authDomain: "floor-tiles-vpc.firebaseapp.com",
    databaseURL: "https://floor-tiles-vpc-default-rtdb.europe-west1.firebasedatabase.app",
    projectId: "floor-tiles-vpc",
    storageBucket: "floor-tiles-vpc.appspot.com",
    messagingSenderId: "621156227751",
    appId: "1:621156227751:web:2ef44726ea870a574a5982",
    measurementId: "G-LWZC7F6NVN"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
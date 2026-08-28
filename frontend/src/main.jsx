import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import App from './App';
import './styles.css';
import './monefy-inspired.css';
import './quick-entry.css';
import './bento.css';
import './mobile.css';
import './banking.css';
import './learn.css';
import './navigation.css';
import './navigation-overrides.css';
import './profile.css';
import './profile-overrides.css';
import './brand.css';

createRoot(document.getElementById('root')).render(<React.StrictMode><BrowserRouter><AuthProvider><App /></AuthProvider></BrowserRouter></React.StrictMode>);

import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Budgets from './pages/Budgets';
import Insights from './pages/Insights';
import Banking from './pages/Banking';
import Learn from './pages/Learn';
import Profile from './pages/Profile';
import { AppLockScreen } from './components/AppLock';

export default function App() {
  const { user, appLocked } = useAuth();
  if (!user) return <Routes><Route path="*" element={<AuthPage />} /></Routes>;
  if (appLocked) return <AppLockScreen/>;
  return <Layout><Routes><Route path="/" element={<Dashboard />} /><Route path="/banking" element={<Banking />} /><Route path="/transactions" element={<Transactions />} /><Route path="/budgets" element={<Budgets />} /><Route path="/insights" element={<Insights />} /><Route path="/profile" element={<Profile />} /><Route path="/learn/:sectionSlug" element={<Learn />} /><Route path="*" element={<Navigate to="/" />} /></Routes></Layout>;
}

import { useState } from 'react';
import { LockKeyhole, ShieldCheck, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function AppLockScreen() {
  const [pin,setPin]=useState(''); const [error,setError]=useState(''); const [loading,setLoading]=useState(false); const {unlock,logout}=useAuth();
  const submit=async(event)=>{event.preventDefault();setLoading(true);setError('');try{await unlock(pin);}catch{setError('Incorrect PIN. Try again.');setPin('');}finally{setLoading(false);}};
  return <div className="app-lock-screen"><form onSubmit={submit}><span><LockKeyhole/></span><p className="eyebrow">NORTHSTAR LOCK</p><h1>Your finances are protected</h1><p>Enter your app PIN to continue.</p><input autoFocus aria-label="App lock PIN" type="password" inputMode="numeric" pattern="\d{4,8}" maxLength="8" value={pin} onChange={event=>setPin(event.target.value.replace(/\D/g,''))} placeholder="••••" required/>{error?<div className="error">{error}</div>:null}<button className="primary" disabled={loading}>{loading?'Checking…':'Unlock'}</button><button type="button" className="text-button" onClick={logout}>Sign out instead</button></form></div>;
}

export function AppLockSettings({onClose}) {
  const [pin,setPin]=useState(''); const [confirm,setConfirm]=useState(''); const [error,setError]=useState(''); const [loading,setLoading]=useState(false); const {user,setupLock,disableLock,lockNow}=useAuth();
  const submit=async(event)=>{event.preventDefault();if(pin!==confirm){setError('PINs do not match.');return;}setLoading(true);try{await setupLock(pin);onClose();}catch{setError('Could not enable app lock.');}finally{setLoading(false);}};
  return <div className="quick-entry-backdrop"><section className="lock-settings" role="dialog" aria-modal="true"><button className="icon-button close-lock" onClick={onClose} aria-label="Close"><X/></button><span className="security-icon"><ShieldCheck/></span><p className="eyebrow">SECURITY</p><h2>App lock</h2>{user.app_lock_enabled?<><p>App lock is enabled. Lock Northstar whenever you step away.</p><button className="primary" onClick={()=>{onClose();lockNow();}}>Lock now</button><button className="danger-button" onClick={async()=>{await disableLock();onClose();}}>Disable app lock</button></>:<form onSubmit={submit}><p>Create a 4–8 digit PIN. It is securely hashed on the server.</p><label>New PIN<input type="password" inputMode="numeric" pattern="\d{4,8}" maxLength="8" required value={pin} onChange={event=>setPin(event.target.value.replace(/\D/g,''))}/></label><label>Confirm PIN<input type="password" inputMode="numeric" pattern="\d{4,8}" maxLength="8" required value={confirm} onChange={event=>setConfirm(event.target.value.replace(/\D/g,''))}/></label>{error?<div className="error">{error}</div>:null}<button className="primary" disabled={loading}>{loading?'Saving…':'Enable app lock'}</button></form>}</section></div>;
}

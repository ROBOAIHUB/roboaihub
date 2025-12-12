import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import api from '../services/api';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const isActive = (path) => location.pathname === path;

    const [notifications, setNotifications] = useState([]);
    const [showNotifDropdown, setShowNotifDropdown] = useState(false);

    useEffect(() => {
        if (user) {
            fetchNotifications();
            const interval = setInterval(fetchNotifications, 60000); // Poll every 60s
            return () => clearInterval(interval);
        }
    }, [user]);

    const fetchNotifications = async () => {
        try {
            const res = await api.get('/users/notifications');
            setNotifications(res.data);
        } catch (err) {
            console.error("Failed to fetch notifications", err);
        }
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-space-800/90 backdrop-blur-md border-b border-blue-900 shadow-neon-blue">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/dashboard" className="text-2xl font-tech font-bold text-neon-blue text-glow-blue">
                            EMS <span className="text-neon-red">V2.0</span>
                        </Link>
                        <div className="hidden md:block ml-10 flex items-baseline space-x-4">
                            <Link
                                to="/dashboard"
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive('/dashboard') ? 'bg-blue-900/50 text-neon-blue border border-neon-blue' : 'text-starlight hover:text-neon-blue'}`}
                            >
                                Dashboard
                            </Link>
                            <Link
                                to="/reporting"
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive('/reporting') ? 'bg-blue-900/50 text-neon-blue border border-neon-blue' : 'text-starlight hover:text-neon-blue'}`}
                            >
                                Reporting
                            </Link>
                            {user?.roles?.includes('Admin') && (
                                <Link
                                    to="/team"
                                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive('/team') ? 'bg-blue-900/50 text-neon-blue border border-neon-blue' : 'text-starlight hover:text-neon-blue'}`}
                                >
                                    Team View
                                </Link>
                            )}
                            {(user?.roles?.includes('Admin') || user?.roles?.includes('HR')) && (
                                <Link
                                    to="/admin"
                                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive('/admin') ? 'bg-red-900/30 text-neon-red border border-neon-red' : 'text-starlight hover:text-neon-red'}`}
                                >
                                    Admin Panel
                                </Link>
                            )}
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        {/* Notification Bell */}
                        <div className="relative">
                            <button
                                onClick={() => setShowNotifDropdown(!showNotifDropdown)}
                                className="text-starlight hover:text-neon-blue relative p-1"
                            >
                                <span className="text-xl">🔔</span>
                                {notifications.length > 0 && (
                                    <span className="absolute -top-1 -right-1 bg-neon-red text-white text-[10px] font-bold px-1.5 rounded-full shadow-[0_0_5px_rgba(255,0,0,0.8)]">
                                        {notifications.length}
                                    </span>
                                )}
                            </button>

                            {showNotifDropdown && (
                                <div className="absolute right-0 mt-2 w-80 bg-space-900 border border-blue-800 rounded shadow-[0_0_20px_rgba(0,0,0,0.8)] overflow-hidden z-[60]">
                                    <div className="p-3 border-b border-blue-900 font-bold text-neon-blue">Notifications</div>
                                    <div className="max-h-64 overflow-y-auto">
                                        {notifications.length === 0 ? (
                                            <div className="p-4 text-xs text-starlight opacity-50 text-center">No new notifications.</div>
                                        ) : (
                                            notifications.map((n, i) => (
                                                <div key={i} className="p-3 border-b border-blue-900/30 hover:bg-white/5 transition">
                                                    <p className="text-sm text-starlight">{n.message}</p>
                                                    <p className="text-[10px] text-neon-blue mt-1 opacity-70">{n.date}</p>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="hidden md:block text-right">
                            <p className="text-sm font-bold text-neon-blue">{user?.full_name}</p>
                            <p className="text-xs text-starlight opacity-70">{user?.roles?.[0]}</p>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="px-3 py-1 border border-neon-red text-neon-red text-xs rounded hover:bg-neon-red hover:text-white transition-all uppercase tracking-wider"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;

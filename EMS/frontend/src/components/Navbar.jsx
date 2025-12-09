import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const isActive = (path) => location.pathname === path;

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

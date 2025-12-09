import { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

const Layout = () => {
    const { logout, user } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    // Theme Configuration
    const themeConfig = {
        "Iron Man": {
            bg: "/iron-man-bg.png",
            overlay: "bg-red-900/30",
            border: "border-yellow-500/50",
            textStart: "text-yellow-400",
            textEnd: "text-red-500",
            shadow: "shadow-red-500/50"
        },
        "Captain America": {
            bg: "/avengers-bg.png",
            overlay: "bg-blue-900/40",
            border: "border-blue-500/50",
            textStart: "text-blue-400",
            textEnd: "text-white",
            shadow: "shadow-blue-500/50"
        },
        "Dr. Doom": {
            bg: "/dr-doom-bg.png",
            overlay: "bg-green-950/60",
            border: "border-green-500/50",
            textStart: "text-green-400",
            textEnd: "text-gray-300",
            shadow: "shadow-green-500/50"
        },
        "Riri Williams": {
            bg: "/iron-man-bg.png", // Reuse Iron Man for now or generic
            overlay: "bg-pink-900/40",
            border: "border-pink-500/50",
            textStart: "text-pink-400",
            textEnd: "text-yellow-400",
            shadow: "shadow-pink-500/50"
        },
        "Dr. Strange": {
            bg: "/dr-strange-bg.png",
            overlay: "bg-purple-900/40",
            border: "border-orange-500/50",
            textStart: "text-orange-400",
            textEnd: "text-purple-400",
            shadow: "shadow-orange-500/50"
        },
        "Hawkeye": {
            bg: "/hawkeye-bg.png",
            overlay: "bg-purple-950/50",
            border: "border-purple-500/50",
            textStart: "text-purple-400",
            textEnd: "text-gray-400",
            shadow: "shadow-purple-500/50"
        },
        "Spider Man": {
            bg: "/spiderman-bg.png",
            overlay: "bg-red-900/40",
            border: "border-blue-500/50",
            textStart: "text-red-500",
            textEnd: "text-blue-500",
            shadow: "shadow-red-500/50"
        },
        "Hulk": {
            bg: "/hulk-bg.png",
            overlay: "bg-green-900/30",
            border: "border-purple-500/50",
            textStart: "text-green-500",
            textEnd: "text-purple-600",
            shadow: "shadow-green-500/50"
        },
        "Falcon": {
            bg: "/falcon-bg.png",
            overlay: "bg-slate-900/40",
            border: "border-red-500/50",
            textStart: "text-gray-200",
            textEnd: "text-red-500",
            shadow: "shadow-red-500/50"
        },
        "Vision": {
            bg: "/vision-bg.png",
            overlay: "bg-teal-900/40",
            border: "border-yellow-500/50",
            textStart: "text-teal-400",
            textEnd: "text-yellow-500",
            shadow: "shadow-teal-500/50"
        },
        "Ant Man": {
            bg: "/antman-bg.png",
            overlay: "bg-red-950/50",
            border: "border-gray-500/50",
            textStart: "text-red-500",
            textEnd: "text-gray-400",
            shadow: "shadow-red-500/50"
        },
        "Star Lord": {
            bg: "/starlord-bg.png",
            overlay: "bg-purple-900/30",
            border: "border-yellow-600/50",
            textStart: "text-yellow-400",
            textEnd: "text-purple-400",
            shadow: "shadow-yellow-500/50"
        },
        "Avengers": { // Fallback
            bg: "/avengers-bg.png",
            overlay: "bg-space-900/40",
            border: "border-blue-900/50",
            textStart: "text-neon-blue",
            textEnd: "text-neon-blue",
            shadow: "shadow-neon-blue"
        }
    };

    const currentTheme = themeConfig[user?.avenger_character] || themeConfig["Avengers"];

    return (
        <div className="min-h-screen relative font-mono text-starlight overflow-x-hidden">
            {/* Dynamic Background Layer */}
            <div className="fixed inset-0 z-0">
                <img src={currentTheme.bg} alt="Background" className="w-full h-full object-cover transition-all duration-1000" />
                <div className={`absolute inset-0 backdrop-blur-[2px] transition-colors duration-1000 ${currentTheme.overlay}`}></div>
            </div>

            {/* Content Layer */}
            <div className="relative z-10 min-h-screen flex flex-col">
                {/* HUD Header (Minimal) */}
                <div className="p-4 flex flex-col md:flex-row justify-between items-center gap-4">
                    <Link to="/dashboard" className="text-2xl font-tech font-bold text-transparent animate-glow-cycle drop-shadow-lg">
                        EMS V2.0
                    </Link>

                    <div className="flex items-center gap-4 bg-space-800/80 backdrop-blur-md px-4 py-2 rounded-full border border-blue-900/50 shadow-neon-blue">
                        <span className="text-xs text-neon-blue font-bold hidden sm:block border-r border-blue-900 pr-3 mr-1">{user?.name || user?.full_name}</span>

                        {/* Employee Navigation Links */}
                        {!user?.roles?.includes('Admin') ? (
                            <div className="flex items-center gap-4 text-xs font-bold tracking-wider">
                                <Link to="/roles" className={`hover:text-neon-blue transition ${location.pathname === '/roles' ? 'text-neon-blue border-b border-neon-blue' : 'text-starlight'}`}>
                                    ROLES
                                </Link>
                                <Link to="/tasks" className={`hover:text-neon-blue transition ${location.pathname === '/tasks' ? 'text-neon-blue border-b border-neon-blue' : 'text-starlight'}`}>
                                    TASKS
                                </Link>
                                <div className="relative">
                                    <button
                                        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                        className={`hover:text-neon-blue transition flex items-center gap-1 ${isDropdownOpen ? 'text-neon-blue' : ''}`}
                                    >
                                        REPORTING <span className="text-[10px]">{isDropdownOpen ? '▲' : '▼'}</span>
                                    </button>

                                    {isDropdownOpen && (
                                        <>
                                            {/* Invisible Overlay to close on outside click */}
                                            <div className="fixed inset-0 z-40 cursor-default" onClick={() => setIsDropdownOpen(false)}></div>

                                            <div className="absolute top-full right-0 mt-2 w-48 bg-space-900 border border-blue-800 rounded-xl shadow-[0_0_20px_rgba(0,100,255,0.2)] overflow-hidden z-50">
                                                <Link
                                                    to="/reporting"
                                                    onClick={() => setIsDropdownOpen(false)}
                                                    className="block px-4 py-2 hover:bg-blue-900/30 text-starlight hover:text-neon-blue transition"
                                                >
                                                    Daily Report
                                                </Link>
                                                {user?.is_mentor && (
                                                    <Link
                                                        to="/mentor-reporting"
                                                        onClick={() => setIsDropdownOpen(false)}
                                                        className="block px-4 py-2 hover:bg-blue-900/30 text-starlight hover:text-neon-blue transition"
                                                    >
                                                        Mentorship Report
                                                    </Link>
                                                )}
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>
                        ) : (
                            /* Admin Navigation Links */
                            <div className="flex items-center gap-4 text-xs font-bold tracking-wider">
                                <Link to="/admin" className={`hover:text-neon-red transition ${location.pathname === '/admin' ? 'text-neon-red border-b border-neon-red' : 'text-starlight'}`}>
                                    ADMIN CENTER
                                </Link>
                            </div>
                        )}

                        <div className="h-4 w-px bg-blue-900/50 mx-2"></div>

                        <button
                            onClick={handleLogout}
                            className="text-xs text-neon-red hover:text-white transition font-bold tracking-wider"
                        >
                            LOGOUT
                        </button>
                    </div>
                </div>

                {/* Main Content Area */}
                <main className="flex-grow max-w-7xl mx-auto w-full p-4 sm:p-6 lg:p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default Layout;

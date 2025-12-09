import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const userData = await login(username, password);
            // Check for Admin role (Case sensitive, usually 'Admin')
            if (userData.roles && userData.roles.includes('Admin')) {
                navigate('/admin');
            } else {
                navigate('/dashboard');
            }
        } catch (err) {
            setError('Access Denied');
        }
    };

    return (
        <div className="flex h-screen w-screen items-center justify-center relative overflow-hidden bg-cover bg-center" style={{ backgroundImage: "url('/avengers-bg.png')" }}>
            {/* Dark Overlay for better contrast */}
            <div className="absolute inset-0 bg-space-900/60 backdrop-blur-[2px]"></div>

            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                className="z-10 w-full max-w-5xl bg-space-800/90 backdrop-blur-xl border border-neon-blue/50 rounded-2xl shadow-[0_0_50px_rgba(0,242,255,0.3)] flex flex-col md:flex-row overflow-hidden"
            >
                {/* Left Side - Quote */}
                <div className="w-full md:w-1/2 p-12 bg-blue-900/40 border-b md:border-b-0 md:border-r border-neon-blue/30 flex items-center justify-center relative">
                    <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
                    <div className="relative z-10">
                        <h1 className="text-4xl md:text-5xl font-tech font-bold text-transparent animate-glow-cycle leading-tight mb-6 drop-shadow-2xl">
                            "Excellence is a habit—build it daily."
                        </h1>
                        <div className="w-24 h-1 bg-neon-red shadow-[0_0_10px_red]"></div>
                    </div>
                </div>

                {/* Right Side - Login Form */}
                <div className="w-full md:w-1/2 p-8 md:p-12">
                    <h2 className="text-4xl font-tech font-bold text-center text-neon-blue text-glow-blue mb-2">
                        EMS <span className="text-neon-red">LOGIN</span>
                    </h2>
                    <p className="text-center text-starlight mb-8 tracking-widest text-sm">SECURE ACCESS TERMINAL</p>

                    {error ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="mb-6 p-6 bg-black/80 border border-neon-red rounded-xl relative overflow-hidden text-center"
                        >
                            {/* Robotic glow effect */}
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-neon-red to-transparent animate-scan-slow"></div>

                            <div className="flex flex-col items-center gap-4">
                                {/* Simple CSS Robot Head */}
                                <div className="w-16 h-16 border-2 border-neon-red rounded-lg relative flex items-center justify-center bg-gray-900 shadow-[0_0_15px_rgba(255,0,0,0.5)]">
                                    <div className="w-4 h-4 rounded-full bg-neon-red shadow-[0_0_10px_red] animate-ping absolute top-4 left-3"></div>
                                    <div className="w-4 h-4 rounded-full bg-neon-red shadow-[0_0_10px_red] animate-ping absolute top-4 right-3"></div>
                                    <div className="w-8 h-1 bg-neon-red absolute bottom-4 shadow-[0_0_5px_red]"></div>
                                </div>

                                <p className="font-mono text-neon-red text-lg italic">
                                    "ACCESS DENIED. SYSTEM LOCKED."
                                </p>

                                <div className="bg-red-900/20 p-3 rounded border border-red-500/50 w-full">
                                    <p className="text-starlight text-sm mb-2">To restore access:</p>
                                    <a
                                        href="http://www.roboaihub.com"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-neon-blue hover:text-white font-bold tracking-wider hover:underline transition-all"
                                    >
                                        VISIT WWW.ROBOAIHUB.COM
                                    </a>
                                    <p className="text-xs text-starlight/70 mt-1">to get connected with us</p>
                                </div>

                                <button
                                    onClick={() => setError('')}
                                    className="text-xs text-gray-500 hover:text-white mt-2 uppercase tracking-widest"
                                >
                                    [ RETRY SEQUENCE ]
                                </button>
                            </div>
                        </motion.div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-neon-blue text-sm font-bold mb-2 uppercase tracking-wider">ID / Username</label>
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="w-full bg-space-900 border border-blue-900 text-neon-blue p-3 rounded-lg focus:outline-none focus:border-neon-blue focus:shadow-neon-blue transition-all duration-300 placeholder-blue-900/50"
                                    placeholder="ENTER ID"
                                />
                            </div>
                            <div>
                                <label className="block text-neon-blue text-sm font-bold mb-2 uppercase tracking-wider">Password</label>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-space-900 border border-blue-900 text-neon-blue p-3 rounded-lg focus:outline-none focus:border-neon-blue focus:shadow-neon-blue transition-all duration-300 placeholder-blue-900/50"
                                    placeholder="••••••••"
                                />
                            </div>

                            <button
                                type="submit"
                                className="w-full py-4 bg-gradient-to-r from-blue-900 to-blue-800 border border-neon-blue text-neon-blue font-bold uppercase tracking-[0.2em] rounded-lg hover:bg-neon-blue hover:text-space-900 hover:shadow-[0_0_30px_rgba(0,242,255,0.6)] transition-all duration-300"
                            >
                                Authenticate
                            </button>
                        </form>
                    )}
                </div>
            </motion.div>
        </div>
    );
};

export default Login;

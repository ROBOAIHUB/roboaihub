import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const Dashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    return (
        <div className="relative min-h-[80vh] flex flex-col items-center justify-start pt-10">

            {/* Standard Dashboard Grid REMOVED - Using Top Panel Navigation */}
            <div className="hidden"></div>

            {/* Holographic Overlay Layer */}
            <div className="fixed inset-0 z-0 flex flex-col items-center justify-center pointer-events-none overflow-hidden pb-0">

                {/* Text Container - Centered */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5, duration: 1 }}
                    className="text-center z-20"
                >
                    <motion.div
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 3, repeat: Infinity }}
                        className="text-xl md:text-3xl tracking-[1em] mb-6 uppercase font-bold text-neon-blue drop-shadow-[0_0_10px_rgba(0,242,255,0.8)]"
                    >
                        Identity Verified
                    </motion.div>
                    <h1 className="text-6xl md:text-9xl font-tech font-bold uppercase tracking-widest text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.8)]">
                        {user?.name || user?.full_name || "OPERATIVE"}
                    </h1>
                    <h2 className="text-2xl md:text-4xl font-bold font-mono tracking-[0.3em] uppercase mt-6 px-8 py-3 rounded-lg border border-blue-500/30 backdrop-blur-md text-starlight bg-space-800/80 shadow-[0_0_20px_rgba(0,100,255,0.3)]">
                        {user?.designation || "UNKNOWN RANK"}
                    </h2>
                </motion.div>
            </div>
        </div>
    );
};

export default Dashboard;

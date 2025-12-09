import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

const Roles = () => {
    const { user } = useAuth();

    return (
        <div className="max-w-4xl mx-auto text-center pt-10">
            <h2 className="text-3xl font-tech text-neon-blue text-glow-blue mb-8">
                OPERATIVE <span className="text-neon-red">PROFILE</span>
            </h2>

            <div className="bg-space-800 border-2 border-neon-blue p-8 rounded-2xl shadow-[0_0_30px_rgba(0,242,255,0.15)] inline-block min-w-[300px] max-w-full">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full mx-auto mb-6 flex items-center justify-center text-4xl font-bold text-white shadow-lg">
                    {user?.name?.charAt(0) || user?.full_name?.charAt(0)}
                </div>

                <h3 className="text-2xl text-white font-bold mb-2">{user?.name || user?.full_name}</h3>
                <p className="text-neon-blue mb-6 tracking-widest uppercase text-sm">{user?.designation || "Operative"}</p>

                <div className="h-px bg-blue-900/50 w-full mb-6"></div>

                <h4 className="text-starlight text-sm uppercase tracking-wider mb-4 opacity-70">Assigned Responsibilities</h4>

                <div className="flex flex-wrap justify-center gap-3">
                    {user?.roles?.map((role, idx) => (
                        <motion.span
                            key={idx}
                            initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: idx * 0.1 }}
                            className="px-4 py-2 bg-blue-900/30 border border-blue-500/50 rounded-full text-neon-blue text-sm font-bold shadow-[0_0_10px_rgba(0,100,255,0.2)]"
                        >
                            {role}
                        </motion.span>
                    ))}
                    {(!user?.roles || user?.roles.length === 0) && (
                        <span className="text-starlight opacity-50 italic">No specific roles assigned.</span>
                    )}
                </div>

                {user?.is_mentor && (
                    <div className="mt-8 pt-6 border-t border-red-900/30">
                        <span className="px-6 py-2 bg-red-900/20 border border-neon-red text-neon-red rounded-full text-xs font-bold tracking-widest uppercase shadow-[0_0_15px_rgba(255,0,0,0.3)] animate-pulse">
                            MENTOR CLEARANCE ACTIVE
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Roles;

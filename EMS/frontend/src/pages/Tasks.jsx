import { useState, useEffect } from 'react';
import api from '../services/api';
import { motion } from 'framer-motion';

const Tasks = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                const res = await api.get('/reports/tasks');
                setTasks(res.data.tasks);
            } catch (err) {
                console.error("Failed to fetch tasks", err);
            } finally {
                setLoading(false);
            }
        };
        fetchTasks();
    }, []);

    return (
        <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-tech text-neon-blue mb-8 text-glow-blue">
                MISSION <span className="text-white">PROTOCOLS</span>
            </h2>

            {loading ? (
                <div className="text-starlight animate-pulse">Scanning Mission Database...</div>
            ) : (
                <div className="grid gap-4">
                    {tasks.map((task, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="p-6 bg-space-800 border border-blue-900 rounded-xl hover:border-neon-blue hover:shadow-neon-blue transition text-starlight backdrop-blur-sm group"
                        >
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-black/30 rounded-full text-neon-blue border border-transparent group-hover:border-neon-blue transition">
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
                                </div>
                                <div className="text-lg font-mono">{task}</div>
                            </div>
                        </motion.div>
                    ))}

                    {tasks.length === 0 && (
                        <div className="p-8 text-center text-starlight opacity-50 border border-dashed border-blue-900 rounded-xl">
                            No active missions assigned for this sector.
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Tasks;

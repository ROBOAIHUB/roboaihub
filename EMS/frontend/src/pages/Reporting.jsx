import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const Reporting = () => {
    const { user } = useAuth();
    const [tasks, setTasks] = useState([]);
    const [reportData, setReportData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [successMsg, setSuccessMsg] = useState('');

    // Initial rows for the report
    const initialRows = [
        { time_slot: '09:30 - 10:30', task: '', description: '', status: 'Pending', remarks: '' },
        { time_slot: '10:30 - 11:30', task: '', description: '', status: 'Pending', remarks: '' },
        { time_slot: '11:30 - 12:30', task: '', description: '', status: 'Pending', remarks: '' },
        { time_slot: '12:30 - 13:30', task: '--- LUNCH BREAK ---', description: 'Locked', status: 'Locked', remarks: 'Locked', locked: true },
        { time_slot: '13:30 - 14:30', task: '', description: '', status: 'Pending', remarks: '' },
        { time_slot: '14:30 - 15:30', task: '', description: '', status: 'Pending', remarks: '' },
        { time_slot: '15:30 - 16:00', task: '--- TEA BREAK ---', description: 'Locked', status: 'Locked', remarks: 'Locked', locked: true },
        { time_slot: '16:00 - 17:30', task: '', description: '', status: 'Pending', remarks: '' },
    ];

    useEffect(() => {
        const fetchTasks = async () => {
            try {
                const res = await api.get('/reports/tasks');
                setTasks(res.data.tasks);
                setReportData(initialRows);
            } catch (err) {
                console.error("Failed to fetch tasks", err);
            } finally {
                setLoading(false);
            }
        };
        fetchTasks();
    }, []);

    const [times, setTimes] = useState({ in_time: '', out_time: '' });

    // Time-based Access Control
    const [isPortalOpen, setIsPortalOpen] = useState(true);

    useEffect(() => {
        const checkTime = () => {
            const currentHour = new Date().getHours();
            // Open between 8 AM (inclusive) and 8 PM (exclusive, so up to 19:59)
            if (currentHour >= 8 && currentHour < 20) {
                setIsPortalOpen(true);
            } else {
                setIsPortalOpen(false);
            }
        };

        checkTime();
    }, []);

    const handleChange = (index, field, value) => {
        if (index === null) {
            setTimes(prev => ({ ...prev, [field]: value }));
        } else {
            const updatedRows = [...reportData];
            updatedRows[index][field] = value;
            setReportData(updatedRows);
        }
    };

    const handleSubmit = async () => {
        // Validation: Check if 'Others' is selected, Description must be filled
        const invalidRows = reportData.filter(row =>
            !row.locked && row.task === 'Others' && !row.description.trim()
        );

        if (invalidRows.length > 0) {
            alert("⚠️ Please provide a DESCRIPTION for all rows where Task is 'Others'.");
            return;
        }

        setSubmitting(true);
        try {
            await api.post('/reports/submit', {
                date: new Date().toISOString().split('T')[0],
                entries: reportData,
                role: 'Office',
                in_time: times.in_time,
                out_time: times.out_time
            });
            setSuccessMsg('Report Submitted Successfully! 🚀');
            setTimeout(() => setSuccessMsg(''), 3000);
        } catch (err) {
            console.error("Submission failed", err);
            alert("Failed to submit report.");
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div className="p-10 text-neon-blue animate-pulse">Initializing Interface...</div>;

    if (!isPortalOpen) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center p-8 border border-red-500/30 bg-black/40 rounded-xl backdrop-blur-md shadow-[0_0_50px_rgba(255,0,0,0.2)]">
                <div className="animate-pulse">
                    <svg className="w-24 h-24 text-red-500 mb-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                    </svg>
                </div>
                <h2 className="text-4xl font-black text-red-500 mb-2 tracking-widest drop-shadow-[0_0_10px_rgba(255,0,0,0.8)]">SYSTEM LOCKED</h2>
                <p className="text-xl text-red-300 font-mono mb-6">REPORTING PORTAL OFFLINE</p>
                <div className="bg-red-900/20 border border-red-500/50 p-4 rounded-lg inline-block">
                    <p className="text-red-400 font-bold">OPERATING HOURS</p>
                    <p className="text-2xl text-white font-mono mt-1">08:00 AM - 08:00 PM</p>
                </div>
                <p className="mt-8 text-gray-400 text-sm">Please return during operational hours to submit your report.</p>
            </div>
        );
    }

    return (
        <div className="">
            <h2 className="text-3xl font-tech text-neon-blue mb-6 drop-shadow-[0_0_10px_rgba(0,242,255,0.3)]">
                DAILY <span className="text-white">REPORTING</span>
            </h2>

            {successMsg && (
                <div className="mb-6 p-4 bg-green-900/30 border border-green-500 text-green-400 rounded-lg font-bold text-center animate-pulse">
                    {successMsg}
                </div>
            )}

            {/* In Time / Out Time Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="p-4 bg-space-900/50 border border-blue-900 rounded-xl relative overflow-hidden group shadow-neon-blue">
                    <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-30 transition-opacity">
                        <svg className="w-16 h-16 text-neon-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path></svg>
                    </div>
                    <label className="block text-neon-blue font-bold mb-2">IN TIME</label>
                    <input
                        type="time"
                        className="w-full bg-black/50 text-starlight p-3 rounded border border-white/10 focus:border-neon-blue focus:shadow-[0_0_10px_#00f2ff] outline-none text-xl font-mono transition"
                        onChange={(e) => handleChange(null, 'in_time', e.target.value)}
                    />
                </div>
                <div className="p-4 bg-space-900/50 border border-blue-900 rounded-xl relative overflow-hidden group shadow-neon-blue">
                    <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-30 transition-opacity">
                        <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                    </div>
                    <label className="block text-white font-bold mb-2">OUT TIME</label>
                    <input
                        type="time"
                        className="w-full bg-black/50 text-starlight p-3 rounded border border-white/10 focus:border-neon-blue focus:shadow-[0_0_10px_#00f2ff] outline-none text-xl font-mono transition"
                        onChange={(e) => handleChange(null, 'out_time', e.target.value)}
                    />
                </div>
            </div>

            <div className="overflow-x-auto rounded-xl border border-blue-900 shadow-neon-blue">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-space-900/80 text-neon-blue uppercase tracking-wider text-sm border-b border-blue-900">
                            <th className="p-4">Time Slot</th>
                            <th className="p-4">Task</th>
                            <th className="p-4">Description</th>
                            <th className="p-4">Status</th>
                            <th className="p-4">Remarks</th>
                        </tr>
                    </thead>
                    <tbody className="bg-black/20 backdrop-blur-sm">
                        {reportData.map((row, index) => (
                            <tr key={index} className="hover:bg-white/5 transition-colors border-b border-white/5">
                                <td className="p-3 font-mono text-sm text-starlight opacity-80">{row.time_slot}</td>

                                <td className="p-3">
                                    {row.locked ? (
                                        <span className="text-gray-500 italic">{row.task}</span>
                                    ) : (
                                        <select
                                            value={row.task}
                                            onChange={(e) => handleChange(index, 'task', e.target.value)}
                                            className="w-full bg-black/40 border border-white/10 text-white rounded p-2 focus:border-neon-blue focus:outline-none disabled:opacity-50"
                                        >
                                            <option value="">Select Task</option>
                                            {tasks.map(t => <option key={t} value={t}>{t}</option>)}
                                        </select>
                                    )}
                                </td>

                                <td className="p-3">
                                    {row.locked ? (
                                        <span className="text-gray-500 italic">{row.description}</span>
                                    ) : (
                                        <input
                                            type="text"
                                            value={row.description}
                                            onChange={(e) => handleChange(index, 'description', e.target.value)}
                                            className={`w-full bg-black/40 border ${row.task === 'Others' && !row.description ? 'border-red-500 animate-pulse' : 'border-white/10'} text-starlight rounded p-2 focus:border-neon-blue focus:outline-none transition-colors disabled:opacity-50`}
                                            placeholder={row.task === 'Others' ? "Required..." : "Details..."}
                                        />
                                    )}
                                </td>

                                <td className="p-3">
                                    {row.locked ? (
                                        <span className="text-gray-500 italic">{row.status}</span>
                                    ) : (
                                        <select
                                            value={row.status}
                                            onChange={(e) => handleChange(index, 'status', e.target.value)}
                                            className="w-full bg-black/40 border border-white/10 text-white rounded p-2 focus:border-neon-blue focus:outline-none disabled:opacity-50"
                                        >
                                            <option value="Pending">Pending</option>
                                            <option value="In Progress">In Progress</option>
                                            <option value="Completed">Completed</option>
                                        </select>
                                    )}
                                </td>

                                <td className="p-3">
                                    {row.locked ? (
                                        <span className="text-gray-500 italic">{row.remarks}</span>
                                    ) : (
                                        <input
                                            type="text"
                                            value={row.remarks}
                                            onChange={(e) => handleChange(index, 'remarks', e.target.value)}
                                            className="w-full bg-black/40 border border-white/10 text-starlight rounded p-2 focus:border-neon-blue focus:outline-none disabled:opacity-50"
                                        />
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="mt-8 flex justify-end items-center">
                <button
                    onClick={handleSubmit}
                    disabled={submitting}
                    className="px-8 py-3 bg-gradient-to-r from-neon-blue to-blue-800 text-white font-bold uppercase tracking-widest rounded shadow-lg hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed disabled:grayscale border border-neon-blue"
                >
                    {submitting ? 'Transmitting...' : 'Submit Report'}
                </button>
            </div>
        </div>
    );
};

export default Reporting;

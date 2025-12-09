import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { motion } from 'framer-motion';

const MentorReporting = () => {
    const { user } = useAuth();
    const [reportData, setReportData] = useState([]);
    const [submitting, setSubmitting] = useState(false);
    const [successMsg, setSuccessMsg] = useState('');

    // Mentor Slots (from SheetManager)
    const initialRows = [
        { time_slot: '08:00 - 09:00', grade: '', topic: '', activity: '', remarks: '' },
        { time_slot: '09:00 - 10:00', grade: '', topic: '', activity: '', remarks: '' },
        { time_slot: '10:00 - 11:00', grade: '', topic: '', activity: '', remarks: '' },
        { time_slot: '11:00 - 12:00', grade: '', topic: '', activity: '', remarks: '' },
        { time_slot: '12:00 - 01:00', grade: '', topic: '', activity: '', remarks: '' },
        { time_slot: '01:00 - 02:00', grade: '', topic: '', activity: '', remarks: '' },
        { time_slot: '02:00 - 03:00', grade: '', topic: '', activity: '', remarks: '' },
    ];

    useEffect(() => {
        setReportData(initialRows);
    }, []);

    const handleChange = (index, field, value) => {
        const updatedRows = [...reportData];
        updatedRows[index][field] = value;
        setReportData(updatedRows);
    };

    const handleSubmit = async () => {
        setSubmitting(true);
        try {
            await api.post('/reports/submit', {
                date: new Date().toISOString().split('T')[0],
                entries: reportData,
                role: 'Mentor'
            });
            setSuccessMsg('Mentor Report Submitted Successfully! 🚀');
            setTimeout(() => setSuccessMsg(''), 3000);
        } catch (err) {
            console.error("Submission failed", err);
            alert("Failed to submit report.");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="">
            <h2 className="text-3xl font-tech text-neon-blue text-glow-blue mb-6">
                MENTOR <span className="text-neon-red">REPORTING</span>
            </h2>

            {successMsg && (
                <motion.div
                    initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
                    className="mb-6 p-4 bg-green-900/30 border border-green-500 text-green-400 rounded-lg font-bold text-center"
                >
                    {successMsg}
                </motion.div>
            )}

            <div className="overflow-x-auto rounded-xl border border-blue-900 shadow-neon-blue">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-space-800 text-neon-blue uppercase tracking-wider text-sm">
                            <th className="p-4 border-b border-blue-900">Time Slot</th>
                            <th className="p-4 border-b border-blue-900">Grade</th>
                            <th className="p-4 border-b border-blue-900">Topic</th>
                            <th className="p-4 border-b border-blue-900">Activity</th>
                            <th className="p-4 border-b border-blue-900">Remarks</th>
                        </tr>
                    </thead>
                    <tbody className="bg-space-900/50">
                        {reportData.map((row, index) => (
                            <tr key={index} className="hover:bg-space-800/50 transition-colors">
                                <td className="p-3 border-b border-blue-900/30 font-mono text-sm text-blue-300">{row.time_slot}</td>

                                <td className="p-3 border-b border-blue-900/30">
                                    <input
                                        type="text" value={row.grade}
                                        onChange={(e) => handleChange(index, 'grade', e.target.value)}
                                        className="w-full bg-space-900 border border-blue-800 text-starlight rounded p-2 focus:border-neon-blue focus:outline-none"
                                    />
                                </td>
                                <td className="p-3 border-b border-blue-900/30">
                                    <input
                                        type="text" value={row.topic}
                                        onChange={(e) => handleChange(index, 'topic', e.target.value)}
                                        className="w-full bg-space-900 border border-blue-800 text-starlight rounded p-2 focus:border-neon-blue focus:outline-none"
                                    />
                                </td>
                                <td className="p-3 border-b border-blue-900/30">
                                    <input
                                        type="text" value={row.activity}
                                        onChange={(e) => handleChange(index, 'activity', e.target.value)}
                                        className="w-full bg-space-900 border border-blue-800 text-starlight rounded p-2 focus:border-neon-blue focus:outline-none"
                                    />
                                </td>
                                <td className="p-3 border-b border-blue-900/30">
                                    <input
                                        type="text" value={row.remarks}
                                        onChange={(e) => handleChange(index, 'remarks', e.target.value)}
                                        className="w-full bg-space-900 border border-blue-800 text-starlight rounded p-2 focus:border-neon-blue focus:outline-none"
                                    />
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="mt-8 flex justify-end">
                <button
                    onClick={handleSubmit}
                    disabled={submitting}
                    className="px-8 py-3 bg-gradient-to-r from-neon-red to-red-700 text-white font-bold uppercase tracking-widest rounded shadow-neon-red hover:scale-105 transition-transform disabled:opacity-50"
                >
                    {submitting ? 'Transmitting...' : 'Submit Report'}
                </button>
            </div>
        </div>
    );
};

export default MentorReporting;

import { useState, useEffect } from 'react';
import api from '../services/api';
import { motion } from 'framer-motion';

const Admin = () => {
    const [employees, setEmployees] = useState({});
    const [loading, setLoading] = useState(true);
    const [formData, setFormData] = useState({
        emp_id: '', name: '', email: '', password: '', designation: '', roles: '', is_mentor: false
    });
    const [msg, setMsg] = useState('');

    // State for Modals
    const [addModalOpen, setAddModalOpen] = useState(false);
    const [selectedEmp, setSelectedEmp] = useState(null);
    const [taskModalOpen, setTaskModalOpen] = useState(false);
    const [taskData, setTaskData] = useState({
        date: new Date().toISOString().split('T')[0],
        tasks: [{ priority: 'Medium', task: '', expected_time: '', deadline: '' }]
    });

    const [reportModalOpen, setReportModalOpen] = useState(false);
    const [reportData, setReportData] = useState(null);
    const [reportDate, setReportDate] = useState('');

    useEffect(() => {
        fetchEmployees();
    }, []);

    const fetchEmployees = async () => {
        try {
            const res = await api.get('/admin/employees');
            setEmployees(res.data);
        } catch (err) {
            console.error("Failed to fetch employees", err);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                ...formData,
                roles: formData.roles.split(',').map(r => r.trim())
            };
            await api.post('/admin/employees/add', payload);
            setMsg('Employee Added Successfully! 🚀');
            fetchEmployees();
            setFormData({ emp_id: '', name: '', email: '', password: '', designation: '', roles: '', is_mentor: false });
            setAddModalOpen(false);
        } catch (err) {
            setMsg('Failed to add employee. ❌');
        }
    };

    const openTaskModal = (empId, empName) => {
        setSelectedEmp({ id: empId, name: empName });
        setTaskData({
            date: new Date().toISOString().split('T')[0],
            tasks: [{ priority: 'Medium', task: '', expected_time: '', deadline: '' }]
        });
        setTaskModalOpen(true);
    };

    const handleTaskChange = (index, field, value) => {
        const updatedTasks = [...taskData.tasks];
        updatedTasks[index][field] = value;
        setTaskData({ ...taskData, tasks: updatedTasks });
    };

    const addTaskRow = () => {
        setTaskData({
            ...taskData,
            tasks: [...taskData.tasks, { priority: 'Medium', task: '', expected_time: '', deadline: '' }]
        });
    };

    const submitTasks = async () => {
        try {
            await api.post('/admin/employees/assign-tasks', {
                emp_id: selectedEmp.id,
                date: taskData.date,
                tasks: taskData.tasks
            });
            setMsg(`Tasks Assigned to ${selectedEmp.name}! ✅`);
            setTaskModalOpen(false);
        } catch (err) {
            console.error(err);
            setMsg('Failed to assign tasks. ❌');
        }
    };

    const viewPreviousReport = async (empId) => {
        try {
            // Default to yesterday
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);
            const dateStr = yesterday.toISOString().split('T')[0];

            setReportDate(dateStr); // Initial fetch for yesterday

            const res = await api.get(`/admin/employees/${empId}/report?date_str=${dateStr}`);
            setReportData(res.data);
            setReportModalOpen(true);
        } catch (err) {
            console.error(err);
            setMsg('Failed to fetch report. ❌');
        }
    };

    return (
        <div className="relative p-6">
            {/* Header & Add Button */}
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-tech text-neon-blue text-glow-blue">
                    ADMIN <span className="text-neon-red">DASHBOARD</span>
                </h2>
                <button
                    onClick={() => setAddModalOpen(true)}
                    className="px-6 py-3 bg-neon-blue text-black font-bold rounded hover:bg-white transition shadow-[0_0_15px_rgba(0,242,255,0.4)] uppercase tracking-widest"
                >
                    + Add Member
                </button>
            </div>

            {msg && <div className="mb-4 p-3 border border-neon-blue text-neon-blue rounded animate-pulse">{msg}</div>}

            {/* Employee List (Full Width) */}
            <div className="bg-space-800 p-6 rounded-xl border border-blue-900 shadow-neon-blue overflow-y-auto max-h-[800px]">
                <h3 className="text-xl text-neon-blue mb-4">Active Personnel</h3>
                <p className="text-xs text-starlight opacity-50 mb-4">Click on an employee to assign tasks.</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(employees).map(([id, emp]) => (
                        <motion.div
                            key={id}
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                            onClick={() => openTaskModal(id, emp.name)}
                            className="p-4 bg-space-900 border border-blue-800 rounded hover:border-neon-blue hover:shadow-[0_0_10px_rgba(0,242,255,0.3)] transition cursor-pointer group"
                        >
                            <div className="flex justify-between items-start">
                                <div>
                                    <h4 className="text-neon-blue font-bold group-hover:text-white transition">{emp.name} <span className="text-xs text-starlight opacity-70">({id})</span></h4>
                                    <p className="text-xs text-starlight opacity-70">{emp.designation}</p>
                                </div>
                                {emp.is_mentor && <span className="text-[10px] bg-neon-red text-white px-2 py-1 rounded tracking-wider shadow-[0_0_5px_rgba(255,0,0,0.5)]">MENTOR</span>}
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Sheet Management Card */}
            <div className="bg-space-800 p-6 rounded-xl border border-yellow-500 shadow-neon-blue mb-6">
                <h3 className="text-xl text-yellow-500 mb-4 font-bold flex items-center gap-2">
                    <span className="text-2xl">⚡</span> SHEET GENERATION STATION
                </h3>
                <div className="flex flex-wrap items-end gap-4">
                    <div>
                        <label className="block text-xs text-starlight mb-1">Target Month</label>
                        <select
                            id="sheetMonth"
                            className="bg-space-900 border border-blue-800 text-white p-3 rounded w-32 focus:border-neon-blue focus:outline-none"
                            defaultValue={new Date().getMonth() + 1}
                        >
                            {Array.from({ length: 12 }, (_, i) => (
                                <option key={i} value={i + 1}>{new Date(0, i).toLocaleString('default', { month: 'long' })}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-xs text-starlight mb-1">Target Year</label>
                        <select
                            id="sheetYear"
                            className="bg-space-900 border border-blue-800 text-white p-3 rounded w-24 focus:border-neon-blue focus:outline-none"
                            defaultValue={new Date().getFullYear()}
                        >
                            <option value={2024}>2024</option>
                            <option value={2025}>2025</option>
                            <option value={2026}>2026</option>
                        </select>
                    </div>
                    <button
                        onClick={async () => {
                            const m = parseInt(document.getElementById('sheetMonth').value);
                            const y = parseInt(document.getElementById('sheetYear').value);
                            if (!window.confirm(`Initialize Bulk Sheet Generation for ${m}/${y}? This may take 2-3 minutes.`)) return;

                            setMsg('Initializing Sequence... Please Wait. ⏳');
                            try {
                                const res = await api.post('/admin/generate-sheets', { month: m, year: y });
                                setMsg(`Operation Complete! Success: ${res.data.summary.success}, Skipped: ${res.data.summary.skipped}. ✅`);
                            } catch (err) {
                                console.error(err);
                                setMsg('Sequence Failed. Check Logs. ❌');
                            }
                        }}
                        className="px-6 py-3 bg-yellow-600 hover:bg-yellow-500 text-white font-bold rounded shadow-[0_0_15px_rgba(255,215,0,0.3)] transition uppercase tracking-wider h-[48px]"
                    >
                        Prepare Monthly Sheets
                    </button>
                    <p className="text-xs text-starlight opacity-50 max-w-sm ml-4 mb-2">
                        *Creates missing daily sheets for all active employees. Skips existing ones.
                    </p>
                </div>

                {/* Drive Sync Section */}
                <div className="mt-8 pt-6 border-t border-yellow-500/30">
                    <h4 className="text-lg text-neon-blue mb-4 font-bold flex items-center gap-2">
                        <span className="text-xl">🔄</span> DRIVE SYNCHRONIZATION
                    </h4>
                    <div className="flex items-center gap-4">
                        <button
                            onClick={async () => {
                                if (!window.confirm("WARNING: This will DELETE any folder in 'EMS_Root' that does not belong to an active employee.\n\nAre you sure you want to Sync & Clean Up?")) return;

                                setMsg('Syncing Drive... This may take a moment. ⏳');
                                try {
                                    const res = await api.post('/admin/sync-drive');
                                    const s = res.data.summary;
                                    setMsg(`Sync Complete! Created: ${s.created.length}, Relinked: ${s.relinked.length}, Removed: ${s.removed.length}. ✅`);
                                } catch (err) {
                                    console.error(err);
                                    setMsg('Sync Failed. Check Logs. ❌');
                                }
                            }}
                            className="px-6 py-3 bg-blue-900/50 border border-neon-blue text-neon-blue font-bold rounded hover:bg-neon-blue hover:text-black transition uppercase tracking-wider h-[48px]"
                        >
                            Sync & Cleanup Drive
                        </button>
                        <p className="text-xs text-starlight opacity-50 max-w-lg">
                            Scans 'EMS_Root'. Creates folders for missing employees.
                            <span className="text-red-400 font-bold"> DELETES any folder that isn't linked to an active user.</span>
                        </p>
                    </div>
                </div>
            </div>

            {/* Add Employee Modal */}
            {addModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                        className="bg-space-800 border-2 border-neon-blue rounded-xl p-8 w-full max-w-2xl shadow-[0_0_50px_rgba(0,242,255,0.2)]"
                    >
                        <div className="flex justify-between items-center mb-6 border-b border-blue-900 pb-4">
                            <h3 className="text-2xl font-tech text-neon-red">Initialize Recruit</h3>
                            <button onClick={() => setAddModalOpen(false)} className="text-starlight hover:text-red-500 text-2xl">&times;</button>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <input
                                    type="text" placeholder="Employee ID" required
                                    value={formData.emp_id} onChange={e => setFormData({ ...formData, emp_id: e.target.value })}
                                    className="bg-red-950/30 border border-red-900 p-3 rounded text-neon-blue w-full placeholder:text-cyan-400 placeholder:drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] focus:border-neon-red focus:outline-none focus:shadow-[0_0_10px_rgba(255,0,0,0.3)] transition"
                                />
                                <input
                                    type="text" placeholder="Full Name" required
                                    value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    className="bg-red-950/30 border border-red-900 p-3 rounded text-neon-blue w-full placeholder:text-cyan-400 placeholder:drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] focus:border-neon-red focus:outline-none focus:shadow-[0_0_10px_rgba(255,0,0,0.3)] transition"
                                />
                            </div>
                            <input
                                type="email" placeholder="Email" required
                                value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })}
                                className="bg-red-950/30 border border-red-900 p-3 rounded text-neon-blue w-full placeholder:text-cyan-400 placeholder:drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] focus:border-neon-red focus:outline-none focus:shadow-[0_0_10px_rgba(255,0,0,0.3)] transition"
                            />
                            <input
                                type="password" placeholder="Password" required
                                value={formData.password} onChange={e => setFormData({ ...formData, password: e.target.value })}
                                className="bg-red-950/30 border border-red-900 p-3 rounded text-neon-blue w-full placeholder:text-cyan-400 placeholder:drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] focus:border-neon-red focus:outline-none focus:shadow-[0_0_10px_rgba(255,0,0,0.3)] transition"
                            />
                            <input
                                type="text" placeholder="Designation" required
                                value={formData.designation} onChange={e => setFormData({ ...formData, designation: e.target.value })}
                                className="bg-red-950/30 border border-red-900 p-3 rounded text-neon-blue w-full placeholder:text-cyan-400 placeholder:drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] focus:border-neon-red focus:outline-none focus:shadow-[0_0_10px_rgba(255,0,0,0.3)] transition"
                            />
                            <div>
                                <label className="block text-xs text-neon-red mb-1 drop-shadow-[0_0_5px_rgba(255,0,0,0.8)]">Role & Responsibility</label>
                                <textarea
                                    placeholder="E.g. Frontend, Backend (comma separated)" required
                                    value={formData.roles} onChange={e => setFormData({ ...formData, roles: e.target.value })}
                                    className="bg-red-950/30 border border-red-900 p-3 rounded text-neon-blue w-full placeholder:text-cyan-400 placeholder:drop-shadow-[0_0_8px_rgba(34,211,238,0.8)] h-24 focus:border-neon-red focus:outline-none focus:shadow-[0_0_10px_rgba(255,0,0,0.3)] transition"
                                />
                            </div>
                            <label className="flex items-center gap-2 text-starlight cursor-pointer p-2 border border-blue-900/50 rounded hover:bg-blue-900/20">
                                <input
                                    type="checkbox"
                                    checked={formData.is_mentor}
                                    onChange={e => setFormData({ ...formData, is_mentor: e.target.checked })}
                                    className="accent-neon-red w-5 h-5"
                                />
                                Assign as Mentor
                            </label>
                            <button type="submit" className="w-full py-4 bg-neon-red text-white font-bold rounded hover:bg-neon-red/80 transition shadow-[0_0_15px_rgba(255,0,0,0.4)] uppercase tracking-wider">
                                ADD TO DATABASE
                            </button>
                        </form>
                    </motion.div>
                </div>
            )}

            {/* Task Assignment Modal */}
            {taskModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                        className="bg-space-800 border-2 border-neon-blue rounded-xl p-6 w-full max-w-4xl shadow-[0_0_50px_rgba(0,242,255,0.2)] max-h-[90vh] overflow-y-auto"
                    >
                        <div className="flex justify-between items-center mb-6 border-b border-blue-900 pb-4">
                            <h3 className="text-2xl font-tech text-white">Assign Tasks: <span className="text-neon-blue">{selectedEmp?.name}</span></h3>
                            <button onClick={() => setTaskModalOpen(false)} className="text-starlight hover:text-neon-red text-2xl">&times;</button>
                        </div>

                        <div className="mb-6">
                            <label className="block text-sm text-neon-blue mb-2">Task Date</label>
                            <input
                                type="date"
                                value={taskData.date}
                                onChange={(e) => setTaskData({ ...taskData, date: e.target.value })}
                                className="bg-space-900 border border-blue-800 text-white p-2 rounded"
                            />
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm text-starlight">
                                <thead className="bg-blue-900/30 text-neon-blue uppercase">
                                    <tr>
                                        <th className="p-3">Priority</th>
                                        <th className="p-3 w-1/3">Task</th>
                                        <th className="p-3">Expected Time</th>
                                        <th className="p-3">Deadline</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-blue-900/30">
                                    {taskData.tasks.map((task, index) => (
                                        <tr key={index} className="hover:bg-blue-900/10 transition">
                                            <td className="p-2">
                                                <select
                                                    value={task.priority}
                                                    onChange={(e) => handleTaskChange(index, 'priority', e.target.value)}
                                                    className="bg-space-900 border border-blue-800 rounded p-2 text-white w-full"
                                                >
                                                    <option>High</option>
                                                    <option>Medium</option>
                                                    <option>Low</option>
                                                </select>
                                            </td>
                                            <td className="p-2">
                                                <input
                                                    type="text" placeholder="Description of the mission"
                                                    value={task.task}
                                                    onChange={(e) => handleTaskChange(index, 'task', e.target.value)}
                                                    className="bg-space-900 border border-blue-800 rounded p-2 text-white w-full"
                                                />
                                            </td>
                                            <td className="p-2">
                                                <input
                                                    type="text" placeholder="e.g. 2h 30m"
                                                    value={task.expected_time}
                                                    onChange={(e) => handleTaskChange(index, 'expected_time', e.target.value)}
                                                    className="bg-space-900 border border-blue-800 rounded p-2 text-white w-full"
                                                />
                                            </td>
                                            <td className="p-2">
                                                <input
                                                    type="date"
                                                    value={task.deadline}
                                                    onChange={(e) => handleTaskChange(index, 'deadline', e.target.value)}
                                                    className="bg-space-900 border border-blue-800 rounded p-2 text-white w-full"
                                                />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="flex gap-4 mt-6">
                            <button
                                onClick={addTaskRow}
                                className="px-4 py-2 border border-neon-blue text-neon-blue rounded hover:bg-neon-blue hover:text-black transition uppercase text-sm font-bold"
                            >
                                + Add Task Row
                            </button>
                            <button
                                onClick={submitTasks}
                                className="flex-1 px-4 py-2 bg-gradient-to-r from-neon-red to-red-800 text-white rounded font-bold uppercase hover:shadow-[0_0_20px_rgba(255,0,0,0.4)] transition"
                            >
                                Dispatch Assignment
                            </button>
                        </div>

                        {/* View Previous Report Section within Task Modal */}
                        <div className="mt-8 pt-6 border-t border-blue-900/50 flex flex-col items-center gap-4">
                            <button
                                onClick={() => viewPreviousReport(selectedEmp.id)}
                                className="px-6 py-2 bg-space-900 border border-yellow-500/50 text-yellow-500 rounded hover:bg-yellow-500/20 transition uppercase text-sm font-bold shadow-[0_0_10px_rgba(255,215,0,0.2)]"
                            >
                                📜 View Previous Day Assignment/Report
                            </button>
                        </div>

                        {/* Remove Employee Button at Bottom */}
                        <div className="mt-8 pt-6 border-t border-red-900/30 flex justify-center">
                            <button
                                onClick={async () => {
                                    if (window.confirm(`Are you sure you want to PERMANENTLY REMOVE ${selectedEmp.name} (${selectedEmp.id}) from the system?`)) {
                                        try {
                                            await api.delete(`/admin/employees/${selectedEmp.id}`);
                                            setMsg(`Employee ${selectedEmp.name} Removed. 🗑️`);
                                            setTaskModalOpen(false);
                                            fetchEmployees();
                                        } catch (err) {
                                            console.error(err);
                                            setMsg('Failed to remove employee. ❌');
                                        }
                                    }
                                }}
                                className="px-6 py-3 bg-red-950/50 border border-red-800 text-red-500 rounded hover:bg-red-900/80 hover:text-white transition uppercase text-sm font-bold shadow-[0_0_15px_rgba(255,0,0,0.2)] flex items-center gap-2"
                            >
                                🗑️ Remove Employee
                            </button>
                        </div>

                    </motion.div>
                </div>
            )}

            {/* Report Viewer Modal */}
            {reportModalOpen && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/90 backdrop-blur-md p-4">
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                        className="bg-space-800 border-2 border-yellow-500/50 rounded-xl p-6 w-full max-w-5xl shadow-[0_0_50px_rgba(255,215,0,0.2)] max-h-[90vh] overflow-y-auto"
                    >
                        <div className="flex justify-between items-center mb-6 border-b border-yellow-900/50 pb-4">
                            <div>
                                <h3 className="text-2xl font-tech text-yellow-500">Mission Report Log</h3>
                                <p className="text-sm text-starlight opacity-70">Operative: {selectedEmp?.name} | Date: {reportData?.date}</p>
                            </div>
                            <button onClick={() => setReportModalOpen(false)} className="text-starlight hover:text-red-500 text-2xl">&times;</button>
                        </div>

                        {!reportData?.found ? (
                            <div className="p-8 text-center text-red-400 border border-dashed border-red-900 rounded bg-red-900/10">
                                ⚠️ No Mission Report found for this date.
                            </div>
                        ) : (
                            <div className="space-y-8">
                                {/* Office Report */}
                                <div>
                                    <h4 className="text-lg text-neon-blue mb-2 font-bold border-l-4 border-neon-blue pl-3">OFFICE PROTOCOLS</h4>
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-left text-xs bg-space-900 border border-blue-900">
                                            <thead className="bg-blue-900/30 text-neon-blue">
                                                <tr>
                                                    <th className="p-2">Time Slot</th>
                                                    <th className="p-2">Task</th>
                                                    <th className="p-2">Description</th>
                                                    <th className="p-2">Status</th>
                                                    <th className="p-2">Remarks</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-blue-900/20 text-starlight">
                                                {reportData.office.map((row, i) => (
                                                    <tr key={i} className="hover:bg-white/5">
                                                        {row.map((cell, j) => <td key={j} className="p-2 border-r border-blue-900/20">{cell}</td>)}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>

                                {/* Mentor Report */}
                                {reportData.mentor.length > 0 && (
                                    <div>
                                        <h4 className="text-lg text-neon-red mb-2 font-bold border-l-4 border-neon-red pl-3">MENTORSHIP LOGS</h4>
                                        <div className="overflow-x-auto">
                                            <table className="w-full text-left text-xs bg-space-900 border border-red-900">
                                                <thead className="bg-red-900/30 text-neon-red">
                                                    <tr>
                                                        <th className="p-2">Time Slot</th>
                                                        <th className="p-2">Grade</th>
                                                        <th className="p-2">Topics</th>
                                                        <th className="p-2">Activity</th>
                                                        <th className="p-2">Remarks</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-red-900/20 text-starlight">
                                                    {reportData.mentor.map((row, i) => (
                                                        <tr key={i} className="hover:bg-white/5">
                                                            {row.map((cell, j) => <td key={j} className="p-2 border-r border-red-900/20">{cell}</td>)}
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </motion.div>
                </div>
            )}
        </div>
    );
};

export default Admin;

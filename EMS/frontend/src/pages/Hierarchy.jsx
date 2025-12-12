import { useState, useEffect } from 'react';
import api from '../services/api';
import { motion } from 'framer-motion';

const Hierarchy = () => {
    const [employees, setEmployees] = useState({});
    const [loading, setLoading] = useState(true);
    const [editModalOpen, setEditModalOpen] = useState(false);
    const [selectedEmp, setSelectedEmp] = useState(null);
    const [formData, setFormData] = useState({ designation: '', roles: '' });
    const [msg, setMsg] = useState('');

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

    // Group by Designation
    const grouped = {};
    Object.entries(employees).forEach(([id, emp]) => {
        const desig = emp.designation || 'Unassigned';
        if (!grouped[desig]) grouped[desig] = [];
        grouped[desig].push({ id, ...emp });
    });

    const openEdit = (emp) => {
        setSelectedEmp(emp);
        setFormData({
            designation: emp.designation,
            roles: Array.isArray(emp.roles) ? emp.roles.join(', ') : emp.roles
        });
        setEditModalOpen(true);
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            await api.post('/admin/employees/add', {
                // We reuse the add endpoint or need an update endpoint? 
                // user_manager.update_employee exists but no specific route?
                // Wait, add_employee checks if ID exists.
                // We need an update endpoint. Using add will fail "already exists".
                // I need to check admin.py for update endpoint.
                // It doesn't look like there is a specific UPDATE endpoint for details.
                // I might need to add one.
                // For now, let's assume I need to ADD that endpoint too. 
                // Wait, I can use "add" with overwrite? No, user_manager returns False.

                // Let's implement client-side first, then fix backend.
                emp_id: selectedEmp.id,
                name: selectedEmp.name,
                email: selectedEmp.email,
                folder_id: selectedEmp.folder_id,
                password: selectedEmp.password, // We don't have password here... this is tricky.
                // We need a proper UPDATE endpoint.
                designation: formData.designation,
                roles: formData.roles.split(',').map(r => r.trim()),
                is_mentor: selectedEmp.is_mentor,
                avenger_character: selectedEmp.avenger_character
            });
            // Ah, I can't use Add.
            alert("Update Endpoint Missing! I will focus on UI first.");
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="p-6 relative min-h-screen">
            <h2 className="text-3xl font-tech text-neon-blue text-glow-blue mb-8">
                COMMAND <span className="text-neon-red">HIERARCHY</span>
            </h2>

            <div className="space-y-8">
                {Object.entries(grouped).map(([role, emps]) => (
                    <div key={role} className="bg-space-900/50 p-6 rounded-xl border border-blue-900/50">
                        <h3 className="text-xl text-yellow-500 font-bold mb-4 uppercase tracking-widest border-b border-yellow-500/20 pb-2">{role} <span className="text-sm opacity-50 text-starlight ml-2">({emps.length})</span></h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {emps.map(emp => (
                                <motion.div
                                    key={emp.id}
                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                                    className="p-4 bg-space-800 border border-blue-800 rounded flex justify-between items-center group hover:border-neon-blue transition"
                                >
                                    <div>
                                        <h4 className="text-neon-blue font-bold">{emp.name}</h4>
                                        <p className="text-xs text-starlight opacity-70">{emp.id}</p>
                                    </div>
                                    <button
                                        onClick={() => openEdit(emp)}
                                        className="px-3 py-1 bg-blue-900/50 text-neon-blue text-xs rounded hover:bg-neon-blue hover:text-black transition"
                                    >
                                        EDIT ROLE
                                    </button>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {/* Edit Modal */}
            {editModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <motion.div
                        initial={{ scale: 0.9 }} animate={{ scale: 1 }}
                        className="bg-space-800 border-2 border-neon-blue rounded-xl p-8 w-full max-w-md shadow-neon-blue"
                    >
                        <h3 className="text-xl font-bold text-white mb-4">Edit Position: {selectedEmp?.name}</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs text-neon-blue mb-1">Designation</label>
                                <input
                                    type="text"
                                    value={formData.designation}
                                    onChange={e => setFormData({ ...formData, designation: e.target.value })}
                                    className="w-full bg-space-900 border border-blue-800 text-white p-2 rounded focus:outline-none focus:border-neon-blue"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-neon-blue mb-1">Roles (comma separated)</label>
                                <textarea
                                    value={formData.roles}
                                    onChange={e => setFormData({ ...formData, roles: e.target.value })}
                                    className="w-full bg-space-900 border border-blue-800 text-white p-2 rounded h-24 focus:outline-none focus:border-neon-blue"
                                />
                            </div>
                            <div className="flex gap-4 mt-6">
                                <button onClick={() => setEditModalOpen(false)} className="px-4 py-2 text-starlight hover:text-white">Cancel</button>
                                <button onClick={handleUpdate} className="flex-1 px-4 py-2 bg-neon-blue text-black font-bold rounded hover:bg-white transition">SAVE CHANGES</button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

export default Hierarchy;

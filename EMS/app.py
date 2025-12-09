import streamlit as st
import os
import datetime
import pandas as pd
from services.auth import AuthManager
from services.drive_manager import DriveManager
from services.sheet_manager import SheetManager
from services.scheduler import SchedulerService
from services.user_manager import UserManager
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title="EMS - Command Center", layout="wide", page_icon="🤖")

# Advanced Robotic Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

    /* Main Background with Grid Animation */
    .stApp {
        background-color: #020205;
        background-image: 
            linear-gradient(rgba(0, 255, 204, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 204, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #e0f7fa;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Headers */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00ffcc;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
    }
    
    /* Holographic Cards */
    .css-1r6slb0, .stMetric, .stAlert, div[data-testid="stExpander"] {
        background: rgba(10, 20, 30, 0.7);
        border: 1px solid rgba(0, 255, 204, 0.3);
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.1), inset 0 0 20px rgba(0, 255, 204, 0.05);
        backdrop-filter: blur(5px);
        border-radius: 15px;
        position: relative;
        overflow: hidden;
    }
    
    /* Scanning Line Animation for Cards */
    .css-1r6slb0::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ffcc, transparent);
        animation: scan 3s infinite linear;
        opacity: 0.5;
    }
    
    @keyframes scan {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    /* Buttons (Neon Glow) */
    .stButton>button {
        background: transparent;
        color: #00ffcc;
        border: 2px solid #00ffcc;
        border-radius: 5px;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        text-transform: uppercase;
        box-shadow: 0 0 5px #00ffcc;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #00ffcc;
        color: #000;
        box-shadow: 0 0 20px #00ffcc, 0 0 40px #00ffcc;
        transform: scale(1.05);
    }

    /* Inputs */
    .stTextInput>div>div>input, .stDateInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        background-color: rgba(0, 0, 0, 0.5);
        color: #00ffcc;
        border: 1px solid #00ffcc;
        border-radius: 5px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 16px;
/* --- GLOBAL THEME: BLUE & RED --- */
.stApp {
    background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
    color: #cceeff !important; /* Ice Blue Text */
    font-family: 'Courier New', monospace;
}

/* --- TEXT ELEMENTS --- */
p, label, span, div, li, .stMarkdown, .stText, .stCaption {
    color: #cceeff !important;
}

/* --- SIDEBAR --- */
[data-testid="stSidebar"] {
    background-color: #0b1021;
    border-right: 1px solid #ff3366; /* Red Border */
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
    color: #99ccff !important;
}

/* --- HEADERS --- */
h1, h2, h3, h4, h5, h6 {
    color: #ff3366 !important; /* Neon Red */
    text-shadow: 0 0 15px #ff3366, 0 0 30px #550000;
    text-transform: uppercase;
    letter-spacing: 3px;
}

/* --- BUTTONS --- */
.stButton>button {
    background: linear-gradient(135deg, #003366 0%, #001133 100%); /* Deep Blue */
    color: #ff3366 !important; /* Red Text */
    border: 1px solid #ff3366; /* Red Border */
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(255, 51, 102, 0.3);
    transition: all 0.3s ease;
    text-transform: uppercase;
    font-weight: bold;
    letter-spacing: 1px;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #990033 0%, #660022 100%); /* Red Gradient */
    box-shadow: 0 0 20px rgba(255, 51, 102, 0.6);
    transform: translateY(-2px);
    color: #ffffff !important;
    border-color: #ff99aa;
}

/* --- INPUTS & CARDS --- */
.stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea, .stDateInput>div>div>input {
    background-color: #050a15 !important;
    color: #ff3366 !important; /* Red Input Text */
    caret-color: #ff3366; /* Red Cursor */
    border: 1px solid #0055aa !important; /* Blue Border */
    border-radius: 6px;
    font-weight: bold;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color: #ff3366 !important; /* Red Focus */
    box-shadow: 0 0 15px rgba(255, 51, 102, 0.3);
}
/* Placeholder Text */
::placeholder {
    color: #0055aa !important;
    opacity: 0.7;
}
/* Input Labels */
.stTextInput label, .stSelectbox label, .stTextArea label, .stDateInput label, .stCheckbox label {
    color: #cceeff !important;
}

/* --- DATAFRAME / TABLE --- */
.stDataFrame {
    border: 1px solid #0055aa;
    background-color: rgba(5, 10, 21, 0.5);
}
[data-testid="stDataFrameResizable"] {
    background-color: transparent;
}
/* Table Text */
[data-testid="stDataFrameResizable"] div {
    color: #cceeff !important;
}

/* --- EXPANDER --- */
.streamlit-expanderHeader {
    background-color: #0b1525;
    color: #ff3366 !important; /* Red Header */
    border: 1px solid #004488;
    border-radius: 6px;
}
.streamlit-expanderContent {
    color: #cceeff !important;
    background-color: rgba(11, 21, 37, 0.5);
    border-top: 1px solid #ff3366;
}

/* --- SCROLLBAR --- */
::-webkit-scrollbar {
    width: 12px;
    background: #020617;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #003366, #ff3366); /* Blue to Red */
    border-radius: 6px;
    border: 2px solid #020617;
}
::-webkit-scrollbar-thumb:hover {
    background: #ff3366;
}

/* --- ALERTS --- */
.stSuccess {
    background-color: rgba(0, 51, 102, 0.5);
    border: 1px solid #0088ff;
    color: #0088ff !important; /* Blue Success */
}
.stError {
    background-color: rgba(102, 0, 34, 0.5);
    border: 1px solid #ff3366;
    color: #ff3366 !important; /* Red Error */
}
.stInfo {
    background-color: rgba(0, 34, 68, 0.5);
    border: 1px solid #0055aa;
    color: #66ccff !important; /* Light Blue Info */
}

/* --- ANIMATIONS --- */
@keyframes pulse-red {
    0% { box-shadow: 0 0 5px rgba(255, 51, 102, 0.4); }
    50% { box-shadow: 0 0 20px rgba(255, 51, 102, 0.7); }
    100% { box-shadow: 0 0 5px rgba(255, 51, 102, 0.4); }
}
.stButton>button {
    animation: pulse-red 3s infinite;
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ EMS COMMAND CENTER ⚡")

# Initialize Services
if 'auth_manager' not in st.session_state:
    st.session_state['auth_manager'] = AuthManager()
    st.session_state['drive_manager'] = DriveManager(st.session_state['auth_manager'].get_drive_service())
    st.session_state['sheet_manager'] = SheetManager(st.session_state['auth_manager'].get_sheet_service())
    st.session_state['user_manager'] = UserManager()

auth_manager = st.session_state['auth_manager']
drive_manager = st.session_state['drive_manager']
sheet_manager = st.session_state['sheet_manager']
user_manager = st.session_state['user_manager']

# Authenticate
if not auth_manager.drive_service:
    success, msg = auth_manager.authenticate()
    if not success:
        st.error(f"Authentication Failed: {msg}")
        st.stop()
    else:
        # Re-init managers with valid services
        drive_manager.service = auth_manager.get_drive_service()
        sheet_manager.service = auth_manager.get_sheet_service()

# Start Scheduler
if 'scheduler' not in st.session_state:
    scheduler = SchedulerService(drive_manager, sheet_manager)
    scheduler.start()
    st.session_state['scheduler'] = scheduler

# Sidebar
st.sidebar.header("🛸 Navigation")
role = st.sidebar.radio("Select Role", ["Admin", "Team"])

if role == "Admin":
    # Admin Login
    st.sidebar.info("🔑 **Test Creds:** `admin123`")
    password = st.sidebar.text_input("🔑 Admin Password", type="password")
    if not user_manager.verify_admin(password):
        st.warning("🔒 ACCESS DENIED. Enter Admin Password.")
        st.stop()

    page = st.sidebar.radio("Go to", ["📊 Dashboard", "👥 Manage Team", "📝 Assign Tasks", "Notifications", "📈 Reports"])

    if page == "📊 Dashboard":
        st.subheader("📊 COMMAND CENTER DASHBOARD")
        
        # 3D Visuals
        c1, c2, c3 = st.columns(3)
        with c1:
            try:
                st.image("assets/team_holo.png", caption="Team Module Online")
            except: pass
        with c2:
            try:
                st.image("assets/task_holo.png", caption="Task Module Online")
            except: pass
        with c3:
            try:
                st.image("assets/report_holo.png", caption="Analytics Module Online")
            except: pass

        # Metrics
        total_employees = len(user_manager.get_all_employees())
        now = datetime.datetime.now()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Team Members", total_employees, delta="Active")
        with col2:
            st.metric("System Status", "ONLINE", delta="Stable")
        with col3:
            st.metric("Current Date", now.strftime("%Y-%m-%d"))
            
        st.markdown("---")
        st.info("🚀 Welcome, Commander. Select an operation from the sidebar to begin.")
        
    elif page == "👥 Manage Team":
        st.subheader("👥 MANAGE TEAM")
        
        # 1. List Employees
        st.markdown("### 📋 Current Personnel")
        employees = user_manager.get_all_employees()
        if employees:
            # Convert to DataFrame for nice display
            emp_list = []
            for eid, data in employees.items():
                emp_list.append({
                    "ID": eid, 
                    "Name": data['name'], 
                    "Designation": data.get('designation', 'N/A'),
                    "Email": data['email']
                })
            st.dataframe(pd.DataFrame(emp_list), use_container_width=True)
        else:
            st.info("No personnel records found.")

        st.markdown("---")

        # 2. Add Employee
        with st.expander("➕ Add New Recruit", expanded=False):
            with st.form("add_employee_form"):
                col1, col2 = st.columns(2)
                with col1:
                    emp_id = st.text_input("🆔 Member ID (Unique)")
                    name = st.text_input("👤 Name")
                    designation = st.text_input("🎖️ Designation")
                with col2:
                    email = st.text_input("📧 Email")
                    password = st.text_input("🔑 Password", type="password")
                    is_mentor = st.checkbox("🎓 Assign as Mentor")
                    roles_input = st.text_area("📜 Roles (Comma separated)")
                
                submitted = st.form_submit_button("🚀 Initialize Recruit")
                
                if submitted:
                    if emp_id and name and email and password:
                        with st.spinner("⚙️ Creating workspace..."):
                            # 1. Create Folder
                            emp_folder_id, shared, msg = drive_manager.add_employee(name, email)
                            if shared:
                                # 2. Add to Database
                                roles_list = [r.strip() for r in roles_input.split(',')] if roles_input else []
                                success, db_msg = user_manager.add_employee(emp_id, name, email, emp_folder_id, password, designation, roles_list, is_mentor)
                                if success:
                                    st.success(f"✅ {name} (ID: {emp_id}) added successfully.")
                                    
                                    # 3. Create current month folder immediately
                                    now = datetime.datetime.now()
                                    current_month = now.strftime("%B_%Y")
                                    month_folder_id = drive_manager.create_folder(current_month, emp_folder_id)
                                    st.info(f"📂 Created folder for {current_month}")
                                    
                                    # 4. Create 31 sheets
                                    with st.spinner("📄 Generating 31 daily sheets..."):
                                        sheet_manager.create_month_sheets(drive_manager, month_folder_id, now.year, now.month)
                                    st.success("✅ 31 Daily Sheets created!")
                                    st.rerun() # Refresh list
                                else:
                                    st.error(f"❌ Database Error: {db_msg}")
                            else:
                                st.error(f"❌ Drive Error: {msg}")
                    else:
                        st.error("⚠️ Please fill in all fields.")

        # 3. Remove Employee
        with st.expander("🗑️ Remove Personnel", expanded=False):
            if not employees:
                st.warning("No employees to remove.")
            else:
                emp_options = {f"{data['name']} ({eid})": eid for eid, data in employees.items()}
                selected_remove = st.selectbox("Select Member to Remove", list(emp_options.keys()))
                remove_id = emp_options[selected_remove]
                
                st.warning(f"⚠️ Warning: This will remove {selected_remove} from the database and trash their Drive folder.")
                if st.button("🔥 Terminate Access"):
                    with st.spinner("Deleting records..."):
                        folder_id = employees[remove_id]['folder_id']
                        d_success, d_msg = drive_manager.delete_folder(folder_id)
                        u_success, u_msg = user_manager.remove_employee(remove_id)
                        
                        if u_success:
                            st.success(f"✅ {u_msg}")
                            if d_success:
                                st.info(f"🗑️ {d_msg}")
                            else:
                                st.warning(f"⚠️ Drive Deletion Failed: {d_msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {u_msg}")

        # 4. Edit Employee
        with st.expander("✏️ Edit Team Member", expanded=False):
            if not employees:
                st.warning("No employees to edit.")
            else:
                emp_options = {f"{data['name']} ({eid})": eid for eid, data in employees.items()}
                selected_edit = st.selectbox("Select Member to Edit", list(emp_options.keys()))
                edit_id = emp_options[selected_edit]
                edit_data = employees[edit_id]
                
                with st.form("edit_employee_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Name", value=edit_data['name'])
                        new_designation = st.text_input("Designation", value=edit_data.get('designation', ''))
                    with col2:
                        new_email = st.text_input("Email", value=edit_data['email'])
                        new_password = st.text_input("Password", value=edit_data.get('password', ''), type="password")
                        new_is_mentor = st.checkbox("🎓 Assign as Mentor", value=edit_data.get('is_mentor', False))
                    
                    new_roles_str = ", ".join(edit_data.get('roles', []))
                    new_roles_input = st.text_area("Roles (Comma separated)", value=new_roles_str)
                    
                    if st.form_submit_button("💾 Update Profile"):
                        new_roles_list = [r.strip() for r in new_roles_input.split(',')] if new_roles_input else []
                        success, msg = user_manager.update_employee(
                            edit_id, 
                            name=new_name, 
                            email=new_email, 
                            password=new_password, 
                            designation=new_designation, 
                            roles=new_roles_list,
                            is_mentor=new_is_mentor
                        )
                        if success:
                            st.success(f"✅ {msg}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

        st.markdown("---")
        st.subheader("🗓️ MONTHLY MAINTENANCE")
        if st.button("🔄 Generate Next Month Folders for All"):
            with st.spinner("⚙️ Processing all employees..."):
                employees = user_manager.get_all_employees()
                if not employees:
                    st.warning("⚠️ No employees in database.")
                else:
                    # Calculate next month
                    now = datetime.datetime.now()
                    if now.month == 12:
                        next_month_date = datetime.date(now.year + 1, 1, 1)
                    else:
                        next_month_date = datetime.date(now.year, now.month + 1, 1)
                    
                    next_month_str = next_month_date.strftime("%B_%Y")
                    
                    count = 0
                    for eid, emp in employees.items():
                        st.write(f"Processing {emp['name']}...")
                        m_folder = drive_manager.create_folder(next_month_str, emp['folder_id'])
                        sheet_manager.create_month_sheets(drive_manager, m_folder, next_month_date.year, next_month_date.month)
                        count += 1
                    
                    st.success(f"✅ Generated folders for {count} employees for {next_month_str}.")

    elif page == "📝 Assign Tasks":
        st.subheader("📝 ASSIGN TASKS")
        
        # Fetch Employees from DB
        employees = user_manager.get_all_employees()
        
        if not employees:
            st.warning("⚠️ No employees found.")
        else:
            # Create options list "Name (ID)"
            emp_options = {f"{data['name']} ({eid})": eid for eid, data in employees.items()}
            selected_option = st.selectbox("👤 Select Team Member", list(emp_options.keys()))
            selected_emp_id = emp_options[selected_option]
            selected_emp_data = employees[selected_emp_id]
            
            with st.form("assign_task_form"):
                col1, col2 = st.columns(2)
                with col1:
                    task_date = st.date_input("📅 Assignment Date")
                    deadline = st.date_input("⏳ Deadline")
                with col2:
                    expected_time = st.text_input("⏱️ Expected Time")
                    
                task_desc = st.text_area("📋 Task Description")
                
                submitted = st.form_submit_button("🚀 Transmit Task")
                
                if submitted:
                    if not task_desc or not expected_time:
                        st.error("⚠️ Please fill in all fields.")
                    else:
                        with st.spinner("📡 Transmitting task..."):
                            success, msg = sheet_manager.update_task_assignment(
                                drive_manager, selected_emp_data['folder_id'], task_date, task_desc, expected_time, deadline
                            )
                            if success:
                                st.success(f"✅ Task assigned to {selected_emp_data['name']}.")
                            else:
                                st.error(f"❌ Failed: {msg}")

    elif page == "📢 Notifications":
        st.subheader("📢 BROADCAST NOTIFICATION")
        
        employees = user_manager.get_all_employees()
        if not employees:
            st.warning("No employees.")
        else:
            emp_options = {f"{data['name']} ({eid})": eid for eid, data in employees.items()}
            selected_option = st.selectbox("👤 Select Recipient", list(emp_options.keys()))
            selected_emp_id = emp_options[selected_option]
            
            msg = st.text_area("Message")
            if st.button("📨 Send Notification"):
                if msg:
                    user_manager.add_notification(selected_emp_id, msg)
                    st.success("Notification Sent!")
                else:
                    st.error("Enter a message.")

    elif page == "📈 Reports":
        st.subheader("📈 PRODUCTIVITY REPORTS")
        
        # Select Employee
        employees = user_manager.get_all_employees()
        if not employees:
            st.warning("No employees found.")
        else:
            emp_options = {f"{data['name']} ({eid})": eid for eid, data in employees.items()}
            selected_option = st.selectbox("Select Member for Analysis", list(emp_options.keys()))
            selected_emp_id = emp_options[selected_option]
            selected_emp_data = employees[selected_emp_id]
            
            # Select Month
            col1, col2 = st.columns(2)
            with col1:
                year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.datetime.now().year)
            with col2:
                month = st.selectbox("Month", range(1, 13), index=datetime.datetime.now().month - 1)
            
            if st.button("📊 Generate Analytics"):
                with st.spinner("🧠 Crunching numbers from daily sheets..."):
                    data, msg = sheet_manager.calculate_monthly_productivity(
                        drive_manager, selected_emp_data['folder_id'], year, month
                    )
                    
                    if not data:
                        st.error(msg)
                    else:
                        st.success("Analysis Complete.")
                        
                        # Metrics
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric("Total Expected Hours", f"{data['expected_hours']} h")
                        with m2:
                            st.metric("Total Actual Hours", f"{data['actual_hours']} h")
                        with m3:
                            efficiency = 0
                            if data['expected_hours'] > 0:
                                efficiency = round((data['actual_hours'] / data['expected_hours']) * 100, 1)
                            st.metric("Efficiency Score", f"{efficiency}%")
                        
                        st.markdown("---")
                        
                        # Charts
                        c1, c2 = st.columns(2)
                        
                        with c1:
                            st.markdown("### 🕒 Hours Comparison")
                            fig = go.Figure(data=[
                                go.Bar(name='Expected', x=['Hours'], y=[data['expected_hours']], marker_color='#00ffcc'),
                                go.Bar(name='Actual', x=['Hours'], y=[data['actual_hours']], marker_color='#0099ff')
                            ])
                            fig.update_layout(
                                barmode='group',
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#00ffcc'),
                                title="Expected vs Actual Hours"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                        with c2:
                            st.markdown("### 📊 Task Status Distribution")
                            labels = list(data['status_counts'].keys())
                            values = list(data['status_counts'].values())
                            
                            fig2 = go.Figure(data=[go.Pie(
                                labels=labels, 
                                values=values, 
                                hole=.3,
                                marker=dict(colors=['#00ffcc', '#0099ff', '#ff0099'])
                            )])
                            fig2.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#00ffcc'),
                                title="Task Status"
                            )
                            st.plotly_chart(fig2, use_container_width=True)

elif role == "Team":
    st.subheader("👤 TEAM PORTAL")
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔐 Secure Login")
        st.info("🔑 **Test Creds:**\nID: `test_team`\nPass: `team123`")
        login_id = st.text_input("🆔 Member ID")
        login_pass = st.text_input("🔑 Password", type="password")
        
    if not login_id or not login_pass:
        st.info("👋 Please enter your Member ID and Password in the sidebar to login.")
        st.stop()
        
    # Verify Login
    is_valid, user_data = user_manager.verify_employee(login_id, login_pass)
    
    if not is_valid:
        st.error("❌ Invalid Credentials. Access Denied.")
        st.stop()
        
    # Welcome Header
    st.markdown(f"""
    <div style='padding: 20px; background: rgba(0, 255, 204, 0.1); border-radius: 10px; border: 1px solid #00ffcc; margin-bottom: 20px;'>
        <h2 style='margin:0;'>Welcome, {user_data['name']}</h2>
        <h4 style='margin:0; color: #fff;'>{user_data.get('designation', 'Team Member')}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Image for Team
    try:
        st.image("assets/robot_bg.png", use_container_width=True)
    except: pass
    
    # 4 Blocks Navigation
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📜 Roles & Resp."):
            st.session_state['team_view'] = 'roles'
    with col2:
        if st.button("📝 Tasks"):
            st.session_state['team_view'] = 'tasks'
    with col3:
        if st.button("📊 Reporting"):
            st.session_state['team_view'] = 'reporting'
    with col4:
        if st.button("🔔 Notifications"):
            st.session_state['team_view'] = 'notifications'
            
    view = st.session_state.get('team_view', 'roles')
    
    st.markdown("---")
    
    if view == 'roles':
        st.subheader("📜 Roles & Responsibilities")
        roles = user_data.get('roles', [])
        if roles:
            for r in roles:
                st.info(f"• {r}")
        else:
            st.write("No specific roles assigned.")
            
    elif view == 'tasks':
        st.subheader("📝 Assigned Tasks")
        report_date = st.date_input("Select Date", datetime.date.today())
        
        if st.button("Load Tasks"):
             with st.spinner("Accessing secure sheet..."):
                sheet_id, msg = sheet_manager.get_daily_sheet_id(drive_manager, user_data['folder_id'], report_date)
                if not sheet_id:
                    st.error(msg)
                else:
                    tasks = sheet_manager.read_assigned_tasks(sheet_id)
                    if tasks:
                        # Updated columns to include Deadline
                        df_tasks = pd.DataFrame(tasks, columns=["Task", "Deadline", "Expected Time", "Priority", "Notes"])
                        st.table(df_tasks)
                    else:
                        st.info("No tasks assigned for this date.")

    elif view == 'reporting':
        st.subheader("📊 Daily Reporting")
        report_date = st.date_input("Reporting Date", datetime.date.today())
        
        # Load Sheet ID first
        sheet_id, msg = sheet_manager.get_daily_sheet_id(drive_manager, user_data['folder_id'], report_date)
        
        if not sheet_id:
            st.error(f"Sheet not found for {report_date}. Please contact Admin.")
        else:
            # --- 1. TIME LOG ---
            st.markdown("### ⏱️ Time Log")
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                time_in = st.text_input("☀️ In Time")
            with c2:
                time_out = st.text_input("🌙 Out Time")
            with c3:
                st.write("")
                st.write("")
                if st.button("Update Time"):
                    sheet_manager.update_time_log(sheet_id, time_in, time_out)
                    st.success("Saved")
            
            st.markdown("---")
            
            # --- 2. OFFICE REPORT ---
            st.markdown("### 🏢 Office Report")
            
            # Fetch Assigned Tasks for Dropdown
            assigned_data = sheet_manager.read_assigned_tasks(sheet_id)
            task_options = [row[0] for row in assigned_data if row] + ["Others"]
            
            # Prepare Data for Editor
            # Fixed Slots
            slots_config = [
                ("09:30 - 10:30", 4), ("10:30 - 11:30", 5), ("11:30 - 12:30", 6),
                ("12:30 - 01:30 (LUNCH)", 7),
                ("01:30 - 02:30", 8), ("02:30 - 03:30", 9),
                ("03:30 - 04:00 (TEA)", 10),
                ("04:00 - 05:30", 11)
            ]
            
            # Create initial DF
            office_data = []
            for slot, idx in slots_config:
                if "LUNCH" in slot:
                    office_data.append({
                        "Time Slot": slot, "Task": "Others", "Description": "--- LUNCH BREAK ---", 
                        "Remarks": "Locked", "Problems": "", "_row_idx": idx
                    })
                elif "TEA" in slot:
                    office_data.append({
                        "Time Slot": slot, "Task": "Others", "Description": "--- TEA BREAK ---", 
                        "Remarks": "Locked", "Problems": "", "_row_idx": idx
                    })
                else:
                    office_data.append({
                        "Time Slot": slot,
                        "Task": "",
                        "Description": "",
                        "Remarks": "",
                        "Problems": "",
                        "_row_idx": idx # Hidden index
                    })
            
            df_office = pd.DataFrame(office_data)
            
            # Configure Editor
            edited_office = st.data_editor(
                df_office,
                column_config={
                    "Time Slot": st.column_config.TextColumn(disabled=True),
                    "Task": st.column_config.SelectboxColumn(
                        "Task",
                        help="Select assigned task. If 'Others', please specify the task in the 'Description' column.",
                        width="medium",
                        options=task_options,
                        required=True
                    ),
                    "Description": st.column_config.TextColumn(
                        "Description / Custom Task",
                        help="Details of the task. If 'Task' is 'Others', write the task name here.",
                        width="large"
                    ),
                    "Remarks": st.column_config.TextColumn("Remarks", width="small"),
                    "Problems": st.column_config.TextColumn("Problems", width="small"),
                    "_row_idx": None # Hide
                },
                hide_index=True,
                use_container_width=True,
                num_rows="fixed"
            )
            
            if st.button("💾 Save Office Report"):
                with st.spinner("Saving data..."):
                    error_found = False
                    # Iterate and save
                    for index, row in edited_office.iterrows():
                        if "LUNCH" in row['Time Slot'] or "TEA" in row['Time Slot']:
                            continue
                            
                        # Logic for Task
                        selected_task = row['Task']
                        description_val = row['Description']
                        
                        final_task = selected_task
                        
                        # Validation: If 'Others' selected, 'Description' must be filled
                        if selected_task == "Others":
                            if not description_val:
                                st.error(f"⚠️ Error in {row['Time Slot']}: You selected 'Others'. Please specify the task in the 'Description' column.")
                                error_found = True
                                continue
                            final_task = description_val # Use Description as the Task Name
                        
                        # Only save if there is data (or overwrite with empty if clearing?)
                        sheet_manager.update_office_row(
                            sheet_id, 
                            row['_row_idx'], 
                            final_task, 
                            description_val, 
                            row['Remarks'], 
                            row['Problems']
                        )
                    
                    if not error_found:
                        st.success("Office Report Saved!")

            # --- 3. MENTOR REPORT ---
            if user_data.get('is_mentor', False):
                st.markdown("---")
                st.markdown("### 🎓 Mentor Report")
                
                # Default Slots
                men_slots_config = [
                    ("08:00 - 09:00", 15), ("09:00 - 10:00", 16), ("10:00 - 11:00", 17), 
                    ("11:00 - 12:00", 18), ("12:00 - 01:00", 19), ("01:00 - 02:00", 20), 
                    ("02:00 - 03:00", 21)
                ]
                
                mentor_data = []
                for slot, idx in men_slots_config:
                    mentor_data.append({
                        "Time Slot": slot,
                        "Grade": "",
                        "Topic": "",
                        "Activity": "",
                        "Remarks": "",
                        "_row_idx": idx
                    })
                
                df_mentor = pd.DataFrame(mentor_data)
                
                edited_mentor = st.data_editor(
                    df_mentor,
                    column_config={
                        "Time Slot": st.column_config.TextColumn(disabled=False), # Editable
                        "_row_idx": None
                    },
                    hide_index=True,
                    use_container_width=True,
                    num_rows="fixed" # Keep fixed rows mapped to sheet rows?
                    # If we allow dynamic rows, we lose the mapping to specific sheet rows (15, 16...)
                    # User said "time slot (editable)".
                    # We will stick to fixed number of rows (7 rows) mapped to 15-21.
                    # They can change the text of the time slot.
                )
                
                if st.button("💾 Save Mentor Report"):
                    with st.spinner("Saving data..."):
                        for index, row in edited_mentor.iterrows():
                            sheet_manager.update_mentor_row(
                                sheet_id,
                                row['_row_idx'],
                                row['Time Slot'],
                                row['Grade'],
                                row['Topic'],
                                row['Activity'],
                                row['Remarks']
                            )
                    st.success("Mentor Report Saved!")

    elif view == 'notifications':
        st.subheader("🔔 Notifications")
        notifs = user_manager.get_notifications(login_id)
        if notifs:
            for n in reversed(notifs):
                st.warning(f"**{n['date']}**: {n['message']}")
        else:
            st.info("No new notifications.")

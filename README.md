Expense Tracker
Take control of your money. Track every expense. Plan a smarter budget.
A Flask-based personal finance web application for managing daily expenses, setting budgets, and understanding spending patterns.

About the Project
Expense Tracker is a personal finance management application built with Python and Flask. It helps users record and organize expenses, monitor monthly spending, manage annual and category-wise budgets, and review useful spending summaries.

The application includes account registration and login, user-specific expense records, profile management, and a collection of pages and API endpoints for expense and budget operations.
Project goal: Make everyday money management easier through organized expense records and clear spending insights.

 Key Features
 Feature	What it does
 User Authentication	Register, log in, and log out
 Expense Management	Add, view, edit, and delete expenses
 Category Tracking	Organize expenses by category
 Monthly Overview	Review expenses grouped by month
 Spending Analytics	View monthly totals and category breakdowns
 Budget Management	Set annual and category-wise budgets
 Budget Analysis	Review spending against budget limits
 Profile Management	View and update profile information
 Password Management	Change account password
 JSON API	Access application features through Flask API routes


 Built With
- Python — core application logic
- Flask — web application framework and API routes
- HTML templates — page rendering through Flask
- JSON — file-based storage for users, expenses, and budgets
- Werkzeug Security — password hashing and password verification
- SQLite — an initialization script is included for an expenses table

Project Structure
Expense-Tracker/
│
├── app.py                 # Main Flask application
├── init_db.py             # SQLite database/table initialization script
│
├── users.json             # Local user data (DO NOT COMMIT)
├── expenses.json          # Local expense data (DO NOT COMMIT)
├── budgets.json           # Local budget data (DO NOT COMMIT)
│
├── expenses.db            # Local SQLite database (DO NOT COMMIT)
├── database.db            # Local database file, if used
│
├── templates/             # HTML templates rendered by Flask
│   ├── login.html
│   ├── home.html
│   ├── monthly_overview.html
│   ├── categories.html
│   ├── budget.html
│   └── ...
│
├── static/                # CSS, JavaScript, and image assets (if present)
│
├── .gitignore
└── README.md
The template and static folders should contain the files used by your local application. The JSON and database files shown above are local data files and should not be published.
⚙️ Getting Started
1. Clone the repository
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
2. Create a virtual environment
Windows
python -m venv venv
venv\Scripts\activate
macOS / Linux
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install Flask
The application imports Flask and Werkzeug (installed with Flask). If you add more libraries to the project, include them in a requirements.txt file.
4. Configure the application
Before running the project, change the development secret key in app.py to a secure value stored in an environment variable. Do not publish real credentials or personal data.
5. Run the application
python app.py
Open your browser at:
http://127.0.0.1:5000/
🔄 How It Works
1. A user registers or logs in.
2. Flask creates a session for the authenticated user.
3. The user adds expenses with a title, amount, category, date, and optional description.
4. Expense records are saved in the application's JSON storage.
5. The application organizes expenses by category and month.
6. Users can review summaries, update records, and manage budgets.
7. Budget analysis compares recorded spending with configured budget amounts.
🔌 Main Application Areas
The Flask application includes routes for:
- Pages: home, login, about, features, blog, contact, help, privacy, terms, monthly overview, categories, profile, budget, and settings.
- Authentication APIs: registration and login.
- Expense APIs: list, add, update, delete, and category filtering.
- Statistics APIs: overall stats, category breakdown, and monthly summaries.
- Profile APIs: view/update profile, change password, and delete account.
- Budget APIs: get/set annual budget, set/delete category budgets, and budget analysis.

🔒 Important Security Notes Before Publishing
This project currently uses local JSON files for application data. Before making the repository public:
1. Do not commit users.json, expenses.json, budgets.json, or database files. They may contain private account and financial information.
2. Replace the placeholder Flask secret key with a strong environment-based secret.
3. Set debug=False when deploying.
4. Use a production-ready database and review authentication, session, input-validation, and error-handling practices before public deployment.
5. Add only sample or fictional data to screenshots and demonstrations.
Suggested .gitignore:
venv/
.venv/
__pycache__/
*.py[cod]
.env

users.json
expenses.json
budgets.json
*.db
instance/

.DS_Store
Future Enhancements
- Interactive charts and visual reports
- Export expenses to CSV or Excel
- Recurring expense reminders
- Search, sorting, and date-range filters
- Improved mobile-friendly interface
- Database-backed storage
- Downloadable monthly and yearly reports
Author
  Sudeep Rathod

Built with ❤️ using Python and Flask.

If you find this project interesting, please ⭐ the repository!
<div align="center">💡 Track Better. Spend Smarter. Save More.
</div>

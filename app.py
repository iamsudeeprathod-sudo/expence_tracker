from flask import Flask, render_template, request, jsonify, session, redirect
from datetime import datetime
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# DATABASE FILES
EXPENSES_FILE = 'expenses.json'
USERS_FILE = 'users.json'
BUDGETS_FILE = 'budgets.json'

# ===== HELPER FUNCTIONS =====

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def user_exists(username, email):
    """Check if user already exists"""
    users = load_users()
    return any(u['username'] == username or u['email'] == email for u in users)

def get_user(username):
    """Get user by username"""
    users = load_users()
    return next((u for u in users if u['username'] == username), None)

def load_expenses(username=None):
    """Load expenses from JSON file"""
    if os.path.exists(EXPENSES_FILE):
        try:
            with open(EXPENSES_FILE, 'r') as f:
                all_expenses = json.load(f)
                if username:
                    return [e for e in all_expenses if e.get('username') == username]
                return all_expenses
        except:
            return []
    return []

def save_expenses(expenses):
    """Save expenses to JSON file"""
    with open(EXPENSES_FILE, 'w') as f:
        json.dump(expenses, f, indent=4)

def load_budgets():
    """Load budget data"""
    if os.path.exists(BUDGETS_FILE):
        try:
            with open(BUDGETS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_budgets(budgets):
    """Save budget data"""
    with open(BUDGETS_FILE, 'w') as f:
        json.dump(budgets, f, indent=4)

def get_monthly_table(username=None):
    """Get expenses organized by month"""
    expenses = load_expenses(username)
    monthly_data = {}
    
    for expense in expenses:
        date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
        month_key = date_obj.strftime('%B %Y')
        
        if month_key not in monthly_data:
            monthly_data[month_key] = []
        
        monthly_data[month_key].append(expense)
    
    for month in monthly_data:
        monthly_data[month].sort(key=lambda x: x['date'], reverse=True)
    
    return monthly_data

def get_monthly_chart_data(username=None):
    """Get data for monthly chart"""
    expenses = load_expenses(username)
    monthly_totals = {}
    
    for expense in expenses:
        date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
        month_key = date_obj.strftime('%Y-%m')
        
        if month_key not in monthly_totals:
            monthly_totals[month_key] = 0
        
        monthly_totals[month_key] += expense['amount']
    
    sorted_months = sorted(monthly_totals.keys())
    labels = [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in sorted_months]
    values = [monthly_totals[m] for m in sorted_months]
    
    return labels, values

# ===== PAGE ROUTES =====

@app.route('/')
def index():
    """Home page"""
    if 'username' in session:
        return render_template('home.html')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if 'username' in session:
        return redirect('/')
    return render_template('login.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/features')
def features():
    """Features page"""
    return render_template('features.html')

@app.route('/blog')
def blog():
    """Blog page"""
    return render_template('blog.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/help')
def help_page():
    """Help center page"""
    return render_template('help.html')

@app.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

@app.route('/monthly')
def monthly_overview():
    """Monthly overview page with add expense form"""
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    monthly_table = get_monthly_table(username)
    labels, values = get_monthly_chart_data(username)
    
    return render_template('monthly_overview.html', 
                         monthly_table=monthly_table,
                         labels=labels,
                         values=values)

@app.route('/categories')
def categories():
    """Categories page with all expense categories"""
    if 'username' not in session:
        return redirect('/login')
    
    return render_template('categories.html')

@app.route('/category/<category_name>')
def category_detail(category_name):
    """Category detail page"""
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    expenses = load_expenses(username)
    category_expenses = [e for e in expenses if e['category'] == category_name]
    category_expenses.sort(key=lambda x: x['date'], reverse=True)
    
    total = sum(e['amount'] for e in category_expenses)
    
    return render_template('category.html',
                         category=category_name,
                         expenses=category_expenses,
                         total=total)

@app.route('/profile')
def profile():
    """User profile page"""
    if 'username' not in session:
        return redirect('/login')
    
    return render_template('profile.html')

@app.route('/budget')
def budget_page():
    """Budget page"""
    if 'username' not in session:
        return redirect('/login')
    
    return render_template('budget.html')

@app.route('/settings')
def settings():
    """Settings page"""
    if 'username' not in session:
        return redirect('/login')
    
    return render_template('settings.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/login')

# ===== API ROUTES - AUTHENTICATION =====

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login API"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400

        user = get_user(username)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if not check_password_hash(user['password'], password):
            return jsonify({'success': False, 'message': 'Invalid password'}), 401

        session['username'] = user['username']
        session['email'] = user['email']
        session['name'] = user['name']

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'username': user['username'],
                'email': user['email'],
                'name': user['name']
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register API"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not all([name, email, username, password]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

        if user_exists(username, email):
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 409

        users = load_users()
        new_user = {
            'id': len(users) + 1,
            'name': name,
            'email': email,
            'username': username,
            'password': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }

        users.append(new_user)
        save_users(users)

        session['username'] = new_user['username']
        session['email'] = new_user['email']
        session['name'] = new_user['name']

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'username': new_user['username'],
                'email': new_user['email'],
                'name': new_user['name']
            }
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== API ROUTES - EXPENSES =====

@app.route('/api/expenses', methods=['GET'])
def api_get_expenses():
    """Get all expenses for logged-in user"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    expenses = load_expenses(session['username'])
    expenses.sort(key=lambda x: x['date'], reverse=True)
    return jsonify({'expenses': expenses})

@app.route('/api/add-expense', methods=['POST'])
def api_add_expense():
    """Add new expense"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        
        if not data.get('title') or not data.get('amount') or not data.get('category') or not data.get('date'):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        try:
            amount = float(data.get('amount'))
            if amount <= 0:
                return jsonify({'success': False, 'message': 'Amount must be greater than 0'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid amount'}), 400
        
        expense = {
            'id': int(data.get('id', int(datetime.now().timestamp() * 1000))),
            'username': session['username'],
            'title': data.get('title').strip(),
            'amount': amount,
            'category': data.get('category'),
            'date': data.get('date'),
            'description': data.get('description', '').strip(),
            'created_at': datetime.now().isoformat()
        }
        
        expenses = load_expenses()
        expenses.insert(0, expense)
        save_expenses(expenses)
        
        return jsonify({'success': True, 'expense': expense}), 201
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete-expense/<int:expense_id>', methods=['DELETE'])
def api_delete_expense(expense_id):
    """Delete expense by ID"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        expenses = load_expenses()
        initial_count = len(expenses)
        expenses = [e for e in expenses if not (e['id'] == expense_id and e['username'] == session['username'])]
        
        if len(expenses) == initial_count:
            return jsonify({'success': False, 'message': 'Expense not found'}), 404
        
        save_expenses(expenses)
        return jsonify({'success': True, 'message': 'Expense deleted'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/update-expense/<int:expense_id>', methods=['PUT'])
def api_update_expense(expense_id):
    """Update expense by ID"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        expenses = load_expenses()
        
        for expense in expenses:
            if expense['id'] == expense_id and expense['username'] == session['username']:
                expense['title'] = data.get('title', expense['title'])
                expense['amount'] = float(data.get('amount', expense['amount']))
                expense['category'] = data.get('category', expense['category'])
                expense['date'] = data.get('date', expense['date'])
                expense['description'] = data.get('description', expense['description'])
                expense['updated_at'] = datetime.now().isoformat()
                
                save_expenses(expenses)
                return jsonify({'success': True, 'expense': expense})
        
        return jsonify({'success': False, 'message': 'Expense not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/category/<category_name>', methods=['GET'])
def api_get_category(category_name):
    """Get expenses by category for logged-in user"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    expenses = load_expenses(session['username'])
    category_expenses = [e for e in expenses if e['category'] == category_name]
    category_expenses.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify(category_expenses)

# ===== API ROUTES - STATISTICS =====

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """Get statistics for logged-in user"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    expenses = load_expenses(session['username'])
    today = datetime.now().strftime('%Y-%m')
    
    all_time_total = sum(e['amount'] for e in expenses)
    monthly_total = sum(e['amount'] for e in expenses if e['date'].startswith(today))
    
    category_totals = {}
    for expense in expenses:
        cat = expense['category']
        category_totals[cat] = category_totals.get(cat, 0) + expense['amount']
    
    return jsonify({
        'monthlyTotal': monthly_total,
        'allTimeTotal': all_time_total,
        'categoryTotals': category_totals,
        'totalExpenses': len(expenses)
    })

@app.route('/api/category-breakdown', methods=['GET'])
def api_category_breakdown():
    """Get category breakdown with detailed stats"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    expenses = load_expenses(session['username'])
    
    categories = {}
    for expense in expenses:
        cat = expense['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'count': 0, 'expenses': []}
        
        categories[cat]['total'] += expense['amount']
        categories[cat]['count'] += 1
        categories[cat]['expenses'].append(expense)
    
    return jsonify({'success': True, 'categories': categories})

@app.route('/api/monthly-summary', methods=['GET'])
def api_monthly_summary():
    """Get monthly summary for analytics"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    expenses = load_expenses(session['username'])
    
    monthly_data = {}
    for expense in expenses:
        month = expense['date'][:7]
        
        if month not in monthly_data:
            monthly_data[month] = {'total': 0, 'count': 0, 'categories': {}}
        
        monthly_data[month]['total'] += expense['amount']
        monthly_data[month]['count'] += 1
        
        cat = expense['category']
        if cat not in monthly_data[month]['categories']:
            monthly_data[month]['categories'][cat] = 0
        monthly_data[month]['categories'][cat] += expense['amount']
    
    return jsonify({'success': True, 'monthly_data': monthly_data})

# ===== API ROUTES - PROFILE =====

@app.route('/api/profile', methods=['GET'])
def api_profile():
    """Get profile information for logged-in user"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user = get_user(session['username'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': {
            'name': user['name'],
            'email': user['email'],
            'username': user['username'],
            'created_at': user.get('created_at', datetime.now().isoformat())
        }
    })

@app.route('/api/update-profile', methods=['PUT'])
def api_update_profile():
    """Update user profile"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        users = load_users()
        
        for user in users:
            if user['username'] == session['username']:
                user['name'] = data.get('name', user['name'])
                user['email'] = data.get('email', user['email'])
                user['phone'] = data.get('phone', '')
                user['address'] = data.get('address', '')
                user['city'] = data.get('city', '')
                user['state'] = data.get('state', '')
                user['zip'] = data.get('zip', '')
                user['bio'] = data.get('bio', '')
                user['updated_at'] = datetime.now().isoformat()
                
                save_users(users)
                session['email'] = user['email']
                session['name'] = user['name']
                
                return jsonify({
                    'success': True,
                    'user': {
                        'name': user['name'],
                        'email': user['email'],
                        'username': user['username']
                    }
                })
        
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/change-password', methods=['POST'])
def api_change_password():
    """Change user password"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not old_password or not new_password or not confirm_password:
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        user = get_user(session['username'])
        
        if not check_password_hash(user['password'], old_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401
        
        users = load_users()
        for u in users:
            if u['username'] == session['username']:
                u['password'] = generate_password_hash(new_password)
                u['updated_at'] = datetime.now().isoformat()
                save_users(users)
                return jsonify({'success': True, 'message': 'Password changed successfully'})
        
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete-account', methods=['DELETE'])
def api_delete_account():
    """Delete user account"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        password = data.get('password', '')
        
        user = get_user(session['username'])
        
        if not check_password_hash(user['password'], password):
            return jsonify({'success': False, 'message': 'Password is incorrect'}), 401
        
        users = load_users()
        users = [u for u in users if u['username'] != session['username']]
        save_users(users)
        
        expenses = load_expenses()
        expenses = [e for e in expenses if e.get('username') != session['username']]
        save_expenses(expenses)
        
        session.clear()
        
        return jsonify({'success': True, 'message': 'Account deleted successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== API ROUTES - BUDGET =====

@app.route('/api/budget', methods=['GET'])
def api_get_budget():
    """Get budget data"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    budgets = load_budgets()
    user_budget = budgets.get(session['username'], {
        'year': datetime.now().year,
        'annual_budget': 500000,
        'category_budgets': {}
    })
    
    return jsonify({
        'success': True,
        'budget': user_budget
    })

@app.route('/api/set-budget', methods=['POST'])
def api_set_budget():
    """Set annual budget"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        year = data.get('year')
        annual_budget = float(data.get('annual_budget', 500000))
        
        if annual_budget <= 0:
            return jsonify({'success': False, 'message': 'Invalid budget amount'}), 400
        
        budgets = load_budgets()
        
        if session['username'] not in budgets:
            budgets[session['username']] = {
                'year': year,
                'annual_budget': annual_budget,
                'category_budgets': {}
            }
        else:
            budgets[session['username']]['year'] = year
            budgets[session['username']]['annual_budget'] = annual_budget
        
        save_budgets(budgets)
        
        return jsonify({'success': True, 'message': 'Budget updated'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/set-category-budget', methods=['POST'])
def api_set_category_budget():
    """Set category budget"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        category = data.get('category')
        budget_amount = float(data.get('budget_amount', 0))
        
        if not category or budget_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid data'}), 400
        
        budgets = load_budgets()
        
        if session['username'] not in budgets:
            budgets[session['username']] = {
                'year': datetime.now().year,
                'annual_budget': 500000,
                'category_budgets': {}
            }
        
        budgets[session['username']]['category_budgets'][category] = budget_amount
        save_budgets(budgets)
        
        return jsonify({'success': True, 'message': 'Category budget updated'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete-category-budget/<category>', methods=['DELETE'])
def api_delete_category_budget(category):
    """Delete category budget"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        budgets = load_budgets()
        
        if session['username'] in budgets:
            if category in budgets[session['username']]['category_budgets']:
                del budgets[session['username']]['category_budgets'][category]
                save_budgets(budgets)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/budget-analysis', methods=['GET'])
def api_budget_analysis():
    """Get detailed budget analysis"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    budgets = load_budgets()
    user_budget = budgets.get(session['username'], {
        'annual_budget': 500000,
        'category_budgets': {}
    })
    
    expenses = load_expenses(session['username'])
    
    analysis = {
        'annual_budget': user_budget['annual_budget'],
        'total_spent': sum(e['amount'] for e in expenses),
        'category_analysis': {}
    }
    
    for category, budget in user_budget['category_budgets'].items():
        spent = sum(e['amount'] for e in expenses if e['category'] == category)
        analysis['category_analysis'][category] = {
            'budget': budget,
            'spent': spent,
            'remaining': budget - spent,
            'percentage': (spent / budget * 100) if budget > 0 else 0
        }
    
    return jsonify({'success': True, 'analysis': analysis})

# ===== API ROUTES - CONTACT =====

@app.route('/contact-submit', methods=['POST'])
def submit_contact():
    """Submit contact form"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        
        # Here you can add email sending logic or save to database
        # For now, just return success
        return jsonify({'success': True, 'message': 'Message sent successfully! We will get back to you soon.'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """500 error handler"""
    return jsonify({'error': 'Server error'}), 500

# ===== MAIN =====

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
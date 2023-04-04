import unittest
import sqlite3
import json
import os
import matplotlib.pyplot as plt


# Create Database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


# TASK 1
# CREATE TABLE FOR EMPLOYEE INFORMATION IN DATABASE AND ADD INFORMATION
def create_employee_table(cur, conn):
    cur.execute("""CREATE TABLE IF NOT EXISTS employees 
                (employee_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                job_id INTEGER,
                hire_date TEXT,
                salary INTEGER)""")
    conn.commit()


# ADD EMPLOYEE'S INFORMATION TO THE TABLE
def add_employee(filename, cur, conn):
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), filename))) as f:
        employees = json.load(f)
        for employee in employees:
            cur.execute("INSERT OR IGNORE INTO employees (employee_id, first_name, last_name, job_id, hire_date, salary) VALUES (?, ?, ?, ?, ?, ?)",
                        (employee['employee_id'],
                         employee['first_name'],
                         employee['last_name'],
                         employee['job_id'],
                         employee['hire_date'],
                         employee['salary']))
    conn.commit()


# TASK 2: GET JOB AND HIRE_DATE INFORMATION
def job_and_hire_date(cur, conn):
    cur.execute("""SELECT hire_date, Jobs.job_title FROM Employees
                JOIN Jobs ON Employees.job_id = Jobs.job_id
                ORDER BY hire_date
                """)
    return cur.fetchone()[1]


# TASK 3: IDENTIFY PROBLEMATIC SALARY DATA
# Apply JOIN clause to match individual employees
def problematic_salary(cur, conn):
    cur.execute("""SELECT first_name, last_name FROM Employees
                JOIN Jobs ON Employees.job_id = Jobs.job_id
                WHERE salary < Jobs.min_salary OR salary > Jobs.max_salary
                """)
    return cur.fetchall()


# TASK 4: VISUALIZATION
def visualization_salary_data(cur, conn):
    cur.execute("""SELECT Jobs.job_title, salary FROM Employees
                JOIN Jobs ON Employees.job_id = Jobs.job_id
                """)
    xs, ys = zip(*cur.fetchall())
    cur.execute("SELECT job_title, min_salary, max_salary FROM Jobs")
    jobs, min_sals, max_sals = zip(*cur.fetchall())
    
    plt.figure(figsize=(10, 5))
    plt.xticks(rotation=45)
    plt.scatter(xs, ys)
    plt.scatter(jobs, min_sals, color='red', marker='x')
    plt.scatter(jobs, max_sals, color='red', marker='x')
    plt.show()


class TestDiscussion12(unittest.TestCase):
    def setUp(self) -> None:
        self.cur, self.conn = setUpDatabase('HR.db')

    def test_create_employee_table(self):
        self.cur.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='employees'")
        table_check = self.cur.fetchall()[0][0]
        self.assertEqual(
            table_check, 1, "Error: 'employees' table was not found")
        self.cur.execute("SELECT * FROM employees")
        count = len(self.cur.fetchall())
        self.assertEqual(count, 13)

    def test_job_and_hire_date(self):
        self.assertEqual('President', job_and_hire_date(self.cur, self.conn))

    def test_problematic_salary(self):
        sal_list = problematic_salary(self.cur, self.conn)
        self.assertIsInstance(sal_list, list)
        self.assertEqual(sal_list[0], ('Valli', 'Pataballa'))
        self.assertEqual(len(sal_list), 4)


def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('HR.db')
    create_employee_table(cur, conn)

    # ADD EMPLOYEES
    add_employee("employee.json", cur, conn)

    # GET FIRST JOB AND HIRE DATE
    dates = job_and_hire_date(cur, conn)
    print("Job for earliest hire date:", dates)

    # IDENTIFY PROBLEMATIC SALARIES
    wrong_salary = (problematic_salary(cur, conn))
    print("Employees with problematic salaries:\n", wrong_salary)
    
    # VISUALIZE SALARY DATA
    visualization_salary_data(cur, conn)


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)

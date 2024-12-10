from __init__ import CURSOR, CONN
from department import Department
from employee import Employee
import sqlite3

def get_connection():
    # This returns a connection to the SQLite database
    return sqlite3.connect('your_database.db')


class Review:
    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        if not isinstance(year, int):
            raise ValueError("Year must be an integer")
        if year < 2000:
            raise ValueError("Year must be >= 2000")
        if not isinstance(summary, str) or len(summary) == 0:
            raise ValueError("Summary must be a non-empty string")

        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        return cls(row[1], row[2], row[3], row[0])

    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id=?", (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def save(self):
        if self.id is None:
            CURSOR.execute("INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)", 
                           (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
            CONN.commit()
        else:
            CURSOR.execute("UPDATE reviews SET year=?, summary=?, employee_id=? WHERE id=?", 
                           (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    def delete(self):
        if self.id is None:
            raise ValueError("Cannot delete a review that has not been saved.")
        CURSOR.execute("DELETE FROM reviews WHERE id=?", (self.id,))
        CONN.commit()
        self.id = None

    def update(self):
        CURSOR.execute("UPDATE reviews SET year=?, summary=?, employee_id=? WHERE id=?", 
                       (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    @classmethod
    def clear_cache(cls):
        print("Clearing cache...")
        cls.all = {}

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        # Ensure the employee ID exists in the employee table
        if Employee.find_by_id(employee_id):
            self._employee_id = employee_id
        else:
            raise ValueError(f"Employee with ID {employee_id} does not exist")
    
    # Inside any method in review.py where Employee is needed
    def some_method(self):
        from employee import Employee  # Delay the import
        employee = Employee.find_by_id(self.employee_id)
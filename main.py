#Imports
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication,  QWidget, QMainWindow, QLabel,  QPushButton, QVBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDateEdit, QLineEdit, QHBoxLayout
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from sys import exit

# Main Class:
class FitTrack(QWidget):
    def __init__(self):
        super().__init__()
        self.settings()  # calling the method
        self.initUI()   # calling the method
        self.button_click()

    def settings(self):
        self.setWindowTitle("FitTrack")
        self.resize(800, 600)

    # init UI
    def initUI(self):
        self.date_box = QDateEdit(self)
        self.date_box.setDate(QDate.currentDate())

        self.kal_box = QLineEdit()
        self.kal_box.setPlaceholderText("Number of Burned Calories")

        self.distance_box = QLineEdit()
        self.distance_box.setPlaceholderText("Enter distance ran")

        self.description = QLineEdit()
        self.description.setPlaceholderText("Enter description")

        self.submit_btn = QPushButton("Submit", self)
        self.submit_btn.setStyleSheet("background-color: #4caf50; color: #fff;")
        self.add_btn = QPushButton("Add", self)
        self.add_btn.setStyleSheet("background-color: #4caf50; color: #fff;")
        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.setStyleSheet("background-color: #f44336; color: #fff;")
        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.setStyleSheet("background-color: #f44336; color: #fff;")
        self.dark_mode = QCheckBox("Dark Mode", self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Id","Date", "Calories", "Distance", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        # Design Layout
        self.master_layout = QHBoxLayout()
        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()

        self.sub_row1 = QHBoxLayout()
        self.sub_row2 = QHBoxLayout()
        self.sub_row3 = QHBoxLayout()
        self.sub_row4 = QHBoxLayout()

        self.sub_row1.addWidget(QLabel("Date:"))
        self.sub_row1.addWidget(self.date_box)

        self.sub_row2.addWidget(QLabel("Calories:"))
        self.sub_row2.addWidget(self.kal_box)

        self.sub_row3.addWidget(QLabel("Distance:"))
        self.sub_row3.addWidget(self.distance_box)

        self.sub_row4.addWidget(QLabel("Description:"))
        self.sub_row4.addWidget(self.description)

        self.col1.addLayout(self.sub_row1)
        self.col1.addLayout(self.sub_row2)
        self.col1.addLayout(self.sub_row3)
        self.col1.addLayout(self.sub_row4)
        self.col1.addWidget(self.dark_mode)

        btn_row1 = QHBoxLayout()
        btn_row2 = QHBoxLayout()


        btn_row1.addWidget(self.add_btn)
        btn_row1.addWidget(self.delete_btn)
        btn_row2.addWidget(self.submit_btn)
        btn_row2.addWidget(self.clear_btn)

        self.col1.addLayout(btn_row1)
        self.col1.addLayout(btn_row2)

        self.col2.addWidget(self.canvas)
        self.col2.addWidget(self.table)

        self.master_layout.addLayout(self.col1, 30)
        self.master_layout.addLayout(self.col2, 70)
        self.setLayout(self.master_layout)

        self.apply_styles()
        self.load_tables()
        
    # Events

    def button_click(self):
        self.add_btn.clicked.connect(self.add_workout)
        self.delete_btn.clicked.connect(self.delete_workout)
        self.submit_btn.clicked.connect(self.calculate_calories)
        self.dark_mode.stateChanged.connect(self.toggle_dark)
        self.clear_btn.clicked.connect(self.reset)

    # Load Tables 
    def load_tables(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT * FROM fittrack ORDER BY date DESC")
        row = 0
        while query.next():
            fit_id = query.value(0)
            date = query.value(1)
            calories = query.value(2)
            distance = query.value(3)
            description = query.value(4)

            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(fit_id)))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(str(calories)))
            self.table.setItem(row, 3, QTableWidgetItem(str(distance)))
            self.table.setItem(row, 4, QTableWidgetItem(description))
            row += 1
        
    # Add Tables
    def add_workout(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        calories = self.kal_box.text()
        distance = self.distance_box.text()
        description = self.description.text()

    

        query = QSqlQuery("""
                          INSERT INTO fittrack (date, calories, distance, description)
                          VALUES (?, ?, ?, ?)
        """)
        
        query.addBindValue(date)
        query.addBindValue(calories)
        query.addBindValue(distance)
        query.addBindValue(description)

        query.exec_()

        self.date_box.setDate(QDate.currentDate())
        self.kal_box.clear()
        self.distance_box.clear()
        self.description.clear()

        self.load_tables()

    # Delete Tables
    def delete_workout(self):
        selected_row = self.table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "Delete Error", "Please select a row to delete.")
            return
        fit_id =int(self.table.item(selected_row, 0).text())
        confirm = QMessageBox.question(self, "Delete Confirmation", "Are you sure you want to delete this entry?", QMessageBox.Yes | QMessageBox.No) 
          
        if confirm == QMessageBox.No:
            return
        query = QSqlQuery()
        query.prepare("DELETE FROM fittrack WHERE id = ?")
        query.addBindValue(fit_id)
        query.exec_() 

        self.load_tables()

    # Calculate Calories
    def calculate_calories(self):
        distances = []
        calories = []

        query = QSqlQuery("SELECT distance, calories FROM fittrack")
        while query.next():
            distance = query.value(0)
            calorie = query.value(1)
            distances.append(distance)
            calories.append(calorie)

        try:
            min_calories = min(calories)
            max_calories = max(calories)
            normalized_calories = [(calorie - min_calories) / (max_calories - min_calories) for calorie in calories]

            plt.style.use("Solarize_Light2")
            ax = self.figure.add_subplot()
            ax.scatter(distances, calories, c=normalized_calories, cmap="viridis", label="Data Points")     
            ax.set_xlabel("Distance")
            ax.set_ylabel("Calories")
            ax.set_title("Calories vs Distance")
            cbar = ax.figure.colorbar(ax.collections[0], label="Normalized Calories")
            ax.legend()
            self.canvas.draw()
        except Exception as e:
            print("ERROR: {e}")
            QMessageBox.warning(self, "Error", "No data available to calculate calories.")

    # Style
    def apply_styles(self):
        self.setStyleSheet(""" 
            QWidget {
                background-color: #b8c9e1;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QPushButton {
                background-color: #4caf50;
                color: #fff;
                font-size: 14px;
                border: none;
                padding: 8px 16px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QDateEdit, QComboBox {
                background-color: #b8c9e1;
                color: #333;
                border: 1px solid #444;
                padding: 5px;
                           
            QTableWidget {
                background-color: #b8c9e1;
                color: #333;
                border: 1px solid #444;
                selection-background-color: #ddd;
            }
""")
        figure_color = "#b8c9e1"
        self.figure.patch.set_facecolor(figure_color)
        self.canvas.setStyleSheet(f"background-color: {figure_color};")

        if self.dark_mode.isChecked():
            self.setStyleSheet(""" 
                FitTrack {
                    background-color: #2e2e2e;
                }
                               
                QWidget {
                    background-color: #2e2e2e;
                }
                QLabel {
                    font-size: 14px;
                    color: #fff;
                }
                QPushButton {
                    background-color: #4caf50;
                    color: #fff;
                    font-size: 14px;
                    border: none;
                    padding: 8px 16px;
                }
                
                QPushButton:hover {
                    background-color: #45a049;
                }
                QLineEdit, QDateEdit, QComboBox {
                    background-color: #444;
                    color: #fff;
                    border: 1px solid #666;
                    padding: 5px;
                }
                
            """)
            figure_color = "#40484c"
            self.figure.patch.set_facecolor(figure_color)
            self.canvas.setStyleSheet(f"background-color: {figure_color};")
   
    # Dark Mode 

    def toggle_dark(self):
        self.apply_styles()

    # Reset
    def reset(self):
        self.kal_box.clear()
        self.distance_box.clear()
        self.description.clear()
        self.date_box.setDate(QDate.currentDate())
        self.figure.clear()
        self.canvas.draw()
        

# Initialize my DB

db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("fittrack.db")

if not db.open():
    QMessageBox.critical(None, "Database Error", "Could not open database.")
    exit(2)

query = QSqlQuery()
query.exec_(""" 
CREATE TABLE IF NOT EXISTS fittrack (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    calories REAL,
    distance REAL,
    description TEXT
)""")


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("Fusion")
    main = FitTrack()
    main.show()
    app.exec_()
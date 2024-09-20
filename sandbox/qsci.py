import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
from enum import Enum

sql_styles = [ # nb: blanks cannot be removed
    'Default', 'Comment', 'Comment line', 'JavaDoc style comment', 'Number', 'Keyword', 'Double-quoted string', 
    'Single-quoted string', 'SQL*Plus keyword', 'SQL*Plus prompt', 'Operator', 'Identifier', '', 'SQL*Plus comment', '', 
    '# comment line', '', 'JavaDoc keyword', 'JavaDoc keyword error', 'User defined 1', 'User defined 2', 'User defined 3', 
    'User defined 4', 'Quoted identifier', 'Quoted operator']

class CustomMainWindow(QMainWindow):
    def __init__(self):
        super(CustomMainWindow, self).__init__()

        # Window setup
        # --------------

        # 1. Define the geometry of the main window
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("QScintilla Test")

        # 2. Create frame and layout
        self.__frm = QFrame(self)
        # self.__frm.setStyleSheet("QWidget { background-color: #ffeaeaea }")
        self.__lyt = QVBoxLayout()
        self.__frm.setLayout(self.__lyt)
        self.setCentralWidget(self.__frm)
        self.__myFont = QFont()
        self.__myFont.setPointSize(14)

        # 3. Place a button
        self.__btn = QPushButton("Qsci")
        self.__btn.setFixedWidth(50)
        self.__btn.setFixedHeight(50)
        self.__btn.clicked.connect(self.__btn_action)
        self.__btn.setFont(self.__myFont)
        self.__lyt.addWidget(self.__btn)

        # QScintilla editor setup
        # ------------------------

        # ! Make instance of QsciScintilla class!
        self.__editor = QsciScintilla()
        self.__editor.setText("""
WITH cte AS (
    SELECT col0_1, col0_2, col00_2 FROM tree
)
SELECT 
    cte.col00_2,
    col10_2,
    (SELECT sum(col20_2) FROM tree)
--comment from from 
FROM cte 
join tree ON tree.col_1 = cte.col0_1
""")
        self.__editor.setLexer(None)
        self.__editor.setUtf8(True)  # Set encoding to UTF-8
        self.__editor.setFont(self.__myFont)  # Will be overridden by lexer!


        # self.__lexer = QsciLexerPython(self.__editor)
        self.__lexer = QsciLexerSQL(self.__editor)
        self.__editor.setColor(QColor(50))
        # self.__editor.sci_set
        # self.__editor.setStyleSheet("color: rgb(50, 50, 50);")
        # self.__editor.
        self.__editor.setLexer(self.__lexer)
        self.__editor.setPaper(QColor(0, 0, 0))  # Dark background
        self.color1 = "#abb2bf"
        self.color2 = "#282c34"
        self.__lexer.setDefaultColor(QColor(50, 250, 50)) # no clue what this does
        self.__lexer.setDefaultPaper(QColor(self.color2)) # this is the background color (except where text is located)

        self.__lexer.setDefaultFont(QFont("Consolas", 14))
        # sql_styles = []
        # for i in range(30):
        #     d = self.__lexer.description(i)
        #     sql_styles.append(d)
        #     # print('   ', d, '=', i)
        # print(sql_styles) 
        for i, s in enumerate(sql_styles):
            self.__lexer.setPaper(QColor(self.color2), i)       

        self.__editor.setCaretForegroundColor(QColor("#dedcdc")) 
        self.__editor.setCaretLineBackgroundColor(QColor("#2c313c")) # color for the current line
        # ! Add editor to layout !
        self.__lyt.addWidget(self.__editor)

        self.__editor.setCaretLineVisible(True)
        self.__editor.setCaretLineBackgroundColor(QColor(250, 50, 50))
        # self.default = 0
        # self.keyword = 1
        # self.types = 2
        # self.string = 3
        # self.keyargs = 4
        # self.brackets = 5
        # self.comments = 6
        # self.constants = 7
        # self.functions = 8
        # self.classes = 9
        # self.function_def = 10

        # Comment = 1
        # CommentDoc = 3
        # CommentDocKeyword = 17
        # CommentDocKeywordError = 18
        # CommentLine = 2
        # CommentLineHash = 15
        # Default = 0
        # DoubleQuotedString = 6
        # Identifier = 11


        # # styles
        # self.__lexer.setColor(QColor(self.color1), self.default)
        # self.__lexer.setColor(QColor("#c678dd"), self.keyword)
        # self.__lexer.setColor(QColor("#56b6c2"), self.types)
        # self.__lexer.setColor(QColor("#98c379"), self.string)
        # self.__lexer.setColor(QColor("#c678dd"), self.keyargs)
        # self.__lexer.setColor(QColor("#c678dd"), self.brackets)
        # self.__lexer.setColor(QColor("#777777"), self.comments)
        # self.__lexer.setColor(QColor("#d19a5e"), self.constants)
        # self.__lexer.setColor(QColor("#61afd1"), self.functions)
        # self.__lexer.setColor(QColor("#c68f55"), self.classes)
        # self.__lexer.setColor(QColor("#61afd1"), self.function_def)

        # # paper color
        # self.__lexer.setPaper(QColor(self.color2), self.default)
        # self.__lexer.setPaper(QColor(self.color2), self.keyword)
        # self.__lexer.setPaper(QColor(self.color2), self.types)
        # self.__lexer.setPaper(QColor(self.color2), self.string)
        # self.__lexer.setPaper(QColor(self.color2), self.keyargs)
        # self.__lexer.setPaper(QColor(self.color2), self.brackets)
        # self.__lexer.setPaper(QColor(self.color2), self.comments)
        # self.__lexer.setPaper(QColor(self.color2), self.constants)
        # self.__lexer.setPaper(QColor(self.color2), self.functions)
        # self.__lexer.setPaper(QColor(self.color2), self.classes)
        # self.__lexer.setPaper(QColor(self.color2), self.function_def)

        # # font
        # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.default)
        # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.keyword)
        # # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.types)
        # # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.string)
        # # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.keyargs)
        # # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.brackets)
        # # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.comments)
        # # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.constants)
        # # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.functions)
        # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.classes)
        # self.__lexer.setFont(QFont("Consolas", 14, weight=QFont.Bold), self.function_def)

        self.show()


    def __btn_action(self):
        print("Hello World!")




if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec_())

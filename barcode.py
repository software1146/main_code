import sys
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from io import BytesIO


left_odd = {
    '0': '0001101', '1': '0011001', '2': '0010011',
    '3': '0111101', '4': '0100011', '5': '0110001',
    '6': '0101111', '7': '0111011', '8': '0110111',
    '9': '0001011'
}
left_even = {
    '0': '0100111', '1': '0110011', '2': '0011011',
    '3': '0100001', '4': '0011101', '5': '0111001',
    '6': '0000101', '7': '0010001', '8': '0001001',
    '9': '0010111'
}
right_even = {
    '0': '1110010', '1': '1100110', '2': '1101100',
    '3': '1000001', '4': '1011100', '5': '1001110',
    '6': '1010000', '7': '1000100', '8': '1001000',
    '9': '1110100'
}
oddeven = [
    [0,0,0,0,0,0],[0,0,1,0,1,1],[0,0,1,1,0,1],[0,0,1,1,1,0],
    [0,1,0,0,1,1],[0,1,1,0,0,1],[0,1,1,1,0,0],[0,1,0,1,0,1],
    [0,1,0,1,1,0],[0,1,1,0,1,0]
]

def generate_ean13_barcode(barcode_number):
    first_num = int(barcode_number[0])
    barcode_list = []
    barcode_list.append('101')
    left_digits = barcode_number[:6]
    for i in range(6):
        if oddeven[first_num][i] == 0:
            barcode_list.append(left_odd[left_digits[i]])
        else:
            barcode_list.append(left_even[left_digits[i]])
    barcode_list.append('01010')
    right_digits = barcode_number[6:]
    for digit in right_digits:
        barcode_list.append(right_even[digit])
    barcode_list.append('101')
    barcode_string = ''.join(barcode_list)
    return barcode_string

def plot_barcode(barcode_string):
    plt.figure(figsize=(12, 2))
    plt.bar(range(len(barcode_string)), [int(bit) for bit in barcode_string], width=1, color='black')
    plt.axis('off')
    plt.xticks([])
    plt.yticks([])
    
     
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close()
    
    return buf

def check_digital_verification(barcode):
    if len(barcode) != 13 or not barcode.isdigit():
        raise ValueError("EAN-13 바코드는 13자리 숫자입니다.다시 알맞게 수정하세요.")
    digits = list(map(int, barcode[:12]))
    total_sum = sum(digits[i] * 3 if i % 2 == 0 else digits[i] for i in range(12))
    check_digit = (10 - (total_sum % 10)) %10
    return check_digit

def barcode_verification(barcode):
    if len(barcode) != 13 or not barcode.isdigit():
        return False
    check_digit = check_digital_verification(barcode)
    return check_digit == int(barcode[-1])

class BarcodeApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('EAN-13 바코드 생성기')
        
        self.layout = QVBoxLayout()
        
        self.label = QLabel('생성을 원하시는 EAN-13바코드 코드를 입력해주세요(띄어쓰기 없이 입력하세요):')
        self.layout.addWidget(self.label)
        
        self.text_input = QLineEdit()
        self.layout.addWidget(self.text_input)
        
        self.generate_button = QPushButton('바코드 생성')
        self.generate_button.clicked.connect(self.generate_barcode)
        self.layout.addWidget(self.generate_button)
        
        self.save_button = QPushButton('이미지 저장')
        self.save_button.clicked.connect(self.save_barcode_image)
        self.layout.addWidget(self.save_button)
        
        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)
        
        self.setLayout(self.layout)
    
    def generate_barcode(self):
        barcode_number = self.text_input.text().strip()
        
        if barcode_verification(barcode_number):
            self.barcode_number = barcode_number
            barcode_string = generate_ean13_barcode(barcode_number)
            buf = plot_barcode(barcode_string)
            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("유효하지 않은 EAN-13바코드 입니다.")
    
    def save_barcode_image(self):
        if hasattr(self, 'barcode_number'):
            barcode_string = generate_ean13_barcode(self.barcode_number)
            buf = plot_barcode(barcode_string)
            
            
            file_name = f"{self.barcode_number}.jpg"
            with open(file_name, 'wb') as f:
                f.write(buf.getvalue())
            
            self.image_label.setText(f"이미지가 '{file_name}'로 저장되었습니다.")
        else:
            self.image_label.setText(f"이미지 저장 실패, 바코드 생성 이후에 이미지를 생성할수 있습니다.")

app = QApplication(sys.argv)
window = BarcodeApp()
window.show()
sys.exit(app.exec_())

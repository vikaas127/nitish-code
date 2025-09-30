from tkinter import *
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import pytesseract
import re
import os

class BusinessCardScanner:
    def __init__(self, root):
        self.root = root
        self.root.geometry('950x750')
        self.root.title('Business Card Scanner')

        # Title and Developer label
        Label(root, text='Business Card Scanner', font=('Helvetica', 28, 'bold'), fg='#2E8B57').pack(pady=(18, 4))
        Label(root, text='Developed By Nitish Bhatia', font=('Arial', 13, 'italic'), fg='#7f8c8d').pack(pady=(0, 15))

        # Status Label
        self.status_var = StringVar(value='Upload a business card image (JPG, PNG)')
        Label(root, textvariable=self.status_var, font=('Arial', 13, 'bold'), fg='#154360').pack(pady=5)

        # Buttons Frame
        btn_frame = Frame(root)
        btn_frame.pack(pady=5)
        Button(btn_frame, text='Browse Card Image', command=self.upload_file,
               font=('Arial', 13), bg='#27ae60', fg='white', width=20).pack(side=LEFT, padx=5)
        self.scan_btn = Button(root, text='Scan and Extract', command=self.scan_image,
                               font=('Arial', 15, 'bold'), bg='#2980b9', fg='white', width=25)
        self.scan_btn.pack(pady=20)
        self.scan_btn.config(state=DISABLED)

        # Image Preview
        self.img_preview = Label(root)
        self.img_preview.pack()

        # Treeview for Fields and Values
        columns = ('Field', 'Value')
        self.tree = ttk.Treeview(root, columns=columns, show='headings', height=15)
        style = ttk.Style()
        style.configure('Treeview.Heading', font=('Arial', 14, 'bold'), foreground='#2980b9')
        style.configure('Treeview', font=('Arial', 12))
        self.tree.heading('Field', text='Field')
        self.tree.heading('Value', text='Value')
        self.tree.column('Field', width=220, anchor=W)
        self.tree.column('Value', width=640, anchor=W)
        self.tree.pack(padx=20, pady=20, fill=BOTH, expand=True)

    def upload_file(self):
        self.filename = filedialog.askopenfilename(
            initialdir=os.path.expanduser("~"),
            title='Select Business Card Image',
            filetypes=[('Image files', '*.jpg *.jpeg *.png')]
        )
        if not self.filename:
            self.status_var.set('No image selected.')
            self.scan_btn.config(state=DISABLED)
            self.img_preview.config(image='')
            return
        self.status_var.set(f'Selected: {os.path.basename(self.filename)}')
        self.scan_btn.config(state=NORMAL)

        img = Image.open(self.filename)
        img.thumbnail((340, 180))
        self.img_disp = ImageTk.PhotoImage(img)
        self.img_preview.config(image=self.img_disp)
        self.img_preview.photo_ref = self.img_disp

    def scan_image(self):
        if not self.filename:
            messagebox.showerror('No Image', 'Please upload a business card image first')
            return
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust to tesseract path
            text = pytesseract.image_to_string(self.filename)
            self.status_var.set('Scan completed. Displaying results.')
            for row in self.tree.get_children():
                self.tree.delete(row)
            data = self.extract_data(text)
            for field, value in data.items():
                self.tree.insert('', END, values=(field, value))
        except Exception as e:
            messagebox.showerror('Error', f'Failed to process image:\n{e}')

    def extract_data(self, text):
        data = {}

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Name heuristic: first line with letters only, >=2 words, no digits or URLs
        name = ''
        for line in lines:
            if not re.search(r'(@|http|www|phone|fax|[0-9])', line, re.I) and re.match(r'^[A-Za-z\s.]+$', line) and len(line.split()) > 1:
                name = line
                break
        if name:
            data['Name'] = name

        # Phone numbers: regex matches
        phones = re.findall(r'(\+?\d[\d\s().-]{7,}\d)', text)
        if phones:
            data['Phone numbers'] = ', '.join(phones)

        # Emails: regex matches
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        if emails:
            data['Emails'] = ', '.join(emails)

        # Websites: regex matches
        urls = re.findall(r'(https?://[^\s]+|www\.[^\s]+)', text)
        if urls:
            data['Websites'] = ', '.join(urls)

        # Addresses: lines containing common address keywords
        addr_keys = ['street', 'st.', 'road', 'rd.', 'ave', 'avenue', 'blvd', 'suite', 'po box', 'postal',
                     'pincode', 'city', 'state', 'zip', 'district', 'lane', 'apartment', 'country']
        address_lines = [line for line in lines if any(k in line.lower() for k in addr_keys)]
        if address_lines:
            data['Address'] = ', '.join(address_lines)

        # Country heuristic from known country names in lines
        countries = ['united states', 'usa', 'uk', 'india', 'canada', 'australia', 'germany', 'france', 'china', 'japan']
        for c in countries:
            for line in lines:
                if c in line.lower():
                    data['Country'] = c.title()
                    break

        # City heuristic from known cities in lines
        cities = ['new york', 'london', 'mumbai', 'delhi', 'toronto', 'sydney', 'berlin', 'paris', 'beijing', 'moscow']
        for city in cities:
            for line in lines:
                if city in line.lower():
                    data['City'] = city.title()
                    break

        # Pin Code: 5 or 6 digit numbers
        pincodes = re.findall(r'\b\d{5,6}\b', text)
        if pincodes:
            data['Pin Code'] = pincodes[0]

        return data

if __name__ == '__main__':
    root = Tk()
    app = BusinessCardScanner(root)
    root.mainloop()

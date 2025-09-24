from tkinter import *
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import pytesseract
import re
import os

class BusinessCardScanner:
    def __init__(self, root):
        self.root = root
        self.root.geometry('950x700')
        self.root.title("Business Card Scanner")

        # Title and credits
        Label(root, text="Business Card Scanner", font=("Helvetica", 28, "bold"), fg="#2754b5").pack(pady=(18,2))
        Label(root, text="Developed By Nitish Bhatia", font=("Arial", 13, "italic"), fg="#888").pack(pady=(0,15))

        # Status
        self.status_var = StringVar(value="Upload a business card image (JPG, PNG)")
        Label(root, textvariable=self.status_var, font=("Arial", 13, "bold"), fg="#154360").pack(pady=5)

        # Upload and Scan
        f_btns = Frame(root)
        f_btns.pack(pady=2)
        Button(f_btns, text="Browse Card Image", command=self.upload_file,
               font=("Arial", 13), bg="#1E8449", fg="white", width=20).pack(side=LEFT, padx=5)
        self.scan_btn = Button(root, text="Scan and Extract",
                               font=("Arial", 15, "bold"), bg="#154360", fg="white", width=25,
                               command=self.scan_image)
        self.scan_btn.pack(pady=15)
        self.scan_btn.config(state=DISABLED)

        # Image preview
        self.img_preview = Label(root)
        self.img_preview.pack()

        # Treeview table: Fields & Values
        columns = ('Field', 'Value')
        self.tree = ttk.Treeview(root, columns=columns, show='headings', height=13)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"), foreground='#154360')
        style.configure("Treeview", font=("Arial", 12))
        self.tree.heading('Field', text='Field')
        self.tree.heading('Value', text='Value')
        self.tree.column('Field', width=190, anchor=W)
        self.tree.column('Value', width=660, anchor=W)
        self.tree.pack(padx=12, pady=13, fill=BOTH, expand=True)

    def upload_file(self):
        self.filename = filedialog.askopenfilename(
            initialdir=os.path.expanduser("~"),
            title="Select Business Card Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if not self.filename:
            self.status_var.set("No image selected.")
            self.scan_btn.config(state=DISABLED)
            self.img_preview.config(image='')
            return
        self.status_var.set(f"Selected: {os.path.basename(self.filename)}")
        self.scan_btn.config(state=NORMAL)
        img = Image.open(self.filename)
        img.thumbnail((340, 180))
        img_disp = ImageTk.PhotoImage(img)
        self.img_preview.config(image=img_disp)
        self.img_preview.photo_ref = img_disp

    def scan_image(self):
        if not self.filename:
            messagebox.showerror("No Image", "Please upload a business card image first")
            return
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Set as needed
            text = pytesseract.image_to_string(self.filename)
            self.status_var.set("Scan completed. Results below.")
            for i in self.tree.get_children():
                self.tree.delete(i)
            fields = self.extract_fields(text)
            for field, value in fields.items():
                self.tree.insert("", END, values=(field, value))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {e}")

    def extract_fields(self, text):
        results = {}
        # Name
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        name = ""
        for line in lines:
            if not re.search(r'(@|www|http|phone|mob|fax|address|[0-9])', line, re.I) and re.match(r'^[A-Za-z\s.]{4,}$', line) and len(line.split()) >= 2:
                name = line
                break
        if name:
            results["Name"] = name
        # Phone(s)
        phones = re.findall(r"(\+?\d[\d\s().-]{7,}\d)", text)
        if phones:
            results["Phone Numbers"] = ", ".join(phones)
        # Email(s)
        emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        if emails:
            results["Email"] = ", ".join(emails)
        # Website(s)
        urls = re.findall(r"(https?://[^\s]+|www\.[^\s]+)", text)
        if urls:
            results["Website"] = ", ".join(urls)
        # Address
        addr_keywords = ['street', 'st.', 'road', 'rd.', 'ave', 'blvd', 'suite', 'po box', 'postal', 'pincode', 'city', 'state', 'zip', 'district', 'lane', 'apartment']
        address_lines = [line for line in lines if any(kw in line.lower() for kw in addr_keywords)]
        if address_lines:
            results["Address"] = ', '.join(address_lines)
        return results

if __name__ == '__main__':
    root = Tk()
    app = BusinessCardScanner(root)
    root.mainloop()

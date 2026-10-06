from flask import Flask, request, jsonify, url_for, abort, redirect

app = Flask(__name__)

STUDENTS = {
    "23t1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23t1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23t1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23t1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23t1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23t1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}}
}

# CÂU 1: Trang chủ
@app.route("/")
def home():
    total_students = len(STUDENTS)
    classes = set(student["lop"] for student in STUDENTS.values())
    total_classes = len(classes)

    student_url = url_for("student_list")
    api_url = url_for("api_students")

    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Trang chủ</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #198754; }}
            a {{ text-decoration: none; color: blue; }}
        </style>
    </head>
    <body>
        <h1>Hệ thống quản lý sinh viên</h1>
        <p>Tổng số sinh viên: <strong>{total_students}</strong></p>
        <p>Số lớp: <strong>{total_classes}</strong></p>
        <p><a href="{student_url}">Danh sách sinh viên</a></p>
        <p><a href="{api_url}">API sinh viên</a></p>
    </body>
    </html>
    """


# CÂU 2: Danh sách sinh viên & Lọc theo lớp
@app.route("/students")
def student_list():
    lop = request.args.get("lop", "").strip()

    if lop:
        students = {mssv: sv for mssv, sv in STUDENTS.items() if sv["lop"].lower() == lop.lower()}
    else:
        students = STUDENTS

    classes = sorted(set(student["lop"] for student in STUDENTS.values()))

    options = '<option value="">Tất cả</option>'
    for class_name in classes:
        selected = "selected" if lop.lower() == class_name.lower() else ""
        options += f'<option value="{class_name}" {selected}>{class_name}</option>'

    rows = ""
    for mssv, student in students.items():
        scores = student["scores"]
        if scores:
            diem_tb = sum(scores.values()) / len(scores)
            if diem_tb >= 8:
                xep_loai = "Giỏi"
            elif diem_tb >= 6.5:
                xep_loai = "Khá"
            elif diem_tb >= 5:
                xep_loai = "Trung bình"
            else:
                xep_loai = "Yếu"
            diem_hien_thi = f"{diem_tb:.2f}"
        else:
            diem_hien_thi = "–"
            xep_loai = "-"

        detail_url = url_for("student_detail", mssv=mssv)
        rows += f"""
        <tr>
            <td><a href="{detail_url}">{mssv}</a></td>
            <td>{student["name"]}</td>
            <td>{student["lop"]}</td>
            <td>{diem_hien_thi}</td>
            <td>{xep_loai}</td>
        </tr>
        """

    if not students:
        rows = '<tr><td colspan="5">Không có sinh viên phù hợp.</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Danh sách sinh viên</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #198754; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid black; padding: 10px; text-align: center; }}
            th {{ background: #198754; color: white; }}
            select {{ padding: 7px; }}
            button {{ padding: 7px 15px; }}
            a {{ color: blue; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h1>Danh sách sinh viên</h1>
        <form method="get" action="{url_for('student_list')}">
            <label>Lọc theo lớp:</label>
            <select name="lop">
                {options}
            </select>
            <button type="submit">Lọc</button>
        </form>
        <table>
            <tr>
                <th>MSSV</th>
                <th>Họ tên</th>
                <th>Lớp</th>
                <th>Điểm TB</th>
                <th>Xếp loại</th>
            </tr>
            {rows}
        </table>
        <br>
        <a href="{url_for('home')}">← Về trang chủ</a>
    </body>
    </html>
    """


# CÂU 3: Chi tiết sinh viên
@app.route("/students/<mssv>")
def student_detail(mssv):
    student = None
    student_mssv = None

    for ma, sv in STUDENTS.items():
        if ma.lower() == mssv.lower():
            student = sv
            student_mssv = ma
            break

    if student is None:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    scores = student["scores"]
    if scores:
        diem_tb = sum(scores.values()) / len(scores)
        if diem_tb >= 8:
            xep_loai = "Giỏi"
        elif diem_tb >= 6.5:
            xep_loai = "Khá"
        elif diem_tb >= 5:
            xep_loai = "Trung bình"
        else:
            xep_loai = "Yếu"
        diem_hien_thi = f"{diem_tb:.2f}"
    else:
        diem_hien_thi = "–"
        xep_loai = "-"

    lop_url = url_for("student_list", lop=student["lop"])

    rows = ""
    for hoc_phan, diem in scores.items():
        rows += f"""
        <tr>
            <td>{hoc_phan}</td>
            <td>{diem}</td>
        </tr>
        """

    if not scores:
        rows = '<tr><td colspan="2">Chưa có điểm học phần</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Chi tiết sinh viên</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #198754; }}
            table {{ border-collapse: collapse; width: 500px; margin-top: 20px; }}
            th, td {{ border: 1px solid black; padding: 10px; text-align: center; }}
            th {{ background: #198754; color: white; }}
            a {{ color: blue; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h1>Thông tin sinh viên</h1>
        <p><strong>Họ tên:</strong> {student["name"]}</p>
        <p><strong>MSSV:</strong> {student_mssv}</p>
        <p><strong>Lớp:</strong> <a href="{lop_url}">{student["lop"]}</a></p>
        <p><strong>Điểm TB:</strong> {diem_hien_thi}</p>
        <p><strong>Xếp loại:</strong> {xep_loai}</p>

        <h2>Bảng điểm từng học phần</h2>
        <table>
            <tr>
                <th>Học phần</th>
                <th>Điểm</th>
            </tr>
            {rows}
        </table>
        <br>
        <a href="{url_for('student_list')}">← Danh sách sinh viên</a>
    </body>
    </html>
    """


# CÂU 4: Điều hướng từ đường dẫn cũ
@app.route("/sv/<mssv>")
def old_student_detail(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)


# API sinh viên
@app.route("/api/students")
def api_students():
    return jsonify(STUDENTS)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
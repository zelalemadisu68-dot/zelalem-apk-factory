import datetime
import os
import sqlite3
import flet as ft

# ==========================================
# 1. ቋሚ የSQLite ዳታቤዝ ሞተር (Offline Database)
# ==========================================
DB_PATH = os.path.join(os.path.expanduser("~"), "zelalem_school_pro.db")


def init_db():
  conn = sqlite3.connect(DB_PATH, check_same_thread=False)
  c = conn.cursor()
  c.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_code TEXT UNIQUE,
        full_name TEXT,
        grade TEXT,
        gender TEXT,
        phone TEXT
    )""")
  c.execute("""CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_code TEXT,
        subject TEXT,
        score REAL,
        UNIQUE(student_code, subject)
    )""")
  c.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_code TEXT,
        date_str TEXT,
        status TEXT,
        UNIQUE(student_code, date_str)
    )""")
  c.execute("""CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_code TEXT,
        amount REAL,
        month_name TEXT,
        date_str TEXT
    )""")

  # ለሙከራ የሚሆኑ የመጀመሪያ ተማሪዎች (ዳታቤዙ ባዶ ከሆነ ብቻ ይገባሉ)
  c.execute("SELECT COUNT(*) FROM students")
  if c.fetchone()[0] == 0:
    sample_students = [
        ("STU-101", "Zelalem Adisu", "Grade 12", "Male", "0911000001"),
        ("STU-102", "Adise Alemayehu", "Grade 12", "Female", "0911000002"),
        ("STU-103", "Dawit Kebede", "Grade 11", "Male", "0911000003"),
    ]
    c.executemany(
        "INSERT INTO students (student_code, full_name, grade, gender, phone)"
        " VALUES (?,?,?,?,?)",
        sample_students,
    )
    conn.commit()
  conn.close()


# ==========================================
# 2. ዋናው የFlet Mobile UI እና ሲስተም
# ==========================================
def main(page: ft.Page):
  init_db()
  page.title = "Birana School Pro"
  page.theme_mode = ft.ThemeMode.DARK
  page.bgcolor = "#0B0F19"
  page.padding = 0

  def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

  def notify(msg, color="#00E676"):
    page.snack_bar = ft.SnackBar(
        ft.Text(msg, color="black", weight="bold"), bgcolor=color
    )
    page.snack_bar.open = True
    page.update()

  # ------------------------------------------
  # ገጽ 1፡ DASHBOARD (አጠቃላይ እይታ)
  # ------------------------------------------
  def build_dashboard():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students")
    total_stu = c.fetchone()[0]

    today = datetime.date.today().isoformat()
    c.execute(
        "SELECT COUNT(*) FROM attendance WHERE date_str=? AND status='Present'",
        (today,),
    )
    present_today = c.fetchone()[0]

    c.execute("SELECT IFNULL(SUM(amount), 0) FROM fees")
    total_fees = c.fetchone()[0]
    conn.close()

    def stat_card(title, value, icon_name, bg_color):
      return ft.Container(
          content=ft.Row(
              [
                  ft.Container(
                      content=ft.Icon(icon_name, color="white", size=30),
                      bgcolor=bg_color,
                      padding=12,
                      border_radius=12,
                  ),
                  ft.Column(
                      [
                          ft.Text(title, size=12, color="#94A3B8"),
                          ft.Text(
                              str(value), size=20, weight="bold", color="white"
                          ),
                      ],
                      spacing=2,
                  ),
              ],
              alignment=ft.MainAxisAlignment.START,
          ),
          bgcolor="#1E293B",
          padding=15,
          border_radius=15,
          margin=ft.margin.only(bottom=10),
      )

    return ft.Container(
        padding=15,
        content=ft.Column(
            [
                ft.Container(
                    gradient=ft.LinearGradient(
                        colors=["#0284C7", "#1E3A8A"],
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                    ),
                    padding=20,
                    border_radius=18,
                    content=ft.Column([
                        ft.Text(
                            "🏫 BIRANA SCHOOL PRO",
                            size=20,
                            weight="bold",
                            color="white",
                        ),
                        ft.Text(
                            "ዘመናዊ የትምህርት ቤት አስተዳደር ሲስተም",
                            size=13,
                            color="#E0F2FE",
                        ),
                        ft.Divider(color="white24"),
                        ft.Text(f"📅 ቀን: {today}  |  Manager: Zelalem", size=12, color="#BAE6FD"),
                    ]),
                ),
                ft.Text(
                    "📊 የዛሬ አጠቃላይ ሪፖርት", size=16, weight="bold", color="#38BDF8"
                ),
                stat_card("ጠቅላላ ተማሪዎች (Total Students)", total_stu, "people", "#2563EB"),
                stat_card(
                    "ዛሬ የተገኙ (Present Today)",
                    f"{present_today} / {total_stu}",
                    "check_circle",
                    "#10B981",
                ),
                stat_card(
                    "ጠቅላላ የተሰበሰበ ክፍያ (ETB)",
                    f"{total_fees:,.2f} ብር",
                    "account_balance_wallet",
                    "#F59E0B",
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )

  # ------------------------------------------
  # ገጽ 2፡ STUDENTS (የተማሪዎች ምዝገባና ዝርዝር)
  # ------------------------------------------
  def build_students():
    name_in = ft.TextField(
        label="ሙሉ ስም (Full Name)", bgcolor="#1E293B", border_radius=10
    )
    grade_in = ft.Dropdown(
        label="ክፍል (Grade)",
        bgcolor="#1E293B",
        border_radius=10,
        options=[
            ft.dropdown.Option("Grade 9"),
            ft.dropdown.Option("Grade 10"),
            ft.dropdown.Option("Grade 11"),
            ft.dropdown.Option("Grade 12"),
        ],
        value="Grade 12",
    )
    gender_in = ft.Dropdown(
        label="ፆታ",
        bgcolor="#1E293B",
        border_radius=10,
        width=120,
        options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female")],
        value="Male",
    )
    phone_in = ft.TextField(
        label="ስልክ ቁጥር", bgcolor="#1E293B", border_radius=10, expand=True
    )
    search_in = ft.TextField(
        label="🔍 ተማሪ ፈልግ (በስም ወይም በID)...",
        bgcolor="#1E293B",
        border_radius=10,
        on_change=lambda e: refresh_list(),
    )
    list_col = ft.Column(spacing=8)

    def refresh_list():
      list_col.controls.clear()
      q = search_in.value.strip() if search_in.value else ""
      conn = get_conn()
      c = conn.cursor()
      if q:
        c.execute(
            "SELECT student_code, full_name, grade, gender, phone FROM students"
            " WHERE full_name LIKE ? OR student_code LIKE ? ORDER BY id DESC",
            (f"%{q}%", f"%{q}%"),
        )
      else:
        c.execute(
            "SELECT student_code, full_name, grade, gender, phone FROM students"
            " ORDER BY id DESC"
        )
      rows = c.fetchall()
      conn.close()

      for code, name, grd, gen, ph in rows:
        list_col.controls.append(
            ft.Container(
                bgcolor="#1E293B",
                padding=12,
                border_radius=12,
                content=ft.Row(
                    [
                        ft.CircleAvatar(
                            content=ft.Text(name[:1].upper(), weight="bold"),
                            bgcolor="#0284C7",
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    f"{name} ({code})",
                                    weight="bold",
                                    size=15,
                                    color="white",
                                ),
                                ft.Text(
                                    f"{grd} • {gen} • 📞 {ph}",
                                    size=12,
                                    color="#94A3B8",
                                ),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                        ft.IconButton(
                            icon="delete",
                            icon_color="#EF4444",
                            on_click=lambda e, sc=code: delete_stu(sc),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )
        )
      page.update()

    def add_stu(e):
      if not name_in.value:
        notify("እባክህ የተማሪውን ስም አስገባ!", "#EF4444")
        return
      conn = get_conn()
      c = conn.cursor()
      c.execute("SELECT COUNT(*) FROM students")
      next_num = 101 + c.fetchone()[0]
      code = f"STU-{next_num}"
      while True:
        c.execute("SELECT 1 FROM students WHERE student_code=?", (code,))
        if not c.fetchone():
          break
        next_num += 1
        code = f"STU-{next_num}"

      c.execute(
          "INSERT INTO students (student_code, full_name, grade, gender, phone)"
          " VALUES (?,?,?,?,?)",
          (
              code,
              name_in.value.strip(),
              grade_in.value,
              gender_in.value,
              phone_in.value or "N/A",
          ),
      )
      conn.commit()
      conn.close()
      name_in.value = ""
      phone_in.value = ""
      notify(f"ተማሪው በመለያ ቁጥር {code} ተመዝግቧል!")
      refresh_list()

    def delete_stu(code):
      conn = get_conn()
      c = conn.cursor()
      c.execute("DELETE FROM students WHERE student_code=?", (code,))
      conn.commit()
      conn.close()
      notify(f"{code} ተሰርዟል", "#F59E0B")
      refresh_list()

    refresh_list()
    return ft.Container(
        padding=15,
        content=ft.Column(
            [
                ft.Text(
                    "👨‍🎓 አዲስ ተማሪ መመዝገቢያ", size=17, weight="bold", color="#38BDF8"
                ),
                name_in,
                ft.Row([grade_in]),
                ft.Row([gender_in, phone_in]),
                ft.ElevatedButton(
                    "➕ ተማሪ መዝግብ (Save Student)",
                    bgcolor="#00C853",
                    color="white",
                    height=45,
                    on_click=add_stu,
                ),
                ft.Divider(color="white24"),
                search_in,
                list_col,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )

  # ------------------------------------------
  # ገጽ 3፡ GRADES (የውጤት መሙያና አቬሬጅ ማስሊያ)
  # ------------------------------------------
  def build_grades():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT student_code, full_name FROM students ORDER BY full_name")
    stu_list = c.fetchall()
    conn.close()

    stu_dd = ft.Dropdown(
        label="ተማሪ ምረጥ",
        bgcolor="#1E293B",
        border_radius=10,
        options=[
            ft.dropdown.Option(key=code, text=f"{name} ({code})")
            for code, name in stu_list
        ],
        value=stu_list[0][0] if stu_list else None,
    )
    sub_dd = ft.Dropdown(
        label="የትምህርት አይነት (Subject)",
        bgcolor="#1E293B",
        border_radius=10,
        options=[
            ft.dropdown.Option("Physics"),
            ft.dropdown.Option("Chemistry"),
            ft.dropdown.Option("Biology"),
            ft.dropdown.Option("Mathematics"),
            ft.dropdown.Option("English"),
        ],
        value="Physics",
    )
    score_in = ft.TextField(
        label="ውጤት (ከ 100%)",
        bgcolor="#1E293B",
        border_radius=10,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    report_col = ft.Column(spacing=8)

    def load_report(e=None):
      report_col.controls.clear()
      if not stu_dd.value:
        return
      conn = get_conn()
      c = conn.cursor()
      c.execute(
          "SELECT subject, score FROM scores WHERE student_code=?",
          (stu_dd.value,),
      )
      rows = c.fetchall()
      conn.close()

      if not rows:
        report_col.controls.append(
            ft.Text("ለዚህ ተማሪ የተሞላ ውጤት የለም።", color="#94A3B8")
        )
      else:
        total = sum(r[1] for r in rows)
        avg = total / len(rows)
        status_txt = "PROMOTED ✅" if avg >= 50 else "FAILED ❌"
        report_col.controls.append(
            ft.Container(
                bgcolor="#0284C7",
                padding=15,
                border_radius=12,
                content=ft.Row(
                    [
                        ft.Text(
                            f"Total: {total:.1f}", weight="bold", color="white"
                        ),
                        ft.Text(
                            f"Average: {avg:.1f}%", weight="bold", color="white"
                        ),
                        ft.Text(status_txt, weight="bold", color="#FEF08A"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )
        )
        for sub, sc in rows:
          report_col.controls.append(
              ft.Container(
                  bgcolor="#1E293B",
                  padding=12,
                  border_radius=10,
                  content=ft.Row(
                      [
                          ft.Text(sub, weight="bold", color="white"),
                          ft.Text(
                              f"{sc} / 100", color="#00E676", weight="bold"
                          ),
                      ],
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  ),
              )
          )
      page.update()

    stu_dd.on_change = load_report

    def save_score(e):
      if not stu_dd.value or not score_in.value:
        notify("ተማሪ እና ውጤት በትክክል አስገባ!", "#EF4444")
        return
      try:
        val = float(score_in.value)
        if val < 0 or val > 100:
          raise ValueError()
      except ValueError:
        notify("ውጤት ከ 0 እስከ 100 መሆን አለበት!", "#EF4444")
        return

      conn = get_conn()
      c = conn.cursor()
      c.execute(
          "INSERT OR REPLACE INTO scores (student_code, subject, score) VALUES"
          " (?,?,?)",
          (stu_dd.value, sub_dd.value, val),
      )
      conn.commit()
      conn.close()
      score_in.value = ""
      notify(f"የ {sub_dd.value} ውጤት ተመዝግቧል!")
      load_report()

    load_report()
    return ft.Container(
        padding=15,
        content=ft.Column(
            [
                ft.Text(
                    "📝 የውጤት መሙያና ሪፖርት ካርድ",
                    size=17,
                    weight="bold",
                    color="#38BDF8",
                ),
                stu_dd,
                sub_dd,
                score_in,
                ft.ElevatedButton(
                    "💾 ውጤት መዝግብ (Save Grade)",
                    bgcolor="#2563EB",
                    color="white",
                    height=45,
                    on_click=save_score,
                ),
                ft.Divider(color="white24"),
                ft.Text("የተማሪው ውጤት ዝርዝር:", weight="bold", color="#94A3B8"),
                report_col,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )

  # ------------------------------------------
  # ገጽ 4፡ ATTENDANCE & FEES (ክትትል እና ክፍያ)
  # ------------------------------------------
  def build_attendance_and_fees():
    today = datetime.date.today().isoformat()
    att_col = ft.Column(spacing=8)

    def refresh_att():
      att_col.controls.clear()
      conn = get_conn()
      c = conn.cursor()
      c.execute(
          "SELECT student_code, full_name, grade FROM students ORDER BY"
          " full_name"
      )
      students = c.fetchall()
      for code, name, grd in students:
        c.execute(
            "SELECT status FROM attendance WHERE student_code=? AND"
            " date_str=?",
            (code, today),
        )
        r = c.fetchone()
        st = r[0] if r else "Unmarked"
        badge_color = (
            "#10B981"
            if st == "Present"
            else ("#EF4444" if st == "Absent" else "#64748B")
        )

        att_col.controls.append(
            ft.Container(
                bgcolor="#1E293B",
                padding=10,
                border_radius=12,
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(name, weight="bold", color="white"),
                                ft.Text(
                                    f"{code} • Status: {st}",
                                    size=12,
                                    color=badge_color,
                                ),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                        ft.ElevatedButton(
                            "P",
                            bgcolor="#10B981",
                            color="white",
                            width=45,
                            on_click=lambda e, sc=code: mark_att(sc, "Present"),
                        ),
                        ft.ElevatedButton(
                            "A",
                            bgcolor="#EF4444",
                            color="white",
                            width=45,
                            on_click=lambda e, sc=code: mark_att(sc, "Absent"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )
        )
      conn.close()
      page.update()

    def mark_att(code, status):
      conn = get_conn()
      c = conn.cursor()
      c.execute(
          "INSERT OR REPLACE INTO attendance (student_code, date_str, status)"
          " VALUES (?,?,?)",
          (code, today, status),
      )
      conn.commit()
      conn.close()
      refresh_att()

    # የክፍያ መመዝገቢያ
    fee_code_in = ft.TextField(
        label="የተማሪ ID (ምሳሌ STU-101)",
        bgcolor="#1E293B",
        border_radius=10,
        expand=True,
    )
    fee_amt_in = ft.TextField(
        label="ብር (ETB)",
        bgcolor="#1E293B",
        border_radius=10,
        width=130,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    def pay_fee(e):
      if not fee_code_in.value or not fee_amt_in.value:
        notify("የተማሪ ID እና የብር መጠን አስገባ!", "#EF4444")
        return
      try:
        amt = float(fee_amt_in.value)
      except ValueError:
        notify("ትክክለኛ ቁጥር አስገባ!", "#EF4444")
        return
      conn = get_conn()
      c = conn.cursor()
      c.execute(
          "INSERT INTO fees (student_code, amount, month_name, date_str) VALUES"
          " (?,?,?,?)",
          (fee_code_in.value.strip().upper(), amt, "Monthly", today),
      )
      conn.commit()
      conn.close()
      fee_amt_in.value = ""
      notify(f"{amt} ብር ክፍያ ተመዝግቧል!")

    refresh_att()
    return ft.Container(
        padding=15,
        content=ft.Column(
            [
                ft.Text(
                    "💳 ወርሃዊ ክፍያ መቀበያ (Fee Collection)",
                    size=16,
                    weight="bold",
                    color="#F59E0B",
                ),
                ft.Row([fee_code_in, fee_amt_in]),
                ft.ElevatedButton(
                    "✅ ክፍያ መዝግብ (Record Payment)",
                    bgcolor="#F59E0B",
                    color="black",
                    on_click=pay_fee,
                ),
                ft.Divider(color="white24"),
                ft.Text(
                    f"📅 የዛሬ ክትትል (Attendance - {today})",
                    size=16,
                    weight="bold",
                    color="#38BDF8",
                ),
                att_col,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )

  # ------------------------------------------
  # ዋናው የNavigation ሲስተም እና Login
  # ------------------------------------------
  body_container = ft.Container(expand=True)

  def switch_tab(e):
    idx = e.control.selected_index
    if idx == 0:
      body_container.content = build_dashboard()
    elif idx == 1:
      body_container.content = build_students()
    elif idx == 2:
      body_container.content = build_grades()
    elif idx == 3:
      body_container.content = build_attendance_and_fees()
    page.update()

  nav_bar = ft.NavigationBar(
      bgcolor="#1E293B",
      selected_index=0,
      on_change=switch_tab,
      destinations=[
          ft.NavigationDestination(icon="dashboard", label="ዳሽቦርድ"),
          ft.NavigationDestination(icon="people", label="ተማሪዎች"),
          ft.NavigationDestination(icon="grading", label="ውጤት"),
          ft.NavigationDestination(icon="fact_check", label="ክትትል/ክፍያ"),
      ],
  )

  # የመግቢያ (Login) ገጽ
  user_in = ft.TextField(
      label="Username", value="admin", bgcolor="#1E293B", border_radius=12
  )
  pass_in = ft.TextField(
      label="Password",
      value="1234",
      password=True,
      can_reveal_password=True,
      bgcolor="#1E293B",
      border_radius=12,
  )

  def do_login(e):
    if user_in.value.strip() == "admin" and pass_in.value.strip() == "1234":
      page.clean()
      body_container.content = build_dashboard()
      page.add(body_container, nav_bar)
    else:
      notify("የተሳሳተ Username ወይም Password!", "#EF4444")

  login_view = ft.Container(
      expand=True,
      padding=25,
      alignment=ft.alignment.center,
      content=ft.Column(
          [
              ft.Icon("school", size=70, color="#38BDF8"),
              ft.Text(
                  "BIRANA SCHOOL PRO", size=24, weight="bold", color="white"
              ),
              ft.Text(
                  "Admin Portal Login", size=14, color="#94A3B8"
              ),
              ft.Container(height=15),
              user_in,
              pass_in,
              ft.Container(height=10),
              ft.ElevatedButton(
                  "🔐 ወደ ሲስተሙ ግባ (LOGIN)",
                  bgcolor="#00C853",
                  color="white",
                  width=300,
                  height=48,
                  on_click=do_login,
              ),
          ],
          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
          alignment=ft.MainAxisAlignment.CENTER,
      ),
  )

  page.add(login_view)


ft.app(target=main)

# Build timestamp: 1794648499
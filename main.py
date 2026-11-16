import datetime
import hashlib
import math
import os
import random
import sqlite3
import string
import tempfile
import threading
import time
import flet as ft

# ANDROID 13 SAFE OFFLINE SQLITE PATH
DB_PATH = os.path.join(tempfile.gettempdir(), "zelalem_omni56_vault.db")


def init_db():
  try:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, body TEXT, ts TEXT
        )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_str TEXT, label TEXT, active INTEGER
        )""")
    conn.commit()
    conn.close()
  except Exception:
    pass


# ==========================================
# THE 56 BUILT-IN OFFLINE TOOLS ENGINE
# ==========================================
TOOLS_CATALOG = [
    ("01. Quadratic Solver (ax²+bx+c)", "Math", "a,b,c (e.g. 1,-5,6)"),
    ("02. Prime Number Checker", "Math", "Enter integer (e.g. 97)"),
    ("03. GCD & LCM Calculator", "Math", "a,b (e.g. 24,36)"),
    ("04. Factorial (n!)", "Math", "Enter n (e.g. 10)"),
    ("05. Fibonacci Generator", "Math", "Count N (e.g. 12)"),
    ("06. Ohm's Law (V = I × R)", "Physics", "Current(I), Resistance(R)"),
    ("07. Kinetic Energy (½mv²)", "Physics", "Mass(kg), Velocity(m/s)"),
    ("08. Projectile Range (v², angle)", "Physics", "Velocity(m/s), Angle(deg)"),
    ("09. Pendulum Period (T)", "Physics", "Length in meters (e.g. 1.5)"),
    ("10. Electrical Power (P = V×I)", "Physics", "Voltage(V), Current(A)"),
    ("11. Gravitational Force", "Physics", "m1(kg), m2(kg), dist(m)"),
    ("12. Lens Focal Length (1/f)", "Physics", "u(cm), v(cm)"),
    ("13. pH from [H+] Concentration", "Chem", "H+ molarity (e.g. 0.001)"),
    ("14. Ideal Gas Pressure (PV=nRT)", "Chem", "n(mol), T(K), V(L)"),
    ("15. Celsius ➔ Fahrenheit & Kelvin", "Convert", "Temp in °C (e.g. 25)"),
    ("16. Fahrenheit ➔ Celsius", "Convert", "Temp in °F (e.g. 98.6)"),
    ("17. Kilometers ➔ Miles & Meters", "Convert", "Kilometers (e.g. 10)"),
    ("18. Kilograms ➔ Pounds (lbs)", "Convert", "Kilograms (e.g. 70)"),
    ("19. Pounds ➔ Kilograms", "Convert", "Pounds (e.g. 154)"),
    ("20. Meters ➔ Feet & Inches", "Convert", "Meters (e.g. 1.78)"),
    ("21. Liters ➔ Gallons", "Convert", "Liters (e.g. 20)"),
    ("22. Speed: km/h ➔ m/s & mph", "Convert", "Speed in km/h (e.g. 100)"),
    ("23. Area: Hectare ➔ Square Meters", "Convert", "Hectares (e.g. 2.5)"),
    ("24. Data: GB ➔ MB & KB", "Convert", "Gigabytes (e.g. 4)"),
    ("25. Pressure: Bar ➔ PSI & Pa", "Convert", "Bar (e.g. 2.2)"),
    ("26. Energy: Calories ➔ Joules", "Convert", "Calories (e.g. 500)"),
    ("27. Angle: Degrees ➔ Radians", "Convert", "Degrees (e.g. 180)"),
    ("28. Power: Horsepower ➔ Watts", "Convert", "HP (e.g. 150)"),
    ("29. Forex Risk & Lot Calculator", "Forex", "Balance,Risk%,StopLossPips"),
    ("30. Forex Risk:Reward (1:R)", "Forex", "StopLoss, TakeProfit"),
    ("31. Compound Interest Calculator", "Finance", "Principal,Rate%,Years"),
    ("32. Loan EMI Monthly Calculator", "Finance", "Loan,AnnualRate%,Months"),
    ("33. Profit Margin & Markup %", "Finance", "Cost, SellingPrice"),
    ("34. Discount Price Calculator", "Finance", "OriginalPrice, Discount%"),
    ("35. Ethiopian VAT (15%) Splitter", "Finance", "Amount in ETB (e.g. 5000)"),
    ("36. Savings Goal Planner", "Finance", "TargetETB, Months"),
    ("37. Hacker Password Generator", "Cyber", "Length (e.g. 16)"),
    ("38. SHA-256 Hash Encryptor", "Cyber", "Enter any text"),
    ("39. Base64 Encoder", "Cyber", "Enter text to encode"),
    ("40. Base64 Decoder", "Cyber", "Enter Base64 string"),
    ("41. Decimal ➔ Binary & Hex", "Cyber", "Enter integer (e.g. 255)"),
    ("42. Binary ➔ Decimal Converter", "Cyber", "Enter binary (e.g. 101101)"),
    ("43. Caesar Cipher Encryptor", "Cyber", "Text,Shift (e.g. ZELALEM,3)"),
    ("44. IP Subnet Host Counter", "Cyber", "CIDR prefix (e.g. 24)"),
    ("45. Satellite Dish Elevation Angle", "Sat", "Lat,Lon,SatLon (e.g. 7.5,35.4,57)"),
    ("46. LNB Skew Angle Calculator", "Sat", "Lat,Lon,SatLon (e.g. 7.5,35.4,7)"),
    ("47. BMI & Body Category", "Fitness", "Weight(kg), Height(cm)"),
    ("48. Daily Calorie (TDEE) Estimator", "Fitness", "Weight(kg),Height(cm),Age"),
    ("49. 1-Rep Max Strength (Calisthenics)", "Fitness", "Weight(kg), Reps"),
    ("50. Daily Water Intake Target", "Fitness", "Body weight in kg (e.g. 65)"),
    ("51. Target Heart Rate Zone", "Fitness", "Your Age (e.g. 19)"),
    ("52. Word, Char & Line Counter", "Utility", "Type or paste sentence"),
    ("53. Exact Age in Days & Hours", "Utility", "Birth Year (e.g. 2007)"),
    ("54. Exam Average & Grade Rank", "Utility", "Scores comma separated"),
    ("55. Random Lucky Picker", "Utility", "Items comma separated"),
    ("56. Roman Numeral Converter", "Utility", "Number 1-3999 (e.g. 2026)"),
]


def execute_tool(tool_name, raw_in):
  s = raw_in.strip()
  nums = []
  for part in s.split(","):
    try:
      nums.append(float(part.strip()))
    except Exception:
      pass

  try:
    idx = int(tool_name[:2])
    if idx == 1 and len(nums) >= 3:
      a, b, c = nums[0], nums[1], nums[2]
      d = b * b - 4 * a * c
      if d < 0:
        return f"Complex Roots (Discriminant = {d})"
      r1 = (-b + math.sqrt(d)) / (2 * a)
      r2 = (-b - math.sqrt(d)) / (2 * a)
      return f"x₁ = {r1:.3f}   |   x₂ = {r2:.3f}"
    elif idx == 2 and nums:
      n = int(nums[0])
      is_p = n > 1 and all(n % i != 0 for i in range(2, int(math.isqrt(n)) + 1))
      return f"{n} is {'PRIME ✅' if is_p else 'NOT PRIME ❌'}"
    elif idx == 3 and len(nums) >= 2:
      a, b = int(nums[0]), int(nums[1])
      g = math.gcd(a, b)
      return f"GCD = {g}   |   LCM = {abs(a*b)//g}"
    elif idx == 4 and nums:
      return f"{int(nums[0])}! = {math.factorial(min(100, int(nums[0])))}"
    elif idx == 5 and nums:
      n = min(40, max(1, int(nums[0])))
      fib = [0, 1]
      for _ in range(2, n):
        fib.append(fib[-1] + fib[-2])
      return ", ".join(map(str, fib[:n]))
    elif idx == 6 and len(nums) >= 2:
      return f"Voltage (V) = {nums[0]*nums[1]:.2f} Volts"
    elif idx == 7 and len(nums) >= 2:
      return f"Kinetic Energy = {0.5 * nums[0] * (nums[1]**2):.2f} Joules"
    elif idx == 8 and len(nums) >= 2:
      rng = (nums[0] ** 2) * math.sin(math.radians(2 * nums[1])) / 9.81
      return f"Horizontal Range = {rng:.2f} meters"
    elif idx == 9 and nums:
      return f"Period (T) = {2 * math.pi * math.sqrt(nums[0]/9.81):.3f} sec"
    elif idx == 10 and len(nums) >= 2:
      return f"Power (P) = {nums[0]*nums[1]:.2f} Watts"
    elif idx == 11 and len(nums) >= 3:
      f = 6.674e-11 * nums[0] * nums[1] / (nums[2] ** 2)
      return f"Force = {f:.4e} N"
    elif idx == 12 and len(nums) >= 2:
      f = 1.0 / ((1.0 / nums[0]) + (1.0 / nums[1]))
      return f"Focal Length (f) = {f:.2f} cm"
    elif idx == 13 and nums:
      return f"pH = {-math.log10(nums[0]):.2f}"
    elif idx == 14 and len(nums) >= 3:
      return f"Pressure = {(nums[0]*0.0821*nums[1])/nums[2]:.2f} atm"
    elif idx == 15 and nums:
      c = nums[0]
      return f"{c*9/5 + 32:.1f} °F   |   {c + 273.15:.1f} K"
    elif idx == 16 and nums:
      return f"{(nums[0]-32)*5/9:.2f} °C"
    elif idx == 17 and nums:
      return f"{nums[0]*0.621371:.2f} Miles  |  {nums[0]*1000:,.0f} m"
    elif idx == 18 and nums:
      return f"{nums[0]*2.20462:.2f} lbs (Pounds)"
    elif idx == 19 and nums:
      return f"{nums[0]/2.20462:.2f} kg"
    elif idx == 20 and nums:
      return f"{nums[0]*3.28084:.2f} ft  ({nums[0]*39.37:.1f} inches)"
    elif idx == 21 and nums:
      return f"{nums[0]*0.264172:.2f} US Gallons"
    elif idx == 22 and nums:
      return f"{nums[0]/3.6:.2f} m/s   |   {nums[0]*0.62137:.2f} mph"
    elif idx == 23 and nums:
      return f"{nums[0]*10000:,.0f} m²"
    elif idx == 24 and nums:
      return f"{nums[0]*1024:,.0f} MB   |   {nums[0]*1048576:,.0f} KB"
    elif idx == 25 and nums:
      return f"{nums[0]*14.5038:.2f} PSI   |   {nums[0]*100000:,.0f} Pa"
    elif idx == 26 and nums:
      return f"{nums[0]*4.184:.1f} Joules"
    elif idx == 27 and nums:
      return f"{math.radians(nums[0]):.4f} Radians"
    elif idx == 28 and nums:
      return f"{nums[0]*745.7:.1f} Watts"
    elif idx == 29 and len(nums) >= 3:
      risk_usd = nums[0] * (nums[1] / 100.0)
      lot = risk_usd / (nums[2] * 10.0)
      return f"Risk: ${risk_usd:.2f}  |  Recommended Lot: { max(0.01, lot):.2f}"
    elif idx == 30 and len(nums) >= 2:
      return f"Risk-to-Reward Ratio = 1 : {nums[1]/nums[0]:.2f}"
    elif idx == 31 and len(nums) >= 3:
      amt = nums[0] * ((1 + (nums[1] / 100.0)) ** nums[2])
      return f"Total = {amt:,.2f}  (Profit: {amt-nums[0]:,.2f})"
    elif idx == 32 and len(nums) >= 3:
      p, r, m = nums[0], (nums[1] / 100.0) / 12.0, nums[2]
      emi = (p * r * ((1 + r) ** m)) / (((1 + r) ** m) - 1)
      return f"Monthly Payment = {emi:,.2f} ETB"
    elif idx == 33 and len(nums) >= 2:
      prof = nums[1] - nums[0]
      return f"Profit: {prof:.2f}  |  Margin: {(prof/nums[1])*100:.1f}%"
    elif idx == 34 and len(nums) >= 2:
      saved = nums[0] * (nums[1] / 100.0)
      return f"Pay Only: {nums[0]-saved:,.2f}  (Saved: {saved:,.2f})"
    elif idx == 35 and nums:
      vat = nums[0] * 0.15
      return f"VAT (15%): {vat:,.2f} ETB  |  Total: {nums[0]+vat:,.2f} ETB"
    elif idx == 36 and len(nums) >= 2:
      return f"Save {nums[0]/nums[1]:,.2f} ETB per month"
    elif idx == 37:
      ln = int(nums[0]) if nums else 16
      chars = string.ascii_letters + string.digits + "!@#$%^&*"
      return "".join(random.choice(chars) for _ in range(min(64, max(6, ln))))
    elif idx == 38:
      return hashlib.sha256(s.encode("utf-8")).hexdigest()[:36] + "..."
    elif idx == 39:
      return base64.b64encode(s.encode("utf-8")).decode("utf-8")
    elif idx == 40:
      return base64.b64decode(s.encode("utf-8")).decode("utf-8", errors="ignore")
    elif idx == 41 and nums:
      n = int(nums[0])
      return f"BIN: {bin(n)[2:]}   |   HEX: {hex(n)[2:].upper()}"
    elif idx == 42:
      return f"Decimal = {int(s, 2)}"
    elif idx == 43:
      parts = s.split(",")
      txt, sh = parts[0], (int(parts[1]) if len(parts) > 1 else 3)
      out = "".join(
          chr((ord(c) - 65 + sh) % 26 + 65) if c.isupper() else c for c in txt.upper()
      )
      return f"Cipher: {out}"
    elif idx == 44 and nums:
      hosts = (2 ** (32 - int(nums[0]))) - 2
      return f"Usable Hosts = {max(0, hosts):,}"
    elif idx == 45 and len(nums) >= 3:
      lat, lon, sat = map(math.radians, nums[:3])
      dlon = sat - lon
      el = math.degrees(
          math.atan(
              (math.cos(lat) * math.cos(dlon) - 0.1512)
              / math.sqrt(1 - (math.cos(lat) * math.cos(dlon)) ** 2)
          )
      )
      return f"Dish Elevation Angle ≈ {el:.1f}°"
    elif idx == 46 and len(nums) >= 3:
      lat, lon, sat = map(math.radians, nums[:3])
      skew = math.degrees(math.atan(math.sin(lon - sat) / math.tan(lat)))
      return f"LNB Skew Angle ≈ {skew:.1f}°"
    elif idx == 47 and len(nums) >= 2:
      bmi = nums[0] / ((nums[1] / 100.0) ** 2)
      cat = "Normal ✅" if 18.5 <= bmi <= 24.9 else ("Overweight" if bmi > 24.9 else "Underweight")
      return f"BMI = {bmi:.1f} ({cat})"
    elif idx == 48 and len(nums) >= 3:
      bmr = 10 * nums[0] + 6.25 * nums[1] - 5 * nums[2] + 5
      return f"BMR: {bmr:.0f} kcal  |  Active TDEE: {bmr*1.55:.0f} kcal/day"
    elif idx == 49 and len(nums) >= 2:
      return f"Estimated 1-Rep Max = {nums[0] * (1 + nums[1]/30.0):.1f} kg"
    elif idx == 50 and nums:
      return f"Recommended Water = {nums[0]*0.035:.2f} Liters / day"
    elif idx == 51 and nums:
      mhr = 220 - nums[0]
      return f"Max HR: {mhr:.0f} bpm  |  Fat-Burn Zone: {mhr*0.65:.0f}-{mhr*0.85:.0f} bpm"
    elif idx == 52:
      return f"Words: {len(s.split())}   |   Chars: {len(s)}"
    elif idx == 53 and nums:
      yrs = 2026 - int(nums[0])
      return f"{yrs} Years  ≈  {yrs*365:,} Days  ≈  {yrs*8760:,} Hours"
    elif idx == 54 and nums:
      avg = sum(nums) / len(nums)
      return f"Count: {len(nums)}  |  Total: {sum(nums):.1f}  |  Average: {avg:.2f}%"
    elif idx == 55:
      items = [x.strip() for x in s.split(",") if x.strip()]
      return f"Winner 🎯: {random.choice(items)}" if items else "Enter items!"
    elif idx == 56 and nums:
      n = int(nums[0])
      val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
      syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
      rom = ""
      for i in range(len(val)):
        while n >= val[i]:
          rom += syb[i]
          n -= val[i]
      return f"Roman Numeral = {rom}"
    return "Enter valid input format."
  except Exception as e:
    return f"Error: {e}"


def main(page: ft.Page):
  init_db()
  page.title = "Zelalem Omni 56"
  page.theme_mode = ft.ThemeMode.DARK
  page.bgcolor = "#060911"
  page.padding = 0

  sw_running = [False]
  sw_seconds = [0.0]

  def notify(msg, col="#00FF88"):
    try:
      page.snack_bar = ft.SnackBar(
          ft.Text(msg, color="black", weight="bold"), bgcolor=col
      )
      page.snack_bar.open = True
      page.update()
    except Exception:
      pass

  lbl_live_clock = ft.Text("00:00:00", size=38, weight="bold", color="#00FF88")
  lbl_live_date = ft.Text("Sunday, Nov 15, 2026", size=12, color="#00E5FF")
  lbl_sw = ft.Text("00:00.0", size=34, weight="bold", color="#FFFFFF")

  def build_clock_tab():
    tf_alarm_time = ft.TextField(
        label="Alarm Time (HH:MM)", bgcolor="#0D1322", border_radius=12, expand=True
    )
    tf_alarm_lbl = ft.TextField(
        label="Label (Study/Sport)", bgcolor="#0D1322", border_radius=12, expand=True
    )
    alarm_col = ft.Column(spacing=8)

    def load_alarms():
      try:
        alarm_col.controls.clear()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        for aid, t_str, lbl, act in conn.execute(
            "SELECT id, time_str, label, active FROM alarms ORDER BY id DESC"
        ):
          alarm_col.controls.append(
              ft.Container(
                  bgcolor="#0D1322",
                  padding=12,
                  border_radius=14,
                  border=ft.border.all(1, "#00E5FF" if act else "#1E293B"),
                  content=ft.Row(
                      [
                          ft.Icon(
                              "alarm",
                              color="#00FF88" if act else "#64748B",
                              size=28,
                          ),
                          ft.Column(
                              [
                                  ft.Text(
                                      t_str,
                                      size=20,
                                      weight="bold",
                                      color="white",
                                  ),
                                  ft.Text(lbl, size=12, color="#94A3B8"),
                              ],
                              expand=True,
                              spacing=2,
                          ),
                          ft.IconButton(
                              icon="delete_outline",
                              icon_color="#F43F5E",
                              on_click=lambda e, x=aid: del_alarm(x),
                          ),
                      ],
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  ),
              )
          )
        conn.close()
        page.update()
      except Exception:
        pass

    def add_alarm(e):
      if not tf_alarm_time.value:
        notify("ሰዓት አስገባ!", "#F43F5E")
        return
      try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute(
            "INSERT INTO alarms (time_str, label, active) VALUES (?,?,1)",
            (tf_alarm_time.value.strip(), tf_alarm_lbl.value or "Alarm"),
        )
        conn.commit()
        conn.close()
        tf_alarm_time.value = ""
        tf_alarm_lbl.value = ""
        notify("⏰ Alarm ተቀምጧል!")
        load_alarms()
      except Exception:
        pass

    def del_alarm(aid):
      try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute("DELETE FROM alarms WHERE id=?", (aid,))
        conn.commit()
        conn.close()
        load_alarms()
      except Exception:
        pass

    def toggle_sw(e):
      sw_running[0] = not sw_running[0]
      page.update()

    def reset_sw(e):
      sw_running[0] = False
      sw_seconds[0] = 0.0
      lbl_sw.value = "00:00.0"
      page.update()

    load_alarms()
    return ft.Container(
        padding=16,
        content=ft.Column(
            [
                ft.Container(
                    padding=20,
                    border_radius=20,
                    gradient=ft.LinearGradient(
                        colors=["#0D1B2A", "#000814"],
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                    ),
                    border=ft.border.all(1.5, "#00E5FF"),
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Text(
                                "⚡ ATOMIC SYSTEM CLOCK",
                                size=10,
                                color="#00E5FF",
                                weight="bold",
                            ),
                            lbl_live_clock,
                            lbl_live_date,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                ),
                ft.Container(
                    bgcolor="#0D1322",
                    padding=16,
                    border_radius=16,
                    border=ft.border.all(1, "#1E293B"),
                    content=ft.Column(
                        [
                            ft.Text(
                                "⏱ STOPWATCH",
                                size=11,
                                color="#00FF88",
                                weight="bold",
                            ),
                            lbl_sw,
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        "▶ START/PAUSE",
                                        bgcolor="#00FF88",
                                        color="black",
                                        on_click=toggle_sw,
                                    ),
                                    ft.ElevatedButton(
                                        "🔄 RESET",
                                        bgcolor="#F43F5E",
                                        color="white",
                                        on_click=reset_sw,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                ft.Text(
                    "⏰ ALARMS", size=13, weight="bold", color="#00E5FF"
                ),
                ft.Row([tf_alarm_time, tf_alarm_lbl]),
                ft.ElevatedButton(
                    "➕ SET ALARM",
                    bgcolor="#00E5FF",
                    color="black",
                    height=44,
                    on_click=add_alarm,
                ),
                alarm_col,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=12,
        ),
    )

  def build_calc_tab():
    expr_txt = ft.Text("", size=16, color="#94A3B8")
    res_txt = ft.Text("0", size=36, weight="bold", color="#00FF88")

    def on_key(k):
      if k == "C":
        expr_txt.value = ""
        res_txt.value = "0"
      elif k == "⌫":
        expr_txt.value = expr_txt.value[:-1]
      elif k == "=":
        try:
          safe_env = {
              "sin": lambda x: math.sin(math.radians(x)),
              "cos": lambda x: math.cos(math.radians(x)),
              "tan": lambda x: math.tan(math.radians(x)),
              "sqrt": math.sqrt,
              "log": math.log10,
              "pi": math.pi,
              "e": math.e,
          }
          ans = eval(
              expr_txt.value.replace("×", "*")
              .replace("÷", "/")
              .replace("^", "**"),
              {"__builtins__": {}},
              safe_env,
          )
          res_txt.value = (
              f"{ans:.6g}" if isinstance(ans, float) else str(ans)
          )
        except Exception:
          res_txt.value = "Error"
      elif k in ["sin", "cos", "tan", "sqrt", "log"]:
        expr_txt.value += f"{k}("
      else:
        expr_txt.value += k
      page.update()

    rows_keys = [
        ["sin", "cos", "tan", "sqrt", "C"],
        ["log", "(", ")", "^", "⌫"],
        ["7", "8", "9", "÷", "pi"],
        ["4", "5", "6", "×", "e"],
        ["1", "2", "3", "-", "%"],
        ["0", ".", "=", "+"],
    ]

    grid_col = ft.Column(spacing=8)
    for r in rows_keys:
      row_ui = ft.Row(spacing=8)
      for k in r:
        is_eq = k == "="
        is_op = k in ["÷", "×", "-", "+", "^", "=", "C", "⌫"]
        bg = "#00FF88" if is_eq else ("#1E293B" if is_op else "#0D1322")
        fg = "#000000" if is_eq else ("#00E5FF" if is_op else "#FFFFFF")
        row_ui.controls.append(
            ft.Container(
                expand=2 if is_eq else 1,
                height=54,
                bgcolor=bg,
                border_radius=14,
                alignment=ft.alignment.center,
                on_click=lambda e, key=k: on_key(key),
                content=ft.Text(k, size=17, weight="bold", color=fg),
            )
        )
      grid_col.controls.append(row_ui)

    return ft.Container(
        padding=16,
        content=ft.Column(
            [
                ft.Container(
                    bgcolor="#0D1322",
                    padding=20,
                    border_radius=18,
                    border=ft.border.all(1, "#00E5FF"),
                    alignment=ft.alignment.bottom_right,
                    content=ft.Column(
                        [expr_txt, res_txt],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                ),
                grid_col,
            ],
            expand=True,
            spacing=14,
        ),
    )

  def build_56_tools_tab():
    dd_tool = ft.Dropdown(
        label="🛠️ Select Tool (1 - 56)",
        bgcolor="#0D1322",
        border_radius=12,
        options=[ft.dropdown.Option(t[0]) for t in TOOLS_CATALOG],
        value=TOOLS_CATALOG[0][0],
    )
    tf_input = ft.TextField(
        label=f"Input: {TOOLS_CATALOG[0][2]}",
        bgcolor="#0D1322",
        border_radius=12,
        value="1,-5,6",
    )
    lbl_result = ft.Text("Result...", size=18, weight="bold", color="#00FF88")
    search_tf = ft.TextField(
        label="🔍 Search 56 Tools...", bgcolor="#0D1322", border_radius=12
    )
    cards_col = ft.Column(spacing=8)

    def on_tool_select(e=None):
      for name, cat, hint in TOOLS_CATALOG:
        if name == dd_tool.value:
          tf_input.label = f"Input ({cat}): {hint}"
          break
      page.update()

    dd_tool.on_change = on_tool_select

    def run_selected_tool(e=None):
      res = execute_tool(dd_tool.value, tf_input.value or "")
      lbl_result.value = f"🎯 {res}"
      page.update()

    def pick_from_card(t_name, hint):
      dd_tool.value = t_name
      tf_input.label = f"Input: {hint}"
      page.update()
      notify(f"Selected: {t_name}", "#00E5FF")

    def render_catalog(e=None):
      cards_col.controls.clear()
      q = (search_tf.value or "").strip().lower()
      for name, cat, hint in TOOLS_CATALOG:
        if q and q not in name.lower() and q not in cat.lower():
          continue
        cards_col.controls.append(
            ft.Container(
                bgcolor="#0D1322",
                padding=12,
                border_radius=12,
                border=ft.border.all(1, "#1E293B"),
                on_click=lambda e, tn=name, th=hint: pick_from_card(tn, th),
                content=ft.Row(
                    [
                        ft.Container(
                            bgcolor="#162238",
                            padding=8,
                            border_radius=8,
                            content=ft.Text(
                                cat, size=10, color="#00E5FF", weight="bold"
                            ),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    name,
                                    size=13,
                                    weight="bold",
                                    color="white",
                                ),
                                ft.Text(
                                    f"Format: {hint}",
                                    size=11,
                                    color="#94A3B8",
                                ),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                        ft.Icon("bolt", color="#00FF88", size=20),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )
        )
      page.update()

    search_tf.on_change = render_catalog
    render_catalog()
    run_selected_tool()

    return ft.Container(
        padding=16,
        content=ft.Column(
            [
                ft.Container(
                    bgcolor="#0A192F",
                    padding=16,
                    border_radius=16,
                    border=ft.border.all(1.5, "#00FF88"),
                    content=ft.Column(
                        [
                            ft.Text(
                                "⚡ OMNI-TOOL EXECUTOR",
                                size=11,
                                weight="bold",
                                color="#00E5FF",
                            ),
                            dd_tool,
                            tf_input,
                            ft.ElevatedButton(
                                "🚀 EXECUTE TOOL",
                                bgcolor="#00FF88",
                                color="black",
                                height=44,
                                on_click=run_selected_tool,
                            ),
                            ft.Divider(color="white24"),
                            lbl_result,
                        ],
                        spacing=10,
                    ),
                ),
                search_tf,
                ft.Text(
                    "📋 56 Tools Catalog:",
                    size=12,
                    color="#94A3B8",
                    weight="bold",
                ),
                cards_col,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        ),
    )

  def build_vault_tab():
    tf_title = ft.TextField(
        label="Note Title", bgcolor="#0D1322", border_radius=12
    )
    tf_body = ft.TextField(
        label="Secret Details...",
        bgcolor="#0D1322",
        border_radius=12,
        multiline=True,
        min_lines=2,
    )
    notes_col = ft.Column(spacing=8)

    def load_notes():
      try:
        notes_col.controls.clear()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        for nid, t, b, ts in conn.execute(
            "SELECT id, title, body, ts FROM notes ORDER BY id DESC"
        ):
          notes_col.controls.append(
              ft.Container(
                  bgcolor="#0D1322",
                  padding=14,
                  border_radius=14,
                  border=ft.border.all(1, "#1E293B"),
                  content=ft.Row(
                      [
                          ft.Column(
                              [
                                  ft.Text(
                                      t, size=15, weight="bold", color="#00FF88"
                                  ),
                                  ft.Text(b, size=13, color="white"),
                                  ft.Text(ts, size=10, color="#64748B"),
                              ],
                              expand=True,
                              spacing=3,
                          ),
                          ft.IconButton(
                              icon="delete_outline",
                              icon_color="#F43F5E",
                              on_click=lambda e, x=nid: del_note(x),
                          ),
                      ],
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  ),
              )
          )
        conn.close()
        page.update()
      except Exception:
        pass

    def save_note(e):
      if not tf_title.value:
        notify("Enter title!", "#F43F5E")
        return
      try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        now_s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute(
            "INSERT INTO notes (title, body, ts) VALUES (?,?,?)",
            (tf_title.value.strip(), tf_body.value or "", now_s),
        )
        conn.commit()
        conn.close()
        tf_title.value = ""
        tf_body.value = ""
        notify("🔐 Saved to Offline Vault!")
        load_notes()
      except Exception:
        pass

    def del_note(nid):
      try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute("DELETE FROM notes WHERE id=?", (nid,))
        conn.commit()
        conn.close()
        load_notes()
      except Exception:
        pass

    load_notes()
    return ft.Container(
        padding=16,
        content=ft.Column(
            [
                ft.Text(
                    "🔐 OFFLINE SQLITE VAULT",
                    size=14,
                    weight="bold",
                    color="#00FF88",
                ),
                tf_title,
                tf_body,
                ft.ElevatedButton(
                    "💾 SAVE NOTE",
                    bgcolor="#00FF88",
                    color="black",
                    height=44,
                    on_click=save_note,
                ),
                ft.Divider(color="#1E293B"),
                notes_col,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        ),
    )

  def clock_worker():
    while True:
      now = datetime.datetime.now()
      lbl_live_clock.value = now.strftime("%I:%M:%S %p")
      lbl_live_date.value = now.strftime("%A, %b %d, %Y")
      if sw_running[0]:
        sw_seconds[0] += 0.2
        mins = int(sw_seconds[0]) // 60
        secs = sw_seconds[0] % 60
        lbl_sw.value = f"{mins:02d}:{secs:04.1f}"
      try:
        page.update()
      except Exception:
        break
      time.sleep(0.2)

  threading.Thread(target=clock_worker, daemon=True).start()

  body = ft.Container(expand=True, content=build_clock_tab())

  def on_nav(e):
    idx = e.control.selected_index
    body.content = [
        build_clock_tab,
        build_calc_tab,
        build_56_tools_tab,
        build_vault_tab,
    ][idx]()
    page.update()

  nav = ft.NavigationBar(
      bgcolor="#0D1322",
      selected_index=0,
      on_change=on_nav,
      destinations=[
          ft.NavigationDestination(icon="alarm", label="Clock"),
          ft.NavigationDestination(icon="calculate", label="Calc"),
          ft.NavigationDestination(icon="grid_view", label="56 Tools"),
          ft.NavigationDestination(icon="lock", label="Vault"),
      ],
  )

  page.add(body, nav)

# NEXUS_BUILD: 1794838272

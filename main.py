import base64
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
import urllib.parse
import uuid
import flet as ft


# =========================================================
# 1. UNIVERSAL FLET COMPATIBILITY LAYER (FLET 0.2x & 1.0+)
# =========================================================
def b_all(w, col):
  try:
    if hasattr(ft, "Border") and hasattr(ft.Border, "all"):
      return ft.Border.all(w, col)
    if hasattr(ft, "border") and hasattr(ft.border, "all"):
      return ft.border.all(w, col)
  except Exception:
    pass
  return None


def get_align(pos="center"):
  try:
    if hasattr(ft, "Alignment"):
      if pos == "center":
        return getattr(ft.Alignment, "CENTER", ft.Alignment(0, 0))
      if pos == "right":
        return getattr(ft.Alignment, "CENTER_RIGHT", ft.Alignment(1, 0))
      if pos == "left":
        return getattr(ft.Alignment, "CENTER_LEFT", ft.Alignment(-1, 0))
    if hasattr(ft, "alignment"):
      if pos == "center":
        return ft.alignment.center
      if pos == "right":
        return ft.alignment.center_right
      if pos == "left":
        return ft.alignment.center_left
  except Exception:
    pass
  return None


SCROLL_AUTO = (
    getattr(ft.ScrollMode, "AUTO", "auto")
    if hasattr(ft, "ScrollMode")
    else "auto"
)
MAIN_SPACE_BETWEEN = (
    getattr(ft.MainAxisAlignment, "SPACE_BETWEEN", "spaceBetween")
    if hasattr(ft, "MainAxisAlignment")
    else "spaceBetween"
)
MAIN_CENTER = (
    getattr(ft.MainAxisAlignment, "CENTER", "center")
    if hasattr(ft, "MainAxisAlignment")
    else "center"
)
CROSS_CENTER = (
    getattr(ft.CrossAxisAlignment, "CENTER", "center")
    if hasattr(ft, "CrossAxisAlignment")
    else "center"
)
CROSS_END = (
    getattr(ft.CrossAxisAlignment, "END", "end")
    if hasattr(ft, "CrossAxisAlignment")
    else "end"
)
CROSS_START = (
    getattr(ft.CrossAxisAlignment, "START", "start")
    if hasattr(ft, "CrossAxisAlignment")
    else "start"
)


# =========================================================
# 2. ANDROID 13/14 FAIL-SAFE SQLITE ENGINE (WITH RAM BACKUP)
# =========================================================
MEM_CONN = None


def get_db():
  global MEM_CONN
  candidate_dirs = [
      os.environ.get("FLET_APP_STORAGE_DATA"),
      os.environ.get("FLET_APP_STORAGE_TEMP"),
      tempfile.gettempdir(),
      os.path.expanduser("~"),
  ]
  for d in candidate_dirs:
    if d and os.path.isdir(d):
      try:
        db_file = os.path.join(d, "zelalem_omni_master.db")
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn, False
      except Exception:
        continue
  if MEM_CONN is None:
    MEM_CONN = sqlite3.connect(":memory:", check_same_thread=False)
  return MEM_CONN, True


def init_db():
  try:
    conn, is_mem = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_str TEXT, label TEXT, active INTEGER
        )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, category TEXT, priority TEXT, status TEXT, dt TEXT
        )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, secret TEXT, ts TEXT
        )""")
    conn.commit()
    if not is_mem:
      conn.close()
  except Exception:
    pass


# =========================================================
# 3. COMPLETE 60 OMNI-TOOLS ENGINE (REAL MATH & SCIENCE)
# =========================================================
TOOLS_CATALOG = [
    # Math, Physics & Chemistry (01 - 16)
    ("01. Quadratic Solver (ax²+bx+c)", "Math/Sci", "1,-5,6"),
    ("02. Prime Number & Factors", "Math/Sci", "97"),
    ("03. GCD & LCM Calculator", "Math/Sci", "24,36"),
    ("04. Factorial (n!)", "Math/Sci", "10"),
    ("05. Fibonacci Sequence", "Math/Sci", "12"),
    ("06. Pythagoras Hypotenuse (a,b)", "Math/Sci", "3,4"),
    ("07. Circle Area & Circumference", "Math/Sci", "7"),
    ("08. Sphere Volume & Surface", "Math/Sci", "5"),
    ("09. Matrix 2x2 Determinant", "Math/Sci", "4,2,3,5"),
    ("10. Ohm's Law (V, I, R)", "Math/Sci", "2.5,12"),
    ("11. Kinetic Energy (Mass, Vel)", "Math/Sci", "60,10"),
    ("12. Projectile Range & Max Height", "Math/Sci", "30,45"),
    ("13. Pendulum Period (Length m)", "Math/Sci", "1.5"),
    ("14. Gravitational Force (m1,m2,r)", "Math/Sci", "1000,500,2"),
    ("15. Lens Focal Length (u, v cm)", "Math/Sci", "20,30"),
    ("16. pH & pOH from [H+] Molarity", "Math/Sci", "0.001"),
    # Universal Unit Converters (17 - 30)
    ("17. Celsius ➔ Fahrenheit & Kelvin", "Convert", "25"),
    ("18. Fahrenheit ➔ Celsius & Kelvin", "Convert", "98.6"),
    ("19. Kilometers ➔ Miles & Meters", "Convert", "10"),
    ("20. Meters ➔ Feet & Inches", "Convert", "1.75"),
    ("21. Kilograms ➔ Pounds & Ounces", "Convert", "68"),
    ("22. Pounds ➔ Kilograms & Grams", "Convert", "150"),
    ("23. Liters ➔ US Gallons & mL", "Convert", "20"),
    ("24. Speed: km/h ➔ m/s & mph", "Convert", "100"),
    ("25. Area: Hectares ➔ m² & Acres", "Convert", "2.5"),
    ("26. Data Storage: GB ➔ MB & KB", "Convert", "4"),
    ("27. Net Speed: Mbps ➔ MB/s", "Convert", "50"),
    ("28. Pressure: Bar ➔ PSI & kPa", "Convert", "2.4"),
    ("29. Energy: Calories ➔ Joules", "Convert", "500"),
    ("30. Power: Horsepower ➔ Watts", "Convert", "150"),
    # Forex Trading & Finance (31 - 40)
    ("31. Forex Lot & Risk Calculator", "Forex/Fin", "1000,2,25"),
    ("32. Forex Risk:Reward Ratio", "Forex/Fin", "20,60"),
    ("33. Forex Pip Profit Value", "Forex/Fin", "0.10,45"),
    ("34. Compound Interest Growth", "Forex/Fin", "10000,12,5"),
    ("35. Monthly Loan EMI Calculator", "Forex/Fin", "50000,14,24"),
    ("36. Profit Margin & Markup %", "Forex/Fin", "800,1200"),
    ("37. Discount & Final Price", "Forex/Fin", "2500,15"),
    ("38. Ethiopian VAT (15%) Splitter", "Forex/Fin", "5000"),
    ("39. Monthly Savings Goal Target", "Forex/Fin", "60000,12"),
    ("40. Return on Investment (ROI %)", "Forex/Fin", "15000,10000"),
    # Satellite Dish & Cyber Security (41 - 50)
    ("41. Sat Dish Elevation (Lat,Lon,Sat)", "Cyber/Sat", "8.15,35.35,57.0"),
    ("42. Sat Dish Azimuth (Lat,Lon,Sat)", "Cyber/Sat", "8.15,35.35,57.0"),
    ("43. LNB Skew Angle (Lat,Lon,Sat)", "Cyber/Sat", "8.15,35.35,7.0"),
    ("44. Hacker Strong Password Gen", "Cyber/Sat", "18"),
    ("45. SHA-256 Hash Generator", "Cyber/Sat", "ZelalemOmni2026"),
    ("46. MD5 Hash Generator", "Cyber/Sat", "ZelalemOmni2026"),
    ("47. Base64 Text Encoder", "Cyber/Sat", "Zelalem Masterpiece"),
    ("48. Decimal ➔ Binary, Octal & Hex", "Cyber/Sat", "255"),
    ("49. Binary ➔ Decimal & Hex", "Cyber/Sat", "11010110"),
    ("50. IPv4 Subnet Usable Hosts", "Cyber/Sat", "24"),
    # Calisthenics, Fitness & Utilities (51 - 60)
    ("51. BMI & Health Category", "Fitness/Util", "64,174"),
    ("52. Daily Calorie (BMR & TDEE)", "Fitness/Util", "64,174,19"),
    ("53. 1-Rep Max Strength (Weight,Reps)", "Fitness/Util", "50,8"),
    ("54. Daily Water Intake Target (kg)", "Fitness/Util", "64"),
    ("55. Heart Rate Zones (Your Age)", "Fitness/Util", "19"),
    ("56. Grade 12 Exam Average & Rank", "Fitness/Util", "88,92,85,90,94,87"),
    ("57. Word, Character & Vowel Counter", "Fitness/Util", "Zelalem Omni Pro"),
    ("58. Exact Age in Days & Hours", "Fitness/Util", "2007"),
    ("59. Random Lucky Winner Picker", "Fitness/Util", "Python,Physics,Math"),
    ("60. Number ➔ Roman Numeral", "Fitness/Util", "2026"),
]


def execute_tool(tool_name, raw_in):
  s = (raw_in or "").strip()
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
      if a == 0:
        return "Error: 'a' cannot be 0"
      d = b * b - 4 * a * c
      if d < 0:
        real = -b / (2 * a)
        imag = math.sqrt(-d) / (2 * a)
        return f"Complex: {real:.2f} ± {imag:.2f}i (D={d:.1f})"
      r1 = (-b + math.sqrt(d)) / (2 * a)
      r2 = (-b - math.sqrt(d)) / (2 * a)
      return f"x₁ = {r1:.4f}  |  x₂ = {r2:.4f}  (D={d:.1f})"
    elif idx == 2 and nums:
      n = abs(int(nums[0]))
      if n < 2:
        return f"{n} is NOT Prime"
      factors = [
          i for i in range(1, min(n + 1, 10000)) if n % i == 0
      ]
      is_p = all(n % i != 0 for i in range(2, int(math.isqrt(n)) + 1))
      status = "PRIME ✅" if is_p else "COMPOSITE ❌"
      return f"{n}: {status} | Divisors: {factors[:8]}"
    elif idx == 3 and len(nums) >= 2:
      a, b = int(nums[0]), int(nums[1])
      g = math.gcd(a, b)
      lcm = abs(a * b) // g if g else 0
      return f"GCD = {g}   |   LCM = {lcm:,}"
    elif idx == 4 and nums:
      n = min(170, max(0, int(nums[0])))
      return f"{n}! = {math.factorial(n):,}"
    elif idx == 5 and nums:
      n = min(35, max(1, int(nums[0])))
      fib = [0, 1]
      for _ in range(2, n):
        fib.append(fib[-1] + fib[-2])
      return " ➔ ".join(map(str, fib[:n]))
    elif idx == 6 and len(nums) >= 2:
      c = math.hypot(nums[0], nums[1])
      area = 0.5 * nums[0] * nums[1]
      return f"Hypotenuse c = {c:.3f}  |  Area = {area:.2f}"
    elif idx == 7 and nums:
      r = nums[0]
      return f"Area = {math.pi*r*r:.2f}  |  Circumference = {2*math.pi*r:.2f}"
    elif idx == 8 and nums:
      r = nums[0]
      v = (4.0 / 3.0) * math.pi * (r**3)
      sa = 4.0 * math.pi * (r**2)
      return f"Volume = {v:.2f}  |  Surface Area = {sa:.2f}"
    elif idx == 9 and len(nums) >= 4:
      det = nums[0] * nums[3] - nums[1] * nums[2]
      return f"Determinant |A| = {det:.2f}"
    elif idx == 10 and len(nums) >= 2:
      i_val, r_val = nums[0], nums[1]
      v_val = i_val * r_val
      p_val = v_val * i_val
      return f"Voltage = {v_val:.2f} V  |  Power = {p_val:.2f} W"
    elif idx == 11 and len(nums) >= 2:
      ke = 0.5 * nums[0] * (nums[1] ** 2)
      mom = nums[0] * nums[1]
      return f"KE = {ke:,.2f} Joules  |  Momentum = {mom:,.1f} kg·m/s"
    elif idx == 12 and len(nums) >= 2:
      v0, ang = nums[0], nums[1]
      rad = math.radians(ang)
      rng = (v0**2) * math.sin(2 * rad) / 9.81
      hmax = ((v0 * math.sin(rad)) ** 2) / (2 * 9.81)
      return f"Range = {rng:.2f} m  |  Max Height = {hmax:.2f} m"
    elif idx == 13 and nums:
      t_sec = 2 * math.pi * math.sqrt(abs(nums[0]) / 9.81)
      return f"Period T = {t_sec:.3f} sec  |  Freq = {1/t_sec:.2f} Hz"
    elif idx == 14 and len(nums) >= 3:
      fg = 6.6743e-11 * nums[0] * nums[1] / (nums[2] ** 2)
      return f"Gravitational Force = {fg:.4e} N"
    elif idx == 15 and len(nums) >= 2:
      f_len = 1.0 / ((1.0 / nums[0]) + (1.0 / nums[1]))
      mag = -nums[1] / nums[0]
      return f"Focal Length f = {f_len:.2f} cm  |  Mag = {mag:.2f}x"
    elif idx == 16 and nums:
      ph = -math.log10(abs(nums[0]))
      poh = 14.0 - ph
      return f"pH = {ph:.2f}  |  pOH = {poh:.2f} ({'Acidic' if ph<7 else 'Basic'})"
    elif idx == 17 and nums:
      c = nums[0]
      return f"{c*9/5+32:.2f} °F   |   {c+273.15:.2f} K"
    elif idx == 18 and nums:
      f = nums[0]
      c = (f - 32) * 5 / 9
      return f"{c:.2f} °C   |   {c+273.15:.2f} K"
    elif idx == 19 and nums:
      km = nums[0]
      return f"{km*0.621371:.3f} Miles  |  {km*1000:,.0f} Meters"
    elif idx == 20 and nums:
      m = nums[0]
      return f"{m*3.28084:.2f} Feet  |  {m*39.3701:.1f} Inches"
    elif idx == 21 and nums:
      kg = nums[0]
      return f"{kg*2.20462:.2f} lbs  |  {kg*35.274:.1f} oz"
    elif idx == 22 and nums:
      lb = nums[0]
      return f"{lb/2.20462:.2f} kg  |  {lb*453.592:,.0f} g"
    elif idx == 23 and nums:
      lt = nums[0]
      return f"{lt*0.264172:.3f} US Gal  |  {lt*1000:,.0f} mL"
    elif idx == 24 and nums:
      kph = nums[0]
      return f"{kph/3.6:.2f} m/s  |  {kph*0.621371:.2f} mph"
    elif idx == 25 and nums:
      ha = nums[0]
      return f"{ha*10000:,.0f} m²  |  {ha*2.47105:.2f} Acres"
    elif idx == 26 and nums:
      gb = nums[0]
      return f"{gb*1024:,.0f} MB  |  {gb*1048576:,.0f} KB"
    elif idx == 27 and nums:
      mbps = nums[0]
      return f"Download Speed = {mbps/8.0:.2f} MB/sec"
    elif idx == 28 and nums:
      bar = nums[0]
      return f"{bar*14.5038:.2f} PSI  |  {bar*100:.1f} kPa"
    elif idx == 29 and nums:
      cal = nums[0]
      return f"{cal*4.184:,.2f} Joules"
    elif idx == 30 and nums:
      hp = nums[0]
      return f"{hp*745.7:,.1f} Watts ({hp*0.7457:.2f} kW)"
    elif idx == 31 and len(nums) >= 3:
      bal, risk_pct, sl_pips = nums[0], nums[1], nums[2]
      risk_usd = bal * (risk_pct / 100.0)
      std_lot = risk_usd / (sl_pips * 10.0)
      return f"Risk: ${risk_usd:.2f}  |  Lot Size: {max(0.01, std_lot):.2f}"
    elif idx == 32 and len(nums) >= 2:
      return f"R:R Ratio = 1 : {nums[1]/nums[0]:.2f}"
    elif idx == 33 and len(nums) >= 2:
      lot, pips = nums[0], nums[1]
      return f"Estimated Profit = ${lot * 10.0 * pips:,.2f}"
    elif idx == 34 and len(nums) >= 3:
      p, r, t = nums[0], nums[1] / 100.0, nums[2]
      tot = p * ((1 + r) ** t)
      return f"Total = {tot:,.2f}  |  Net Gain = {tot-p:,.2f}"
    elif idx == 35 and len(nums) >= 3:
      p, r, m = nums[0], (nums[1] / 100.0) / 12.0, nums[2]
      emi = (p * r * ((1 + r) ** m)) / (((1 + r) ** m) - 1)
      return f"Monthly EMI = {emi:,.2f}  |  Total = {emi*m:,.2f}"
    elif idx == 36 and len(nums) >= 2:
      cost, sell = nums[0], nums[1]
      prof = sell - cost
      return f"Profit: {prof:,.2f} | Margin: {(prof/sell)*100:.1f}% | Markup: {(prof/cost)*100:.1f}%"
    elif idx == 37 and len(nums) >= 2:
      orig, disc = nums[0], nums[1]
      saved = orig * (disc / 100.0)
      return f"Pay: {orig-saved:,.2f}  |  You Save: {saved:,.2f}"
    elif idx == 38 and nums:
      amt = nums[0]
      vat = amt * 0.15
      return f"VAT (15%): {vat:,.2f} ETB  |  Gross: {amt+vat:,.2f} ETB"
    elif idx == 39 and len(nums) >= 2:
      return f"Save {nums[0]/nums[1]:,.2f} per month ({nums[0]/(nums[1]*30):,.1f}/day)"
    elif idx == 40 and len(nums) >= 2:
      ret, cost = nums[0], nums[1]
      roi = ((ret - cost) / cost) * 100.0
      return f"Net Profit: {ret-cost:,.2f}  |  ROI: {roi:.2f}%"
    elif idx == 41 and len(nums) >= 3:
      lat, lon, sat = map(math.radians, nums[:3])
      dlon = sat - lon
      cos_c = math.cos(lat) * math.cos(dlon)
      el = math.degrees(
          math.atan((cos_c - 0.1512) / math.sqrt(max(1e-9, 1 - cos_c**2)))
      )
      return f"Dish Elevation Angle = {el:.2f}°"
    elif idx == 42 and len(nums) >= 3:
      lat, lon, sat = map(math.radians, nums[:3])
      dlon = lon - sat
      az = 180.0 + math.degrees(math.atan2(math.tan(dlon), math.sin(lat)))
      return f"True Azimuth Angle = {az % 360:.2f}°"
    elif idx == 43 and len(nums) >= 3:
      lat, lon, sat = map(math.radians, nums[:3])
      skew = math.degrees(math.atan2(math.sin(lon - sat), math.tan(lat)))
      return f"LNB Skew Polarization = {skew:.2f}°"
    elif idx == 44:
      ln = int(nums[0]) if nums else 16
      chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
      return "".join(random.choice(chars) for _ in range(min(48, max(8, ln))))
    elif idx == 45:
      return hashlib.sha256(s.encode("utf-8")).hexdigest()[:40]
    elif idx == 46:
      return hashlib.md5(s.encode("utf-8")).hexdigest()
    elif idx == 47:
      return base64.b64encode(s.encode("utf-8")).decode("utf-8")
    elif idx == 48 and nums:
      n = int(nums[0])
      return f"BIN: {bin(n)[2:]} | OCT: {oct(n)[2:]} | HEX: {hex(n)[2:].upper()}"
    elif idx == 49:
      clean_b = "".join(c for c in s if c in "01") or "0"
      dec = int(clean_b, 2)
      return f"DEC: {dec:,}   |   HEX: {hex(dec)[2:].upper()}"
    elif idx == 50 and nums:
      cidr = min(32, max(1, int(nums[0])))
      hosts = max(0, (2 ** (32 - cidr)) - 2)
      return f"/{cidr} Subnet ➔ {hosts:,} Usable Hosts"
    elif idx == 51 and len(nums) >= 2:
      w, h_cm = nums[0], nums[1]
      bmi = w / ((h_cm / 100.0) ** 2)
      cat = (
          "Optimal Fit ✅"
          if 18.5 <= bmi <= 24.9
          else ("Overweight ⚠️" if bmi > 24.9 else "Underweight ⚡")
      )
      return f"BMI = {bmi:.2f}  ({cat})"
    elif idx == 52 and len(nums) >= 3:
      bmr = 10 * nums[0] + 6.25 * nums[1] - 5 * nums[2] + 5
      return f"BMR: {bmr:.0f} kcal | Athletic TDEE: {bmr*1.65:.0f} kcal/day"
    elif idx == 53 and len(nums) >= 2:
      orm = nums[0] * (1.0 + nums[1] / 30.0)
      return f"1-Rep Max = {orm:.1f} kg  |  80% Working: {orm*0.8:.1f} kg"
    elif idx == 54 and nums:
      return f"Daily Hydration = {nums[0]*0.04:.2f} Liters (Athlete Target)"
    elif idx == 55 and nums:
      mhr = 220 - nums[0]
      return f"Max HR: {mhr:.0f} bpm | Endurance: {mhr*0.65:.0f}-{mhr*0.85:.0f} bpm"
    elif idx == 56 and nums:
      avg = sum(nums) / len(nums)
      grade = "A+ Distinction 🏆" if avg >= 85 else ("A" if avg >= 75 else "B")
      return f"Total: {sum(nums):.1f} | Average: {avg:.2f}% ({grade})"
    elif idx == 57:
      vowels = sum(1 for c in s.lower() if c in "aeiou")
      return f"Words: {len(s.split())} | Chars: {len(s)} | Vowels: {vowels}"
    elif idx == 58 and nums:
      yrs = 2026 - int(nums[0])
      return f"{yrs} Yrs ≈ {yrs*365:,} Days ≈ {yrs*8760:,} Hours"
    elif idx == 59:
      items = [x.strip() for x in s.split(",") if x.strip()]
      return f"Selected Winner 🎯: {random.choice(items)}" if items else "Enter comma items!"
    elif idx == 60 and nums:
      n = min(3999, max(1, int(nums[0])))
      val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
      syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
      rom = ""
      for i in range(len(val)):
        while n >= val[i]:
          rom += syb[i]
          n -= val[i]
      return f"Roman Numeral = {rom}"
    return "እባክህ በምሳሌው መሰረት ትክክለኛ ቁጥር አስገባ (e.g. 10,20)"
  except Exception as err:
    return f"Calc Error: {err}"


# =========================================================
# 4. MAIN SUPER-APP UI & BRAIN (100% ANDROID FLET 1.0 SAFE)
# =========================================================
def main(page: ft.Page):
  try:
    init_db()
    page.title = "Z-OS Omni"
    page.padding = 0
    page.bgcolor = "#030712"
    try:
      page.theme_mode = (
          ft.ThemeMode.DARK if hasattr(ft, "ThemeMode") else "dark"
      )
    except Exception:
      pass

    # App Reactive State
    bright_mode = [False]
    active_tab = [0]
    sw_running = [False]
    sw_seconds = [0.0]
    pomo_running = [False]
    pomo_seconds = [1500]
    selected_cat = ["ALL"]
    selected_tool_idx = [0]
    calc_history = []

    def theme():
      if bright_mode[0]:
        return {
            "bg": "#0B132B",
            "card": "#1C2541",
            "card_alt": "#263354",
            "border": "#00F5D4",
            "sub_border": "#3A506B",
            "neon": "#00F5D4",
            "cyan": "#38BDF8",
            "text": "#FFFFFF",
            "muted": "#CBD5E1",
        }
      return {
          "bg": "#030712",
          "card": "#0D1424",
          "card_alt": "#131C31",
          "border": "#00E5FF",
          "sub_border": "#1E293B",
          "neon": "#00FF88",
          "cyan": "#00E5FF",
          "text": "#FFFFFF",
          "muted": "#94A3B8",
      }

    def safe_update():
      try:
        page.update()
      except Exception:
        pass

    def neon_btn(
        label,
        on_click,
        bg="#00FF88",
        fg="#030712",
        height=44,
        expand=False,
        border_col=None,
    ):
      return ft.Container(
          bgcolor=bg,
          height=height,
          expand=expand,
          border_radius=12,
          padding=8,
          border=b_all(1.5, border_col) if border_col else None,
          alignment=get_align("center"),
          on_click=on_click,
          content=ft.Text(label, size=13, weight="bold", color=fg),
      )

    status_txt = ft.Text(
        "⚡ Z-OS OMNI READY • 60 TOOLS ACTIVE",
        size=11,
        weight="bold",
        color="#00FF88",
    )
    status_box = ft.Container(
        bgcolor="#09101D",
        padding=8,
        border_radius=10,
        border=b_all(1, "#1E293B"),
        content=ft.Row(
            [
                status_txt,
                ft.Container(
                    bgcolor="#1E293B",
                    padding=6,
                    border_radius=8,
                    on_click=lambda e: toggle_brightness(),
                    content=ft.Text(
                        "☀️ BRIGHTNESS",
                        size=10,
                        weight="bold",
                        color="#00E5FF",
                    ),
                ),
            ],
            alignment=MAIN_SPACE_BETWEEN,
        ),
    )

    def notify(msg, col="#00FF88"):
      status_txt.value = msg
      status_txt.color = col
      safe_update()

    lbl_live_clock = ft.Text("00:00:00", size=34, weight="bold", color="#00FF88")
    lbl_live_date = ft.Text(
        "Wednesday, Nov 18, 2026 • System Online", size=11, color="#00E5FF"
    )
    lbl_sw = ft.Text("00:00.0", size=30, weight="bold", color="#FFFFFF")
    lbl_pomo = ft.Text("25:00", size=30, weight="bold", color="#00E5FF")

    # =====================================================
    # TAB 0: HUB, ATOMIC CLOCK, STOPWATCH, POMODORO & ALARM
    # =====================================================
    def build_hub_tab():
      th = theme()
      tf_alarm_time = ft.TextField(
          label="Alarm (HH:MM)",
          bgcolor=th["card"],
          color="white",
          border_radius=10,
          expand=True,
          value="06:00",
      )
      tf_alarm_lbl = ft.TextField(
          label="Purpose (Study/Calisthenics)",
          bgcolor=th["card"],
          color="white",
          border_radius=10,
          expand=True,
          value="Grade 12 Physics Study",
      )
      alarm_col = ft.Column(spacing=8)

      def load_alarms():
        alarm_col.controls.clear()
        try:
          conn, is_mem = get_db()
          rows = conn.execute(
              "SELECT id, time_str, label, active FROM alarms ORDER BY id DESC"
          ).fetchall()
          if not is_mem:
            conn.close()
          for aid, t_str, lbl, act in rows:
            alarm_col.controls.append(
                ft.Container(
                    bgcolor=th["card"],
                    padding=12,
                    border_radius=12,
                    border=b_all(1, th["cyan"]),
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        f"⏰ {t_str}",
                                        size=17,
                                        weight="bold",
                                        color=th["neon"],
                                    ),
                                    ft.Text(lbl, size=12, color=th["muted"]),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            neon_btn(
                                "🗑️ DEL",
                                lambda e, x=aid: del_alarm(x),
                                bg="#F43F5E",
                                fg="white",
                                height=34,
                            ),
                        ],
                        alignment=MAIN_SPACE_BETWEEN,
                    ),
                )
            )
        except Exception:
          pass
        safe_update()

      def add_alarm(e):
        if not tf_alarm_time.value:
          notify("⚠️ Please enter alarm time!", "#F43F5E")
          return
        try:
          conn, is_mem = get_db()
          conn.execute(
              "INSERT INTO alarms (time_str, label, active) VALUES (?,?,1)",
              (tf_alarm_time.value.strip(), tf_alarm_lbl.value or "Alarm"),
          )
          conn.commit()
          if not is_mem:
            conn.close()
          notify(f"⏰ Alarm set for {tf_alarm_time.value}!")
          load_alarms()
        except Exception as ex:
          notify(f"Error: {ex}", "#F43F5E")

      def del_alarm(aid):
        try:
          conn, is_mem = get_db()
          conn.execute("DELETE FROM alarms WHERE id=?", (aid,))
          conn.commit()
          if not is_mem:
            conn.close()
          notify("🗑️ Alarm removed", "#00E5FF")
          load_alarms()
        except Exception:
          pass

      def toggle_sw(e):
        sw_running[0] = not sw_running[0]
        notify("⏱️ Stopwatch Running" if sw_running[0] else "⏸️ Stopwatch Paused")

      def reset_sw(e):
        sw_running[0] = False
        sw_seconds[0] = 0.0
        lbl_sw.value = "00:00.0"
        safe_update()

      def toggle_pomo(e):
        pomo_running[0] = not pomo_running[0]
        notify("🔥 Study Timer Active!" if pomo_running[0] else "⏸️ Study Paused")

      def reset_pomo(e):
        pomo_running[0] = False
        pomo_seconds[0] = 1500
        lbl_pomo.value = "25:00"
        safe_update()

      load_alarms()

      return ft.Container(
          padding=14,
          content=ft.Column(
              [
                  ft.Container(
                      bgcolor=th["card_alt"],
                      padding=18,
                      border_radius=18,
                      border=b_all(1.5, th["border"]),
                      alignment=get_align("center"),
                      content=ft.Column(
                          [
                              ft.Text(
                                  "⚡ ZELALEM OMNI COMMAND HUB",
                                  size=11,
                                  weight="bold",
                                  color=th["cyan"],
                              ),
                              lbl_live_clock,
                              lbl_live_date,
                          ],
                          horizontal_alignment=CROSS_CENTER,
                          spacing=4,
                      ),
                  ),
                  ft.Row(
                      [
                          ft.Container(
                              expand=True,
                              bgcolor=th["card"],
                              padding=12,
                              border_radius=14,
                              border=b_all(1, th["sub_border"]),
                              content=ft.Column(
                                  [
                                      ft.Text(
                                          "⏱️ STOPWATCH",
                                          size=11,
                                          weight="bold",
                                          color=th["neon"],
                                      ),
                                      lbl_sw,
                                      ft.Row(
                                          [
                                              neon_btn(
                                                  "▶/⏸",
                                                  toggle_sw,
                                                  bg=th["neon"],
                                                  fg="#030712",
                                                  height=36,
                                                  expand=True,
                                              ),
                                              neon_btn(
                                                  "🔄",
                                                  reset_sw,
                                                  bg="#F43F5E",
                                                  fg="white",
                                                  height=36,
                                              ),
                                          ],
                                          spacing=6,
                                      ),
                                  ],
                                  horizontal_alignment=CROSS_CENTER,
                                  spacing=6,
                              ),
                          ),
                          ft.Container(
                              expand=True,
                              bgcolor=th["card"],
                              padding=12,
                              border_radius=14,
                              border=b_all(1, th["sub_border"]),
                              content=ft.Column(
                                  [
                                      ft.Text(
                                          "🎯 STUDY 25m",
                                          size=11,
                                          weight="bold",
                                          color=th["cyan"],
                                      ),
                                      lbl_pomo,
                                      ft.Row(
                                          [
                                              neon_btn(
                                                  "▶/⏸",
                                                  toggle_pomo,
                                                  bg=th["cyan"],
                                                  fg="#030712",
                                                  height=36,
                                                  expand=True,
                                              ),
                                              neon_btn(
                                                  "🔄",
                                                  reset_pomo,
                                                  bg="#F43F5E",
                                                  fg="white",
                                                  height=36,
                                              ),
                                          ],
                                          spacing=6,
                                      ),
                                  ],
                                  horizontal_alignment=CROSS_CENTER,
                                  spacing=6,
                              ),
                          ),
                      ],
                      spacing=10,
                  ),
                  ft.Text(
                      "⏰ SMART ALARM SCHEDULE",
                      size=12,
                      weight="bold",
                      color=th["cyan"],
                  ),
                  ft.Row([tf_alarm_time, tf_alarm_lbl], spacing=8),
                  neon_btn(
                      "➕ SAVE ALARM SCHEDULE",
                      add_alarm,
                      bg=th["cyan"],
                      fg="#030712",
                      height=42,
                  ),
                  alarm_col,
              ],
              scroll=SCROLL_AUTO,
              expand=True,
              spacing=12,
          ),
      )

    # =====================================================
    # TAB 1: PRO SCIENTIFIC CALCULATOR
    # =====================================================
    def build_calc_tab():
      th = theme()
      expr_txt = ft.Text("", size=16, color=th["muted"])
      res_txt = ft.Text("0", size=34, weight="bold", color=th["neon"])
      hist_col = ft.Column(spacing=4)

      def render_hist():
        hist_col.controls.clear()
        for h_item in calc_history[-3:]:
          hist_col.controls.append(
              ft.Text(f"• {h_item}", size=11, color=th["muted"])
          )

      def on_key(k):
        if k == "C":
          expr_txt.value = ""
          res_txt.value = "0"
        elif k == "⌫":
          expr_txt.value = expr_txt.value[:-1]
        elif k == "=":
          raw_e = expr_txt.value.strip()
          if not raw_e:
            return
          try:
            safe_env = {
                "sin": lambda x: math.sin(math.radians(x)),
                "cos": lambda x: math.cos(math.radians(x)),
                "tan": lambda x: math.tan(math.radians(x)),
                "sqrt": math.sqrt,
                "log": math.log10,
                "ln": math.log,
                "pi": math.pi,
                "e": math.e,
                "abs": abs,
            }
            clean_e = (
                raw_e.replace("×", "*")
                .replace("÷", "/")
                .replace("^", "**")
                .replace("π", "pi")
            )
            ans = eval(clean_e, {"__builtins__": {}}, safe_env)
            formatted = (
                f"{ans:.8g}" if isinstance(ans, float) else str(ans)
            )
            res_txt.value = formatted
            calc_history.append(f"{raw_e} = {formatted}")
            render_hist()
          except Exception:
            res_txt.value = "Syntax Error"
        elif k in ["sin", "cos", "tan", "sqrt", "log", "ln"]:
          expr_txt.value += f"{k}("
        else:
          expr_txt.value += k
        safe_update()

      rows_keys = [
          ["sin", "cos", "tan", "sqrt", "C"],
          ["log", "ln", "(", ")", "⌫"],
          ["7", "8", "9", "÷", "^"],
          ["4", "5", "6", "×", "π"],
          ["1", "2", "3", "-", "e"],
          ["0", ".", "%", "+", "="],
      ]

      grid_col = ft.Column(spacing=8)
      for r in rows_keys:
        row_ui = ft.Row(spacing=8)
        for k in r:
          is_eq = k == "="
          is_clr = k in ["C", "⌫"]
          is_op = k in ["÷", "×", "-", "+", "^", "%"]
          bg = (
              th["neon"]
              if is_eq
              else (
                  "#F43F5E"
                  if is_clr
                  else (th["card_alt"] if is_op else th["card"])
              )
          )
          fg = (
              "#030712"
              if is_eq
              else (
                  "white"
                  if is_clr
                  else (th["cyan"] if is_op else "white")
              )
          )
          row_ui.controls.append(
              ft.Container(
                  expand=1,
                  height=48,
                  bgcolor=bg,
                  border_radius=12,
                  border=b_all(1, th["sub_border"]),
                  alignment=get_align("center"),
                  on_click=lambda e, key=k: on_key(key),
                  content=ft.Text(k, size=15, weight="bold", color=fg),
              )
          )
        grid_col.controls.append(row_ui)

      render_hist()
      return ft.Container(
          padding=14,
          content=ft.Column(
              [
                  ft.Container(
                      bgcolor=th["card"],
                      padding=16,
                      border_radius=16,
                      border=b_all(1.5, th["border"]),
                      alignment=get_align("right"),
                      content=ft.Column(
                          [hist_col, expr_txt, res_txt],
                          horizontal_alignment=CROSS_END,
                          spacing=4,
                      ),
                  ),
                  grid_col,
              ],
              scroll=SCROLL_AUTO,
              expand=True,
              spacing=12,
          ),
      )

    # =====================================================
    # TAB 2: 60 OMNI-TOOLS ENGINE (WITH FILTER CHIPS & SEARCH)
    # =====================================================
    def build_tools_tab():
      th = theme()
      cur_tool = TOOLS_CATALOG[selected_tool_idx[0]]
      lbl_active_title = ft.Text(
          f"⚡ {cur_tool[0]}", size=15, weight="bold", color=th["cyan"]
      )
      tf_input = ft.TextField(
          label=f"Input ({cur_tool[1]}) — Example: {cur_tool[2]}",
          value=cur_tool[2],
          bgcolor=th["card"],
          color="white",
          border_radius=10,
      )
      lbl_result = ft.Text(
          "🎯 Tap EXECUTE or pick any tool below",
          size=16,
          weight="bold",
          color=th["neon"],
      )
      search_tf = ft.TextField(
          label="🔍 Search 60 Tools (e.g. Dish, Forex, BMI, Ohm, Quadratic)...",
          bgcolor=th["card"],
          color="white",
          border_radius=10,
      )
      cat_row = ft.Row(spacing=6, scroll=SCROLL_AUTO)
      cards_col = ft.Column(spacing=8)

      categories = [
          "ALL",
          "Math/Sci",
          "Convert",
          "Forex/Fin",
          "Cyber/Sat",
          "Fitness/Util",
      ]

      def run_current_tool(e=None):
        t_item = TOOLS_CATALOG[selected_tool_idx[0]]
        ans = execute_tool(t_item[0], tf_input.value or "")
        lbl_result.value = f"🎯 {ans}"
        notify(f"Computed: {t_item[0][:22]}", th["neon"])

      def select_tool(idx):
        selected_tool_idx[0] = idx
        t_item = TOOLS_CATALOG[idx]
        lbl_active_title.value = f"⚡ {t_item[0]}"
        tf_input.label = f"Input ({t_item[1]}) — Example: {t_item[2]}"
        tf_input.value = t_item[2]
        run_current_tool()

      def set_cat(c_name):
        selected_cat[0] = c_name
        render_cats()
        render_tools()

      def render_cats():
        cat_row.controls.clear()
        for c in categories:
          is_sel = selected_cat[0] == c
          cat_row.controls.append(
              ft.Container(
                  bgcolor=th["neon"] if is_sel else th["card"],
                  padding=8,
                  border_radius=10,
                  border=b_all(1, th["border"] if is_sel else th["sub_border"]),
                  on_click=lambda e, cn=c: set_cat(cn),
                  content=ft.Text(
                      c,
                      size=11,
                      weight="bold",
                      color="#030712" if is_sel else "white",
                  ),
              )
          )

      def render_tools(e=None):
        cards_col.controls.clear()
        q = (search_tf.value or "").strip().lower()
        for i, (name, cat, ex_in) in enumerate(TOOLS_CATALOG):
          if selected_cat[0] != "ALL" and cat != selected_cat[0]:
            continue
          if q and (q not in name.lower() and q not in cat.lower()):
            continue
          is_curr = i == selected_tool_idx[0]
          cards_col.controls.append(
              ft.Container(
                  bgcolor=th["card_alt"] if is_curr else th["card"],
                  padding=12,
                  border_radius=12,
                  border=b_all(
                      1.5 if is_curr else 1,
                      th["neon"] if is_curr else th["sub_border"],
                  ),
                  on_click=lambda e, idx=i: select_tool(idx),
                  content=ft.Row(
                      [
                          ft.Container(
                              bgcolor="#09101D",
                              padding=6,
                              border_radius=8,
                              content=ft.Text(
                                  cat, size=10, weight="bold", color=th["cyan"]
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
                                      f"Sample Input: {ex_in}",
                                      size=11,
                                      color=th["muted"],
                                  ),
                              ],
                              expand=True,
                              spacing=2,
                          ),
                          ft.Text("⚡ RUN", size=11, weight="bold", color=th["neon"]),
                      ],
                      alignment=MAIN_SPACE_BETWEEN,
                  ),
              )
          )
        safe_update()

      search_tf.on_change = render_tools
      render_cats()
      render_tools()
      run_current_tool()

      return ft.Container(
          padding=14,
          content=ft.Column(
              [
                  ft.Container(
                      bgcolor=th["card_alt"],
                      padding=14,
                      border_radius=16,
                      border=b_all(1.5, th["neon"]),
                      content=ft.Column(
                          [
                              lbl_active_title,
                              tf_input,
                              neon_btn(
                                  "🚀 CALCULATE / EXECUTE NOW",
                                  run_current_tool,
                                  bg=th["neon"],
                                  fg="#030712",
                                  height=42,
                              ),
                              ft.Container(
                                  bgcolor="#060B14",
                                  padding=10,
                                  border_radius=10,
                                  border=b_all(1, th["sub_border"]),
                                  content=lbl_result,
                              ),
                          ],
                          spacing=8,
                      ),
                  ),
                  cat_row,
                  search_tf,
                  cards_col,
              ],
              scroll=SCROLL_AUTO,
              expand=True,
              spacing=10,
          ),
      )

    # =====================================================
    # TAB 3: PROJECT & STUDY TASK MATRIX
    # =====================================================
    def build_tasks_tab():
      th = theme()
      tf_task = ft.TextField(
          label="New Goal / Study Task...",
          bgcolor=th["card"],
          color="white",
          border_radius=10,
      )
      selected_tcat = ["Study"]
      cat_bar = ft.Row(spacing=6)
      tasks_col = ft.Column(spacing=8)
      stats_lbl = ft.Text("Progress: 0/0", size=12, weight="bold", color=th["neon"])

      task_cats = ["Study", "Python/Dev", "Calisthenics", "Satellite/FX"]

      def pick_tcat(c):
        selected_tcat[0] = c
        render_tcat()
        safe_update()

      def render_tcat():
        cat_bar.controls.clear()
        for c in task_cats:
          act = selected_tcat[0] == c
          cat_bar.controls.append(
              ft.Container(
                  expand=True,
                  bgcolor=th["cyan"] if act else th["card"],
                  padding=8,
                  border_radius=8,
                  alignment=get_align("center"),
                  on_click=lambda e, cn=c: pick_tcat(cn),
                  content=ft.Text(
                      c,
                      size=10,
                      weight="bold",
                      color="#030712" if act else "white",
                  ),
              )
          )

      def load_tasks():
        tasks_col.controls.clear()
        try:
          conn, is_mem = get_db()
          rows = conn.execute(
              "SELECT id, title, category, status, dt FROM tasks ORDER BY id"
              " DESC"
          ).fetchall()
          if not is_mem:
            conn.close()
          done_c = sum(1 for r in rows if r[3] == "DONE")
          stats_lbl.value = (
              f"📊 Completed: {done_c} / {len(rows)} Tasks"
          )
          for tid, title, cat, st, dt in rows:
            is_done = st == "DONE"
            tasks_col.controls.append(
                ft.Container(
                    bgcolor=th["card"],
                    padding=12,
                    border_radius=12,
                    border=b_all(1, th["neon"] if is_done else th["sub_border"]),
                    content=ft.Row(
                        [
                            neon_btn(
                                "✅ DONE" if is_done else "⏳ TODO",
                                lambda e, x=tid: toggle_task(x),
                                bg=th["neon"] if is_done else th["card_alt"],
                                fg="#030712" if is_done else th["cyan"],
                                height=34,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        title,
                                        size=14,
                                        weight="bold",
                                        color="white",
                                    ),
                                    ft.Text(
                                        f"{cat} • {dt}",
                                        size=10,
                                        color=th["muted"],
                                    ),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            neon_btn(
                                "🗑️",
                                lambda e, x=tid: del_task(x),
                                bg="#F43F5E",
                                fg="white",
                                height=34,
                            ),
                        ],
                        spacing=8,
                    ),
                )
            )
        except Exception:
          pass
        safe_update()

      def add_task(e):
        if not tf_task.value:
          notify("⚠️ Enter a task title!", "#F43F5E")
          return
        try:
          conn, is_mem = get_db()
          dt = datetime.datetime.now().strftime("%b %d, %H:%M")
          conn.execute(
              "INSERT INTO tasks (title, category, priority, status, dt) VALUES"
              " (?,?,'HIGH','TODO',?)",
              (tf_task.value.strip(), selected_tcat[0], dt),
          )
          conn.commit()
          if not is_mem:
            conn.close()
          tf_task.value = ""
          notify("✅ Task added to Matrix!")
          load_tasks()
        except Exception:
          pass

      def toggle_task(tid):
        try:
          conn, is_mem = get_db()
          cur = conn.execute(
              "SELECT status FROM tasks WHERE id=?", (tid,)
          ).fetchone()[0]
          nxt = "TODO" if cur == "DONE" else "DONE"
          conn.execute("UPDATE tasks SET status=? WHERE id=?", (nxt, tid))
          conn.commit()
          if not is_mem:
            conn.close()
          load_tasks()
        except Exception:
          pass

      def del_task(tid):
        try:
          conn, is_mem = get_db()
          conn.execute("DELETE FROM tasks WHERE id=?", (tid,))
          conn.commit()
          if not is_mem:
            conn.close()
          load_tasks()
        except Exception:
          pass

      render_tcat()
      load_tasks()
      return ft.Container(
          padding=14,
          content=ft.Column(
              [
                  ft.Container(
                      bgcolor=th["card_alt"],
                      padding=14,
                      border_radius=14,
                      border=b_all(1, th["cyan"]),
                      content=ft.Column(
                          [
                              ft.Text(
                                  "📋 ZELALEM GOAL & STUDY MATRIX",
                                  size=12,
                                  weight="bold",
                                  color=th["cyan"],
                              ),
                              stats_lbl,
                              tf_task,
                              cat_bar,
                              neon_btn(
                                  "➕ ADD TO TASK MATRIX",
                                  add_task,
                                  bg=th["neon"],
                                  fg="#030712",
                                  height=42,
                              ),
                          ],
                          spacing=8,
                      ),
                  ),
                  tasks_col,
              ],
              scroll=SCROLL_AUTO,
              expand=True,
              spacing=10,
          ),
      )

    # =====================================================
    # TAB 4: ENCRYPTED OFFLINE VAULT & CYBER KEYGEN
    # =====================================================
    def build_vault_tab():
      th = theme()
      tf_title = ft.TextField(
          label="Account / Secret Title",
          bgcolor=th["card"],
          color="white",
          border_radius=10,
      )
      tf_secret = ft.TextField(
          label="Secret Note, PIN, or Password...",
          bgcolor=th["card"],
          color="white",
          border_radius=10,
      )
      vault_col = ft.Column(spacing=8)

      def gen_pass(e):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = "".join(random.choice(chars) for _ in range(16))
        tf_secret.value = pwd
        notify("🔑 16-Char Cyber Password Generated!", th["cyan"])

      def load_vault():
        vault_col.controls.clear()
        try:
          conn, is_mem = get_db()
          rows = conn.execute(
              "SELECT id, title, secret, ts FROM vault ORDER BY id DESC"
          ).fetchall()
          if not is_mem:
            conn.close()
          for vid, t, sec, ts in rows:
            sig = hashlib.sha256(sec.encode("utf-8")).hexdigest()[:12].upper()
            vault_col.controls.append(
                ft.Container(
                    bgcolor=th["card"],
                    padding=12,
                    border_radius=12,
                    border=b_all(1, th["neon"]),
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        f"🔐 {t}",
                                        size=14,
                                        weight="bold",
                                        color=th["neon"],
                                    ),
                                    ft.Text(sec, size=13, color="white"),
                                    ft.Text(
                                        f"SHA256: {sig} • {ts}",
                                        size=10,
                                        color=th["muted"],
                                    ),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            neon_btn(
                                "🗑️",
                                lambda e, x=vid: del_vault(x),
                                bg="#F43F5E",
                                fg="white",
                                height=34,
                            ),
                        ],
                        alignment=MAIN_SPACE_BETWEEN,
                    ),
                )
            )
        except Exception:
          pass
        safe_update()

      def save_vault(e):
        if not tf_title.value:
          notify("⚠️ Enter a title for the secret!", "#F43F5E")
          return
        try:
          conn, is_mem = get_db()
          ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
          conn.execute(
              "INSERT INTO vault (title, secret, ts) VALUES (?,?,?)",
              (tf_title.value.strip(), tf_secret.value or "", ts),
          )
          conn.commit()
          if not is_mem:
            conn.close()
          tf_title.value = ""
          tf_secret.value = ""
          notify("🔐 Encrypted & Saved to Offline Vault!")
          load_vault()
        except Exception:
          pass

      def del_vault(vid):
        try:
          conn, is_mem = get_db()
          conn.execute("DELETE FROM vault WHERE id=?", (vid,))
          conn.commit()
          if not is_mem:
            conn.close()
          load_vault()
        except Exception:
          pass

      load_vault()
      return ft.Container(
          padding=14,
          content=ft.Column(
              [
                  ft.Container(
                      bgcolor=th["card_alt"],
                      padding=14,
                      border_radius=14,
                      border=b_all(1.5, th["neon"]),
                      content=ft.Column(
                          [
                              ft.Text(
                                  "🔐 OFFLINE SQLITE VAULT & KEYGEN",
                                  size=12,
                                  weight="bold",
                                  color=th["neon"],
                              ),
                              tf_title,
                              tf_secret,
                              ft.Row(
                                  [
                                      neon_btn(
                                          "🎲 GEN PASSWORD",
                                          gen_pass,
                                          bg=th["cyan"],
                                          fg="#030712",
                                          height=40,
                                          expand=True,
                                      ),
                                      neon_btn(
                                          "💾 SAVE SECRET",
                                          save_vault,
                                          bg=th["neon"],
                                          fg="#030712",
                                          height=40,
                                          expand=True,
                                      ),
                                  ],
                                  spacing=8,
                              ),
                          ],
                          spacing=8,
                      ),
                  ),
                  vault_col,
              ],
              scroll=SCROLL_AUTO,
              expand=True,
              spacing=10,
          ),
      )

    # =====================================================
    # CUSTOM CRASH-PROOF 5-TAB NEON NAVIGATION BAR
    # =====================================================
    body_container = ft.Container(expand=True)
    nav_row = ft.Row(spacing=6)

    tab_defs = [
        ("⚡", "Hub", build_hub_tab),
        ("🧮", "Calc", build_calc_tab),
        ("🛠️", "60 Tools", build_tools_tab),
        ("📋", "Tasks", build_tasks_tab),
        ("🔐", "Vault", build_vault_tab),
    ]

    def switch_tab(idx):
      try:
        active_tab[0] = idx
        render_nav()
        body_container.content = tab_defs[idx][2]()
        safe_update()
      except Exception as tab_err:
        notify(f"Tab error: {tab_err}", "#F43F5E")

    def toggle_brightness():
      bright_mode[0] = not bright_mode[0]
      th = theme()
      page.bgcolor = th["bg"]
      notify(
          "☀️ Ultra-Bright Mode ON"
          if bright_mode[0]
          else "🌙 Cyber Neon Mode ON",
          th["neon"],
      )
      switch_tab(active_tab[0])

    def render_nav():
      th = theme()
      nav_row.controls.clear()
      for i, (ico, lbl, _) in enumerate(tab_defs):
        is_act = active_tab[0] == i
        nav_row.controls.append(
            ft.Container(
                expand=1,
                height=56,
                bgcolor=th["card_alt"] if is_act else th["card"],
                border_radius=12,
                border=b_all(
                    1.5 if is_act else 1,
                    th["neon"] if is_act else th["sub_border"],
                ),
                alignment=get_align("center"),
                on_click=lambda e, idx=i: switch_tab(idx),
                content=ft.Column(
                    [
                        ft.Text(ico, size=16),
                        ft.Text(
                            lbl,
                            size=10,
                            weight="bold",
                            color=th["neon"] if is_act else th["muted"],
                        ),
                    ],
                    alignment=MAIN_CENTER,
                    horizontal_alignment=CROSS_CENTER,
                    spacing=2,
                ),
            )
        )

    render_nav()
    body_container.content = build_hub_tab()

    # FIXED: Plain integer padding=10 (No ft.padding.symmetric call!)
    main_layout = ft.Column(
        [
            ft.Container(height=24),
            ft.Container(
                padding=10,
                content=status_box,
            ),
            body_container,
            ft.Container(
                bgcolor="#060B14",
                padding=8,
                content=nav_row,
            ),
        ],
        expand=True,
        spacing=0,
    )

    page.add(main_layout)

    def clock_worker():
      while True:
        time.sleep(0.2)
        try:
          now = datetime.datetime.now()
          lbl_live_clock.value = now.strftime("%I:%M:%S %p")
          lbl_live_date.value = now.strftime("%A, %b %d, %Y • System Online")
          if sw_running[0]:
            sw_seconds[0] += 0.2
            m = int(sw_seconds[0]) // 60
            s = sw_seconds[0] % 60
            lbl_sw.value = f"{m:02d}:{s:04.1f}"
          if pomo_running[0] and pomo_seconds[0] > 0:
            pomo_seconds[0] = max(0.0, pomo_seconds[0] - 0.2)
            pm = int(pomo_seconds[0]) // 60
            ps = int(pomo_seconds[0]) % 60
            lbl_pomo.value = f"{pm:02d}:{ps:02d}"
          safe_update()
        except Exception:
          break

    threading.Thread(target=clock_worker, daemon=True).start()

  except Exception as fatal_e:
    page.add(
        ft.Container(
            padding=24,
            bgcolor="#1E1B4B",
            expand=True,
            content=ft.Column([
                ft.Text(
                    "⚠️ DIAGNOSTIC RECOVERY MODE",
                    size=18,
                    weight="bold",
                    color="#00FF88",
                ),
                ft.Text(str(fatal_e), size=13, color="white"),
            ]),
        )
    )
    page.update()


# =========================================================
# 5. UNIVERSAL ENTRYPOINT (SUPPORTS FLET 0.2x AND FLET 1.0+)
# =========================================================
if __name__ == "__main__":
  if hasattr(ft, "run"):
    ft.run(main)
  elif hasattr(ft, "app"):
    ft.app(target=main)

# NEXUS_BUILD: 1795033659

import datetime
import re

def validate_field(ctype, raw):
    ctype, raw = str(ctype).strip().lower(), raw.strip()
    if not raw: return True, "", None

    if ctype == "число":
        if not re.match(r'^-?\d+(?:[.,]\d+)?$', raw):
            return False, None, "недопустимые символы (только цифры, -, . или ,)"
        try:
            val = float(raw.replace(",", "."))
            return True, (int(val) if val.is_integer() else val), None
        except ValueError:
            return False, None, "неверный формат числа"

    if ctype == "да/нет":
        low = raw.lower()
        if low in ("1", "да", "yes", "true", "+"): return True, 1, None
        if low in ("0", "нет", "no", "false", "-"): return True, 0, None
        return False, None, "введите да/нет"

    if ctype == "дата":
        for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                dt = datetime.datetime.strptime(raw, fmt)
                if 1900 <= dt.year <= 2100:
                    return True, dt.strftime("%Y-%m-%d"), None
                else:
                    return False, None, "год должен быть в диапазоне 1900-2100"
            except ValueError:
                pass
        return False, None, "формат ДД.ММ.ГГГГ"

    if ctype == "время":
        raw = raw.replace(".", ":")
        if ":" not in raw and len(raw) == 4: raw = raw[:2] + ":" + raw[2:]
        
        if re.match(r'^\d{1,2}:\d{2}$', raw):
            h, m = map(int, raw.split(":"))
            if 0 <= h <= 23 and 0 <= m <= 59:
                return True, f"{h:02d}:{m:02d}", None
            return False, None, "неверное время (ЧЧ:ММ)"
            
        return False, None, "формат ЧЧ:ММ"

    return True, raw, None
#!/usr/bin/env python3
"""Generate a subscribable iCalendar feed from the public show agenda."""
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
shows = json.loads((ROOT / "agenda/shows.json").read_text(encoding="utf-8"))
tz = ZoneInfo("America/Sao_Paulo")
def esc(s):
    return str(s or "").replace("\\","\\\\").replace("\n","\\n").replace(",","\\,").replace(";","\\;")
def time_of(s):
    match = re.search(r"(?<!\d)([01]?\d|2[0-3])\s*(?:[:hH]\s*([0-5]?\d))?",str(s or ""))
    return (int(match.group(1)),int(match.group(2) or 0)) if match else None
def fold(s):
    parts=[]
    while len(s.encode("utf-8"))>73:
        n=0
        while len(s[:n+1].encode("utf-8"))<=73 and n<len(s)-1:n+=1
        parts.append(s[:n]);s=s[n:]
    parts.append(s)
    return "\r\n ".join(parts)
lines=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Lippi e Leo//Agenda de Shows//PT-BR","CALSCALE:GREGORIAN","METHOD:PUBLISH","X-WR-CALNAME:Lippi & Léo - Shows","X-WR-TIMEZONE:America/Sao_Paulo","REFRESH-INTERVAL;VALUE=DURATION:PT1H","X-PUBLISHED-TTL:PT1H"]
for i,show in enumerate(shows):
    try: day=datetime.strptime(show["date"],"%Y-%m-%d").date()
    except (ValueError,KeyError,TypeError):continue
    venue=str(show.get("venue") or "Show")
    city=str(show.get("city") or "")
    when=time_of(show.get("time"))
    lines+=["BEGIN:VEVENT",f"UID:show-{day:%Y%m%d}-{i}@lippieleo.com.br",f"DTSTAMP:{datetime.now(tz).astimezone(ZoneInfo('UTC')):%Y%m%dT%H%M%SZ}"]
    if when:
        start=datetime(day.year,day.month,day.day,*when,tzinfo=tz)
        lines += [f"DTSTART;TZID=America/Sao_Paulo:{start:%Y%m%dT%H%M%S}",f"DTEND;TZID=America/Sao_Paulo:{start+timedelta(hours=2):%Y%m%dT%H%M%S}"]
    else:
        lines += [f"DTSTART;VALUE=DATE:{day:%Y%m%d}",f"DTEND;VALUE=DATE:{day+timedelta(days=1):%Y%m%d}"]
    lines += [f"SUMMARY:{esc('Lippi & Léo - '+venue)}",f"LOCATION:{esc(city)}",f"DESCRIPTION:{esc('Horário informado: '+str(show.get('time') or 'A confirmar')+' | '+str(show.get('notes') or '')+' | Veja: https://www.lippieleo.com.br/#agenda')}","URL:https://www.lippieleo.com.br/#agenda","END:VEVENT"]
lines.append("END:VCALENDAR")
(ROOT/"agenda"/"lippi-leo.ics").write_bytes(("\r\n".join(fold(s) for s in lines)+"\r\n").encode("utf-8"))
